#ifndef _REG_NODE_H_
#define _REG_NODE_H_

#include <stdint.h>
#include <type_traits>
#include "halcpp_utils.h"

namespace halcpp
{

    /**
     * @brief A base class template representing a register.
     *
     * @tparam BASE The relative base address of the register.
     * @tparam WIDTH The width (in bits) of the register.
     * @tparam PARENT_TYPE The parent type of the register.
     */
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class RegBase
    {
    public:
        /**
         * @brief Get the absolute address of the register.
         */
        static constexpr uint32_t get_abs_addr() { return PARENT_TYPE().get_abs_addr() + BASE; }

    protected:
        static constexpr uint32_t width = WIDTH;
        static constexpr uint32_t rel_base = BASE;
        using parent_type = PARENT_TYPE;
        using dataType = typename std::conditional<WIDTH <= 8, uint8_t,
                                                   typename std::conditional<WIDTH <= 16, uint16_t,
                                                                             uint32_t>::type>::type;
    };

    /**
     * @brief A mixin class template for register write operations.
     *
     * @tparam BASE_TYPE The base type of the register.
     */
    template <typename BASE_TYPE>
    class RegWrMixin : public BASE_TYPE
    {
    public:
        using parent = typename BASE_TYPE::parent_type;

        /**
         * @brief Check if the register has a set operation (write capability).
         */
        static constexpr bool has_set() { return true; };

        /**
         * @brief Set the value of the register.
         *
         * @param val The value to be set.
         */
        static inline void set(typename BASE_TYPE::dataType val)
        {
            parent::set(BASE_TYPE::rel_base, val);
        }

        /**
         * @brief Set the value of the register using a constant.
         *
         * @param a The constant value to be set.
         */
        template <uint32_t CONST_WIDTH, uint32_t CONST_VAL>
        static inline void set(const Const<CONST_WIDTH, CONST_VAL> &a)
        {
            static_assert(BASE_TYPE::width == CONST_WIDTH, "You need to provide all the bits for concatenation.");
            parent::set(BASE_TYPE::rel_base, a.val);
        }
    };

    /**
     * @brief A mixin class template for register read operations.
     *
     * @tparam BASE_TYPE The base type of the register.
     */
    template <typename BASE_TYPE>
    class RegRdMixin : public BASE_TYPE
    {
    private:
        using parent = typename BASE_TYPE::parent_type;

    public:
        /**
         * @brief Check if the field has a get operation (read capability).
         */
        static constexpr bool has_get() { return true; };

        /**
         * @brief Get the value of the register.
         *
         * @return typename BASE_TYPE::dataType The value of the register.
         */
        static typename BASE_TYPE::dataType get()
        {
            return parent::get(BASE_TYPE::rel_base);
        }

        /**
         * @brief Convert the value of the register to a specified type.
         *
         * @tparam T The type to convert the value to.
         * @return operator const T() The value of the register converted to type T.
         */
        template <typename T>
        inline operator T() const {
            static_assert(std::is_integral<T>::value, "T must be an integral type.");
            static_assert(
                sizeof(T) >= (BASE_TYPE::width / 8),
                "T must be smaller than or equal to Field width, otherwise data will be lost");

            return static_cast<T>(get());
        }
    };

    /**
     * @brief A class template representing a register with a set of mixins.
     *
     * @tparam RegMixins The mixins associated with the register.
     */
    template <typename... RegMixins>
    class RegNode : public RegMixins...
    {
    private:
        /**
         * @brief Helper function for setting the value of the register.
         *
         * @tparam DT The data type of the value to be set.
         * @tparam T The type of the mixin.
         * @param val The value to be set.
         */
        template <typename DT, typename T>
        void call_set([[maybe_unused]] const DT &val) const
        {
            if constexpr (node_has_set_v<T>)
                T::set(val);
        }
        /**
         * @brief Recursive helper function for setting the value of the register.
         *
         * This function template is used internally to call the call_set function recursively
         * for each register mixin in the parameter pack.
         *
         * @tparam DT The data type of the value to be set.
         * @tparam T The type of the mixin.
         * @tparam T1 The type of the next mixin.
         * @tparam Ts The types of the remaining mixins.
         * @param val The value to be set.
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
         * instance of the RegNode class, and the assignment is propagated to each
         * register mixin contained within the RegNode. The operator is conditionally
         * enabled based on whether any of the register mixins have a set function,
         * ensuring that the operator is only available when it makes sense based on
         * the composition of the RegNode.
         *
         * @tparam Tp The type of the value to be set.
         * @tparam T The type of the mixin.
         * @return typename std::enable_if<std::disjunction_v<node_has_set<RegMixins>...>, T>::type The result type.
         * @param val The value to be set.
         */
        template <typename Tp, typename T = void>
        typename std::enable_if<std::disjunction_v<node_has_set<RegMixins>...>, T>::type
        operator=(Tp val)
        {
            call_set<Tp, RegMixins...>(val);
        }
    };

    /**
     * @brief Alias for RegNode representing a read-only register.
     */
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    using RegRO = RegNode<RegRdMixin<RegBase<BASE, WIDTH, PARENT_TYPE>>>;

    /**
     * @brief Alias for RegNode representing a write-only register.
     */
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    using RegWO = RegNode<RegWrMixin<RegBase<BASE, WIDTH, PARENT_TYPE>>>;

    /**
     * @brief Alias for RegNode representing a read-write register.
     */
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    using RegRW = RegNode<RegWrMixin<RegBase<BASE, WIDTH, PARENT_TYPE>>,
                          RegRdMixin<RegBase<BASE, WIDTH, PARENT_TYPE>>>;

}

#endif // !_REG_NODE_H_
