#include "simple_hal.h"

int main () {

    volatile SIMPLE_HAL<0> soc;
 
    int num = 4;
    soc.r1.f1 = num;

    [[maybe_unused]] int read_num = soc.r1.f1;
    // soc.r1 = 2;
    // soc.r1.f2 = 10;
    //
    // for(volatile int i =0; i< 10; i++){
    //     soc.r1 = i;
    // }


    return 0;
}

