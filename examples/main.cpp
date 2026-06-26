#include <iostream>

#include "mock_io.h"
#include "generated/enum_example_hal.h"

int main() {

    ENUM_EXAMPLE_HAL<0> hal;

    hal.r1.f1 = enum_example_nm::system_state_e::SHUTDOWN; 
    std::cout << "hal.DATA.RDATA = " << (uint32_t) hal.r1.get() << "\n";

    return 0;
}

