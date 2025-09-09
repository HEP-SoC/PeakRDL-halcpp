#include "fixp_simple_hal.h"

int main () {

    FIXP_SIMPLE_HAL<0> soc;
 
    soc.r1.f1 = 4.8;

    float read_num = soc.r1.f1;

    return 0;
}

