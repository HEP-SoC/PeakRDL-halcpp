// Generated with PeakRD-halcpp : https://github.com/HEP-SoC/PeakRDL-halcpp
#ifndef __ARRAY_REG_HAL_H_
#define __ARRAY_REG_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace array_reg_nm
{


    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class CHAN_T : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = CHAN_T<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 31, TYPE> data;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



}


template <uint32_t BASE, typename PARENT_TYPE=void>
class ARRAY_REG_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = ARRAY_REG_HAL<BASE, PARENT_TYPE>;

    static halcpp::RegArrayNode<array_reg_nm::CHAN_T, 0x0, 32, 4, TYPE , 4> channel;
};

#endif // !__ARRAY_REG_HAL_H_
