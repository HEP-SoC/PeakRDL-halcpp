#include <cstdint>
#include <iostream>
#include <cassert>

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

/****************************/
/***** Field Width test *****/
/****************************/

void assert_field_width(uint32_t expected_width,
                        uint32_t actual_width,
                        const char *field_path){
    if(expected_width != actual_width){
        std::cerr << "Field width test error for " << field_path;
        std::cerr << "\n\tExpected width: " << std::dec << expected_width;
        std::cerr << "\n\tActual width:   " << std::dec << actual_width << std::endl;
        assert(expected_width == actual_width);
    }
}

template<typename FIELD_T>
void test_field_width(FIELD_T &field, uint32_t width, const char* field_path){
    assert_field_width(width, field.get_width(), field_path);
}

/**********************************/
/***** Field Base address test ****/
/**********************************/

void assert_field_base_address(uint32_t expected_base_address,
                               uint32_t actual_base_address,
                               const char *field_path){
    if(expected_base_address != actual_base_address){
        std::cerr << "Field width test error for " << field_path;
        std::cerr << "\n\tExpected width: " << std::dec << expected_base_address;
        std::cerr << "\n\tActual width:   " << std::dec << actual_base_address << std::endl;
        assert(expected_base_address == actual_base_address);
    }
}

template<typename FIELD_T>
void test_field_base_address(FIELD_T &field, uint32_t base_address, const char* field_path){
    assert_field_width(base_address, field.get_abs_addr(), field_path);
}

/**********************************/
/*** Field start/end bit test *****/
/**********************************/

void assert_field_start_end_bit(uint32_t expected_start_bit,
                               uint32_t actual_start_bit,
                               uint32_t expected_end_bit,
                               uint32_t actual_end_bit,
                               const char *field_path){
    if((expected_start_bit != actual_start_bit) or
       (expected_end_bit   != actual_end_bit)){
        std::cerr << "Field start/end test error for " << field_path;
        std::cerr << "\n\tExpected start bit index: " << std::dec << expected_start_bit;
        std::cerr << "\n\tActual start bit index:   " << std::dec << actual_start_bit;
        std::cerr << "\n\tExpected end bit index: " << std::dec << expected_end_bit;
        std::cerr << "\n\tActual end bit index:   " << std::dec << actual_end_bit << std::endl;
        assert(expected_start_bit == actual_start_bit);
        assert(expected_end_bit == actual_end_bit);
    }
}

template<typename FIELD_T>
void test_field_start_end_bit(FIELD_T &field, uint32_t start_bit, uint32_t end_bit, const char* field_path){
    uint32_t read_start_bit = field.get_start_bit();
    uint32_t read_end_bit = field.get_end_bit();
    assert_field_start_end_bit(start_bit, read_start_bit, end_bit, read_end_bit, field_path);
}

/****************************/
/****** RW Field test *******/
/****************************/

void assert_rw(uint32_t exp, uint32_t rec, const char* field_path){
    if(exp != rec){
        std::cerr << "Field RW test error for " << field_path;
        std::cerr << "\n\tWrote: 0x" << std::hex << exp;
        std::cerr << "\n\tRead:  0x" << std::hex << rec << "\n";
        assert(exp == rec);
    }
}

template<typename FIELD_T>
void test_rw_field(uint32_t val, uint32_t exp, FIELD_T &field, const char* field_path){
    field = val;

    uint32_t result = field;
    assert_rw(exp, result, field_path);
}

template<typename FIELD_T>
void test_rw_field_marching_ones(FIELD_T &field, const char* field_path){
    uint32_t width = field.get_width();
    test_rw_field(0, 0, field, field_path);
    for (int i = 0; i < width; i++) {
        uint32_t write_val = 1 << i;
        test_rw_field(write_val, write_val, field, field_path);
    }
}

template<typename FIELD_T>
void test_rw_field_overflow(FIELD_T &field, const char* field_path){
    uint32_t width = field.get_width();
    test_rw_field((1 << width), 0, field, field_path);
}

void assert_rw_at(uint32_t bit_idx, uint32_t exp_bit_val, uint32_t exp_field_val, uint32_t actual_field_val, const char* field_path) {
    uint32_t mask = 1u << bit_idx;
    uint32_t rec_bit = (actual_field_val & mask) ? 1u : 0u;

    if ((exp_bit_val != rec_bit) or 
        (exp_field_val != actual_field_val)) {
        std::cerr << "Field RW at() accessor test error for " << field_path;
        std::cerr << "\n\tBit index: " << std::dec << bit_idx;
        std::cerr << "\n\tExpected:  " << exp_bit_val;
        std::cerr << "\n\tBut read:  " << rec_bit;
        std::cerr << "\n\tExpected field value:  0x" << std::hex << exp_field_val;
        std::cerr << "\n\tActual field value:    0x" << std::hex << actual_field_val << "\n";
        assert(exp_bit_val == rec_bit);
        assert(exp_field_val == actual_field_val);
    }
}

template<typename FIELD_T, uint32_t WIDTH>
void test_rw_field_at_accessor(FIELD_T &field, const char* field_path){
    test_rw_field(0, 0, field, field_path);
    uint32_t exp_val = 0;
    for_sequence<WIDTH>([&field, &exp_val, &field_path](auto i) {
        field.template at<i>() = 1;
        exp_val = exp_val | (1 << i);
        assert_rw_at(i, 1, exp_val, field.get(), field_path);
    });

    // Set the last bit of the field to 0, (currently all bits are 1)
    field.template at<-1>() = 0;
    exp_val = (1 << (WIDTH-1)) - 1;
    assert_rw_at(WIDTH-1, 0, exp_val, field.get(), field_path);
}

template<typename FIELD_T, uint32_t WIDTH>
void test_rw_field(FIELD_T &field,
                   const char* field_path){
    test_rw_field_marching_ones(field, field_path);
    test_rw_field_overflow(field, field_path);
    test_rw_field_at_accessor<FIELD_T, WIDTH>(field, field_path);
}


/****************************/
/****** RO Field test *******/
/****************************/

template<typename FIELD_T, uint32_t WIDTH>
void test_ro_field_at_accessor(FIELD_T &field, const char* field_path){
    for_sequence<WIDTH>([&field, &field_path](auto i) {
        volatile uint32_t val = field.template at<i>();
    });
    volatile uint32_t val = field.template at<-1>().get();
}

template<typename FIELD_T, uint32_t WIDTH>
void test_ro_field(FIELD_T &field,
                   const char* field_path){
    volatile uint32_t read = field;
    test_ro_field_at_accessor<FIELD_T, WIDTH>(field, field_path);
}

/****************************/
/****** WO Field test *******/
/****************************/

template<typename FIELD_T, uint32_t WIDTH>
void test_wo_field_at_accessor(FIELD_T &field, const char* field_path){
    for_sequence<WIDTH>([&field, &field_path](auto i) {
        field.template at<i>() = 1;
    });
    field.template at<-1>() = 0;
}

template<typename FIELD_T, uint32_t WIDTH>
void test_wo_field(FIELD_T &field,
                   const char* field_path){
    field = 1;
    test_wo_field_at_accessor<FIELD_T, WIDTH>(field, field_path);
}

/****************************/
/**** Generic Field test ****/
/****************************/

template<typename FIELD_T>
void test_generic_field(FIELD_T &field,
                        uint32_t width,
                        size_t base_address,
                        uint32_t start_bit,
                        uint32_t end_bit,
                        const char* field_path){

    test_field_width(field, width, field_path);
    test_field_base_address(field, base_address, field_path);
    test_field_start_end_bit(field, start_bit, end_bit, field_path);

}
