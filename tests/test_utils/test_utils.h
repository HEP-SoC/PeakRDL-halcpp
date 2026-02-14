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

template<typename FIELD_T>
void test_rw_field(uint32_t val, int32_t exp, FIELD_T &field) {
    field = val;
    EXPECT_EQ((uint32_t)field, exp);
}

template<typename FIELD_T>
void test_rw_field_range(FIELD_T &field) {
    int width = field.get_width();
    for (int i = 0; i < (1 << width); i++) {
        test_rw_field(i, i, field);
    }
}

template<typename FIELD_T>
void test_rw_field_overflow(FIELD_T &field) {
    int width = field.get_width();
    test_rw_field((1 << width), 0, field);
}
