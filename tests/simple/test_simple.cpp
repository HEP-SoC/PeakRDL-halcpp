#include <cmath>
#include <gtest/gtest.h>
#include "mock_io.h"
#include "simple_hal.h"
#include <cstdint>
#include "test_utils.h"

inline constexpr SIMPLE_HAL<0> hal{};

using HalFields = ::testing::Types<
    FieldReference<hal.r1.f1>,
    FieldReference<hal.r1.f2>,
    FieldReference<hal.r2.f5>,
    FieldReference<hal.r2.f6>
>;

TYPED_TEST_SUITE(HalFieldTest, HalFields);

TYPED_TEST(HalFieldTest, TestRWFields) {
    auto& field = TestFixture::field();
    test_rw_field_range(field);
    test_rw_field_overflow(field);
}
