#include <gtest/gtest.h>

template <auto &Field>
struct FieldReference {
    static auto& get() { return Field; }
};

template <typename FieldT>
class HalFieldTest : public ::testing::Test {
protected:
    static auto& field() { return FieldT::get(); }
};

/***********************/
/*** WO field tests ****/
/***********************/

template<typename FIELD_T>
void test_w_field(uint32_t val, FIELD_T &field) {
    field = val;
}

template<typename FIELD_T>
void test_w_field_range(FIELD_T &field) {
    int width = field.get_width();
    for (int i = 0; i < (1 << width); i++) {
        test_w_field(i, i, field);
    }
}

/***********************/
/*** RO field tests ****/
/***********************/

template<typename FIELD_T>
void test_r_field(int32_t exp, FIELD_T &field) {
    EXPECT_EQ((uint32_t)field, exp);
}

/***********************/
/*** RW field tests ****/
/***********************/

template<typename FIELD_T>
void test_rw_field(uint32_t val, int32_t exp, FIELD_T &field) {
    field = val;
    EXPECT_EQ((uint32_t)field, exp);
}

template<typename FIELD_T>
void test_rw_field_marching_ones(FIELD_T &field) {
    test_rw_field(0, 0, field);
    int width = field.get_width();
    for (int i = 0; i < (1 << width); i++) {
        uint32_t write_val = 1 << i;
        test_rw_field(write_val, write_val, field);
    }
}

template<typename FIELD_T>
void test_rw_field_overflow(FIELD_T &field) {
    int width = field.get_width();
    test_rw_field((1 << width), 0, field);
}
