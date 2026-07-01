#ifndef _FIXP_FIELD_NODE_H_
#define _FIXP_FIELD_NODE_H_

#include <stdint.h>
#include <type_traits>
#include <tuple>
#include "halcpp_utils.h"

namespace halcpp
{
    template <uint32_t START_INT_BIT,
              uint32_t END_INT_BIT,
              uint32_t START_FRAC_BIT,
              uint32_t END_FRAC_BIT,
              typename PARENT_TYPE>
    class FixpFieldBase
    {
    public:
        /**
         * @brief Return the absolute address of the node.
         *
         */
        static constexpr uint32_t get_abs_addr() { return PARENT_TYPE().get_abs_addr(); }

        /**
         * @brief Return the width of the field noe.
         *
         */
        static constexpr uint32_t get_width() { return width; }
        static constexpr uint32_t get_int_width() { return width_int; }
        static constexpr uint32_t get_frac_width() { return width_frac; }

        /**
         * @brief Calculate the field mask.
         *
         * Example: START_BIT = 3, width = 4 => field_mask = 0000 0000 0111 1000
         */
        static constexpr uint32_t field_mask()
        {
            static_assert(width <= 32, "Register cannot be bigger than 32 bits");
            return (~0u) ^ (bit_mask() << START_INT_BIT);
        }

        /**
         * @brief Calculate the bit mask.
         *
         * Example: width = 4 => bit_mask = 0000 0000 0000 1111
         */
        static constexpr uint32_t bit_mask()
        {
            return (((1u << (width)) - 1));
        }



    protected:
        using parent_type = PARENT_TYPE;

        static constexpr uint32_t start_bit = START_INT_BIT;
        static constexpr uint32_t start_int_bit = START_INT_BIT;
        static constexpr uint32_t end_int_bit = END_INT_BIT;
        static constexpr uint32_t start_frac_bit = START_FRAC_BIT;
        static constexpr uint32_t end_frac_bit = END_FRAC_BIT;
        static constexpr uint32_t end_bit = END_FRAC_BIT;

        static constexpr uint32_t width = end_bit - start_bit + 1;
        static constexpr uint32_t width_int = end_int_bit - start_int_bit + 1;
        static constexpr uint32_t width_frac = end_frac_bit - start_frac_bit + 1;


        using dataType = float;
    };

    template <typename BASE_TYPE>
    class FixpFieldWrMixin : public BASE_TYPE
    {
    public:
        using parent = typename BASE_TYPE::parent_type;

        /**
         * @brief Check if the field has a set operation (write capability).
         */
        static constexpr bool has_set() { return true; };

        /**
         * @brief Set the value of the field.
         *
         * @param val The value to set.
         */
        static inline void set(typename BASE_TYPE::dataType val)
        {
            uint32_t fixp_val = float_to_fixp(val);
            if constexpr (node_has_get_v<parent>)
                parent::set((parent::get() & BASE_TYPE::field_mask()) | ((fixp_val & BASE_TYPE::bit_mask()) << BASE_TYPE::start_bit));
            else
                parent::set(fixp_val << BASE_TYPE::start_bit);
        }

        static inline uint32_t float_to_fixp(typename BASE_TYPE::dataType val){
            return val * (1<<BASE_TYPE::width_frac);
        }

        /**
         * @brief Set the value of the field using a constant.
         *
         * @tparam CONST_WIDTH The width of the constant.
         * @tparam CONST_VAL The value of the constant.
         * @param a The constant value to set.
         */
        template <uint32_t CONST_WIDTH, uint32_t CONST_VAL>
        static inline void set(const Const<CONST_WIDTH, CONST_VAL> &a)
        {
            static_assert(CONST_WIDTH == BASE_TYPE::width, "Constant is not the same width as field");
            set((typename BASE_TYPE::dataType)a.val);
        }
    };

    template <typename BASE_TYPE>
    class FixpFieldRdMixin : public BASE_TYPE
    {
    private:
        using parent = typename BASE_TYPE::parent_type;

    public:
        /**
         * @brief Check if the field has a get operation (read capability).
         */
        static constexpr bool has_get() { return true; };

        /**
         * @brief Return the value of the field.
         */
        static typename BASE_TYPE::dataType get()
        {
            // Read the full register, mask, and shift it to get the field value
            uint32_t fixp_val = (parent::get() & ~BASE_TYPE::field_mask()) >> BASE_TYPE::start_bit;

            return fixp_to_float(fixp_val);
        }

        static inline float fixp_to_float(uint32_t val){
            return (float)val / (1<<BASE_TYPE::width_frac);
        }

        /**
         * @brief Implicit conversion operator to convert the field value to another type.
         *
         * @tparam T The type to convert to.
         * @return The value of the field converted to the specified type.
         */
        template <typename T>
        inline operator const T()
        {
            return static_cast<T>(get());
        }
    };


    template <typename... FieldMixins> // TODO merge this with RegNode?
    class FixpFieldNode : public FieldMixins...
    {
    private:
        template <typename DT, typename T>
        void call_set([[maybe_unused]] const DT &val) const
        {
            if constexpr (node_has_set_v<T>)
                T::set(val);
        }

        template <typename DT, typename T, typename T1, typename... Ts>
        void call_set(const DT val) const
        {
            call_set<DT, T>(val);
            call_set<DT, T1, Ts...>(val);
        }

    public:
        template <typename Tp, typename T = void>
        typename std::enable_if<std::disjunction_v<node_has_set<FieldMixins>...>, T>::type
        operator=(Tp val)
        {
            call_set<Tp, FieldMixins...>(val);
        }

        // template <int32_t IDX>
        // static constexpr auto at()
        // {
        //     // Get the type of the first mixin from the tuple of FieldMixins types
        //     using first_mixin = typename std::tuple_element<0, std::tuple<FieldMixins...>>::type;
        //     // Define the parent type using the parent type of the first mixin
        //     using parent_type = typename first_mixin::parent;
        //
        //     // Check if the given index is within the bounds of the width of the first mixin
        //     static_assert(IDX < static_cast<int32_t>(first_mixin::width));
        //     static_assert(IDX >= -1);
        //     // Calculate the index to be used for accessing the mixin based on the given index
        //     constexpr uint32_t idx = IDX == -1 ? first_mixin::width - 1 : IDX;
        //
        //     // Calculate the number of mixins in the tuple
        //     constexpr std::size_t num_of_mixins = sizeof...(FieldMixins);
        //
        //     // Define the base type using the calculated index and parent type
        //     using base_type = FieldBase<idx, idx, parent_type>;
        //
        //     // Check if there's only one mixin
        //     if constexpr (num_of_mixins == 1)
        //     {
        //         // If the mixin has a 'get' function, return a FieldNode with a read mixin
        //         if constexpr (node_has_get_v<first_mixin>)
        //             return FieldNode<FieldRdMixin<base_type>>();
        //         // If the mixin has a 'set' function, return a FieldNode with a write mixin
        //         if constexpr (node_has_set_v<first_mixin>)
        //             return FieldNode<FieldWrMixin<base_type>>();
        //     }
        //     // If there are two mixins
        //     else if constexpr (num_of_mixins == 2)
        //     {
        //         // Return a FieldNode with both write and read mixins
        //         return FieldNode<FieldWrMixin<base_type>, FieldRdMixin<base_type>>();
        //     }
        // }
    };

    template <uint32_t START_INT_BIT, uint32_t END_INT_BIT, uint32_t START_FRAC_BIT, uint32_t END_FRAC_BIT, typename PARENT_TYPE>
    using FixpFieldRO = FixpFieldNode<FixpFieldRdMixin<FixpFieldBase<START_INT_BIT, END_INT_BIT, START_FRAC_BIT, END_FRAC_BIT, PARENT_TYPE>>>;

    /**
     * @brief Alias for FieldNode representing a write-only field.
     */
    template <uint32_t START_INT_BIT, uint32_t END_INT_BIT, uint32_t START_FRAC_BIT, uint32_t END_FRAC_BIT, typename PARENT_TYPE>
    using FixpFieldWO = FixpFieldNode<FixpFieldWrMixin<FixpFieldBase<START_INT_BIT, END_INT_BIT, START_FRAC_BIT, END_FRAC_BIT, PARENT_TYPE>>>;

    /**
     * @brief Alias for FieldNode representing a read-write field.
     */
    template <uint32_t START_INT_BIT, uint32_t END_INT_BIT, uint32_t START_FRAC_BIT, uint32_t END_FRAC_BIT, typename PARENT_TYPE>
    using FixpFieldRW = FixpFieldNode<FixpFieldWrMixin<FixpFieldBase<START_INT_BIT, END_INT_BIT, START_FRAC_BIT, END_FRAC_BIT, PARENT_TYPE>>,
                                      FixpFieldRdMixin<FixpFieldBase<START_INT_BIT, END_INT_BIT, START_FRAC_BIT, END_FRAC_BIT, PARENT_TYPE>>>;
}


#endif

