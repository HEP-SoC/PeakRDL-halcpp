#ifndef _FIELD_NODE_H_
#define _FIELD_NODE_H_

#include <stdint.h>
#include <type_traits>
#include <tuple>
#include "halcpp_utils.h"

namespace halcpp
{

    /**
     * @brief Template class representing a field within a register.
     *
     * This class template represents a field within a register. It defines the base
     * properties and operations for accessing and manipulating the field.
     *
     * @tparam START_BIT The starting bit index of the field within the register.
     * @tparam END_BIT The ending bit index of the field within the register.
     * @tparam PARENT_TYPE The type of the parent register containing the field.
     */
    template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
    class FieldBase
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

        /**
         *
         * @brief Return the index of first bit of the field in the parent register
         */
        static constexpr uint32_t get_start_bit() { return start_bit; }

        /**
         *
         * @brief Return the index of last bit of the field in the parent register
         */
        static constexpr uint32_t get_end_bit() { return end_bit; }

        /**
         * @brief Calculate the field mask.
         *
         * Example: START_BIT = 3, width = 4 => field_mask = 0000 0000 0111 1000
         */
        static constexpr uint32_t field_mask()
        {
            static_assert(width <= 32, "Register cannot be bigger than 32 bits");
            return (~0u) ^ (bit_mask() << START_BIT);
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

        static constexpr uint32_t start_bit = START_BIT;
        static constexpr uint32_t end_bit = END_BIT;
        static constexpr uint32_t width = END_BIT - START_BIT + 1;

        using dataType = typename std::conditional<width <= 8, uint8_t,
                                                   typename std::conditional<width <= 16, uint16_t, uint32_t>::type>::type;
    };

    /**
     * @brief Mixin class for fields with write capability.
     *
     * This mixin class provides write capability to fields within registers.
     *
     * @tparam BASE_TYPE The base field type.
     */
    template <typename BASE_TYPE>
    class FieldWrMixin : public BASE_TYPE
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
            if constexpr (node_has_get_v<parent>)
                parent::set((parent::get() & BASE_TYPE::field_mask()) | ((val & BASE_TYPE::bit_mask()) << BASE_TYPE::start_bit));
            else
                parent::set(val << BASE_TYPE::start_bit);
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

    /**
     * @brief Mixin class for fields with read capability.
     *
     * This mixin class provides read capability to fields within registers.
     *
     * @tparam BASE_TYPE The base field type.
     */
    template <typename BASE_TYPE>
    class FieldRdMixin : public BASE_TYPE
    {
    public:
        using parent = typename BASE_TYPE::parent_type;
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
            return (parent::get() & ~BASE_TYPE::field_mask()) >> BASE_TYPE::start_bit;
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
            static_assert(std::is_integral<T>::value, "T must be an integral type.");
            static_assert(
                sizeof(T) >= (float)(BASE_TYPE::end_bit - BASE_TYPE::start_bit + 1) / 8,
                "T must be smaller than or equal to Field width, otherwise data will be lost");
            return static_cast<T>(get());
        }
    };

    /**
     * @brief Template class representing a collection of field mixins.
     *
     * @tparam FieldMixins The field mixins to combine.
     */
    template <typename... FieldMixins> // TODO merge this with RegNode?
    class FieldNode : public FieldMixins...
    {
    private:
        /**
         * @brief Helper function to call the set function of field mixins.
         *
         * This function template is used internally to call the set function of field mixins.
         *
         * @tparam DT The data type of the value to set.
         * @tparam T The type of the field mixin.
         * @param val The value to set.
         */
        template <typename DT, typename T>
        void call_set([[maybe_unused]] const DT &val) const
        {
            if constexpr (node_has_set_v<T>)
                T::set(val);
        }

        /**
         * @brief Recursive helper function to call_set for multiple field mixins.
         *
         * This function template is used internally to call the call_set function recursively
         * for each field mixin in the parameter pack.
         *
         * @tparam DT The data type of the value to set.
         * @tparam T The type of the first field mixin.
         * @tparam T1 The type of the second field mixin.
         * @tparam Ts The types of the remaining field mixins.
         * @param val The value to set.
         */
        template <typename DT, typename T, typename T1, typename... Ts>
        void call_set(const DT val) const
        {
            call_set<DT, T>(val);
            call_set<DT, T1, Ts...>(val);
        }

    public:
        /**
         * @brief Overloaded assignment operator for setting values.
         *
         * This assignment operator overloading allows to assign a value (val) to an
         * instance of the FieldNode class, and the assignment is propagated to each
         * field mixin contained within the FieldNode. The operator is conditionally
         * enabled based on whether any of the field mixins have a set function,
         * ensuring that the operator is only available when it makes sense based on
         * the composition of the FieldNode.
         *
         * @tparam Tp The type of the value to set.
         * @tparam T The enable_if condition type.
         * @param val The value to set.
         * @return T (if enabled) indicating success.
         */
        template <typename Tp, typename T = void>
        typename std::enable_if<std::disjunction_v<node_has_set<FieldMixins>...>, T>::type
        operator=(Tp val)
        {
            call_set<Tp, FieldMixins...>(val);
        }

        /**
         * @brief Accessor function to retrieve a field mixin at a specific index.
         *
         * This static member function template provides a way to access a specific field mixin
         * within the FieldNode class template based on the index.
         *
         * @tparam IDX The index of the field mixin to retrieve.
         * @return An instance of the FieldNode containing the specified field mixin.
         */
        template <int32_t IDX>
        static constexpr auto at()
        {
            // Get the type of the first mixin from the tuple of FieldMixins types
            using first_mixin = typename std::tuple_element<0, std::tuple<FieldMixins...>>::type;
            // Define the parent type using the parent type of the first mixin
            using parent_type = typename first_mixin::parent;

            // Check if the given index is within the bounds of the width of the first mixin
            static_assert(IDX < static_cast<int32_t>(first_mixin::width));
            static_assert(IDX >= -1);
            // Calculate the index to be used for accessing the mixin based on the given index
            constexpr uint32_t idx = IDX == -1 ? first_mixin::width - 1 : IDX;
            constexpr uint32_t start_bit = first_mixin::start_bit;

            // Calculate the number of mixins in the tuple
            constexpr std::size_t num_of_mixins = sizeof...(FieldMixins);

            // Define the base type using the calculated index and parent type
            using base_type = FieldBase<start_bit + idx, start_bit + idx, parent_type>;

            // Check if there's only one mixin
            if constexpr (num_of_mixins == 1)
            {
                // If the mixin has a 'get' function, return a FieldNode with a read mixin
                if constexpr (node_has_get_v<first_mixin>)
                    return FieldNode<FieldRdMixin<base_type>>();
                // If the mixin has a 'set' function, return a FieldNode with a write mixin
                if constexpr (node_has_set_v<first_mixin>)
                    return FieldNode<FieldWrMixin<base_type>>();
            }
            // If there are two mixins
            else if constexpr (num_of_mixins == 2)
            {
                // Return a FieldNode with both write and read mixins
                return FieldNode<FieldWrMixin<base_type>, FieldRdMixin<base_type>>();
            }
        }
    };

    /**
     * @brief Alias for FieldNode representing a read-only field.
     */
    template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
    using FieldRO = FieldNode<FieldRdMixin<FieldBase<START_BIT, END_BIT, PARENT_TYPE>>>;

    /**
     * @brief Alias for FieldNode representing a write-only field.
     */
    template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
    using FieldWO = FieldNode<FieldWrMixin<FieldBase<START_BIT, END_BIT, PARENT_TYPE>>>;

    /**
     * @brief Alias for FieldNode representing a read-write field.
     */
    template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
    using FieldRW = FieldNode<FieldWrMixin<FieldBase<START_BIT, END_BIT, PARENT_TYPE>>,
                              FieldRdMixin<FieldBase<START_BIT, END_BIT, PARENT_TYPE>>>;

}

#endif
