#ifndef __REG_TEST_UTILS_H_
#define __REG_TEST_UTILS_H_

#include <cassert>
#include <cstdint>
#include <iostream>

/**********************************/
/****** Reg base address test *****/
/**********************************/

void assert_reg_base_address(uint32_t expected_base_address,
                             uint32_t actual_base_address,
                             const char *reg_path){
    if(expected_base_address != actual_base_address){
        std::cerr << "Reg base address test error for " << reg_path;
        std::cerr << "\n\tExpected base address: 0x" << std::hex << expected_base_address;
        std::cerr << "\n\tActual base address:   0x" << std::hex << actual_base_address << std::endl;
        assert(expected_base_address == actual_base_address);
    }
}

template<typename REG_T>
void test_reg_base_address(REG_T &reg, uint32_t base_address, const char* reg_path){
    assert_reg_base_address(base_address, reg.get_abs_addr(), reg_path);
}

/****************************/
/**** Generic Reg test ******/
/****************************/

template<typename REG_T>
void test_generic_reg(const REG_T &reg,
                      size_t base_address,
                      const char* reg_path){

    test_reg_base_address(reg, base_address, reg_path);
}

/**********************************/
/*********** RW reg test **********/
/**********************************/

void assert_rw_reg(uint32_t expected_data,
                   uint32_t actual_data,
                   const char *reg_path){
    if(expected_data != actual_data){
        std::cerr << "RW Reg test error for " << reg_path;
        std::cerr << "\n\tExpected data: 0x" << std::hex << expected_data;
        std::cerr << "\n\tActual data:   0x" << std::hex << actual_data << std::endl;
        assert(expected_data == actual_data);
    }
}

template<typename REG_T>
void test_rw_reg(REG_T reg, const char* reg_path){
    reg = reg.get_abs_addr();
    assert_rw_reg(reg.get_abs_addr(), reg.get(), reg_path);
}

/**********************************/
/*********** RO reg test **********/
/**********************************/

template<typename REG_T>
void test_ro_reg(const REG_T &reg){
    [[maybe_unused]] uint32_t val = reg;
}

/**********************************/
/*********** WO reg test **********/
/**********************************/

template<typename REG_T>
void test_wo_reg(REG_T &reg){
    reg = 1;
}

#endif // !__REG_TEST_UTILS_H_


