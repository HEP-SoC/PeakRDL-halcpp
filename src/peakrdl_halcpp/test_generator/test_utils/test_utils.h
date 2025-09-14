#ifndef __TEST_UTILS_H_
#define __TEST_UTILS_H_
#include <utility>

/****************************/
/** Compile time for loop ***/
/****************************/

template <typename T, T... S, typename F>
constexpr void for_sequence(std::integer_sequence<T, S...>, F f) {
    (static_cast<void>(f(std::integral_constant<T, S>{})), ...);
}

template<auto n, typename F>
constexpr void for_sequence(F f) {
    for_sequence(std::make_integer_sequence<decltype(n), n>{}, f);
}


#endif // !__TEST_UTILS_H_
