#include <cmath>
#include <gtest/gtest.h>
#include "mock_io.h"
#include "fixp_simple_hal.h"
#include <cstdint>
#include "test_utils.h"

inline constexpr FIXP_SIMPLE_HAL<0> hal{};

TEST(FixpTest, Basic) {
    hal.r1.f1 = 15.6123;

    std::cout << "Float value: " << (float)hal.r1.f1 << "\n";
}
