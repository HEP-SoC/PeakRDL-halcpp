#ifndef _HALCPP_UTILS_H_
#define _HALCPP_UTILS_H_

#include <type_traits>
#include <cstdint>

namespace halcpp
{

    /**
     * @brief Template class representing a constant value with a specified width.
     *
     * This class template allows defining a constant value with a specified width.
     * The width is provided as a template parameter, and the value itself is provided
     * as a template argument.
     *
     * @tparam WIDTH The width of the constant value in bits.
     * @tparam VAL The value of the constant.
     */
    template <uint32_t WIDTH, uint32_t VAL>
    class Const
    {
    public:
        /** Type alias for the data type of the constant value. */
        using dataType = typename std::conditional<(WIDTH) <= 8, uint8_t,
                                                   typename std::conditional<(WIDTH) <= 16, uint16_t,
                                                                             uint32_t>::type>::type;

        static constexpr dataType val = VAL;
        static constexpr uint32_t width = WIDTH;

        /**
         * @brief Concatenation operator ',' to concatenate constants.
         *
         * This operator concatenates two constant values and returns a new
         * constant with the combined width and value.
         *
         * @tparam OTHER_WIDTH The width of the other constant to concatenate.
         * @tparam OTHER_VAL The value of the other constant to concatenate.
         * @param a The other constant to concatenate.
         * @return A new constant with the concatenated width and value.
         */
        template <uint32_t OTHER_WIDTH, uint32_t OTHER_VAL>
        inline const Const<OTHER_WIDTH + WIDTH, (VAL << OTHER_WIDTH) | OTHER_VAL> operator,([[maybe_unused]] const Const<OTHER_WIDTH, OTHER_VAL> &a) const
        {
            return Const<OTHER_WIDTH + WIDTH, (VAL << OTHER_WIDTH) | OTHER_VAL>();
        }
    };

    /**
     * @brief Type trait to check if a type has a `set` member function.
     *
     * This type trait checks if a given type has a member function named `has_set`.
     * It is used to determine if a type supports the `set` operation.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE, class = void>
    struct node_has_set : std::false_type
    {
    };

    /**
     * @brief Specialization of `node_has_set` for types with a `set` member function.
     *
     * This specialization enables `node_has_set` for types that have a member function
     * named `has_set`. It derives from std::integral_constant with a boolean value
     * indicating the presence of the `has_set` function.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    struct node_has_set<TYPE,
                        std::enable_if_t<std::is_invocable_r<bool, decltype(TYPE::has_set)>::value>>
        : std::integral_constant<bool, TYPE::has_set()>
    {
    };

    /**
     * @brief Convenience variable template to check if a type has a `set` member function.
     *
     * This variable template provides a boolean value indicating whether a given type
     * has a member function named `has_set`. It uses the `node_has_set` type trait.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    constexpr bool node_has_set_v = node_has_set<TYPE>::value;

    /**
     * @brief Type trait to check if a type has a `get` member function.
     *
     * This type trait checks if a given type has a member function named `has_get`.
     * It is used to determine if a type supports the `get` operation.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE, class = void>
    struct node_has_get : std::false_type
    {
    };

    /**
     * @brief Specialization of `node_has_get` for types with a `get` member function.
     *
     * This specialization enables `node_has_get` for types that have a member function
     * named `has_get`. It derives from std::integral_constant with a boolean value
     * indicating the presence of the `has_get` function.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    struct node_has_get<TYPE,
                        std::enable_if_t<std::is_invocable_r<bool, decltype(TYPE::has_get)>::value>>
        : std::integral_constant<bool, TYPE::has_get()>
    {
    };

    /**
     * @brief Convenience variable template to check if a type has a `get` member function.
     *
     * This variable template provides a boolean value indicating whether a given type
     * has a member function named `has_get`. It uses the `node_has_get` type trait.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    constexpr bool node_has_get_v = node_has_get<TYPE>::value;

    /**
     * @brief Type trait to check if a type has an `onwrite_hazard_mask` static member.
     *
     * Used to detect (at compile time) whether a register type carries the write-side-effect
     * masking constants emitted by the code generator, without requiring every possible
     * parent type to define them.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE, class = void>
    struct node_has_onwrite_hazard : std::false_type
    {
    };

    /**
     * @brief Specialization of `node_has_onwrite_hazard` for types that define
     * `onwrite_hazard_mask`.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    struct node_has_onwrite_hazard<TYPE, std::void_t<decltype(TYPE::onwrite_hazard_mask)>> : std::true_type
    {
    };

    /**
     * @brief Convenience variable template for `node_has_onwrite_hazard`.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    constexpr bool node_has_onwrite_hazard_v = node_has_onwrite_hazard<TYPE>::value;

    /**
     * @brief Type trait exposing a register's `has_onread_hazard` flag, defaulting to false
     * for types that don't define it.
     *
     * A register has an onread hazard when one of its fields has a destructive-read side
     * effect (onread=rclr/rset/ruser). Reading such a register - even incidentally, as part
     * of a read-modify-write to set a sibling field - silently disturbs it.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE, class = void>
    struct node_onread_hazard : std::false_type
    {
    };

    /**
     * @brief Specialization of `node_onread_hazard` for types that define `has_onread_hazard`.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    struct node_onread_hazard<TYPE, std::void_t<decltype(TYPE::has_onread_hazard)>>
        : std::integral_constant<bool, TYPE::has_onread_hazard>
    {
    };

    /**
     * @brief Convenience variable template for `node_onread_hazard`.
     *
     * @tparam TYPE The type to check.
     */
    template <class TYPE>
    constexpr bool node_onread_hazard_v = node_onread_hazard<TYPE>::value;

}

#endif // !_HALCPP_UTILS_H_
