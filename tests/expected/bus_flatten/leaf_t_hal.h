// Generated with PeakRD-halcpp : https://github.com/HEP-SoC/PeakRDL-halcpp
#ifndef __LEAF_T_HAL_H_
#define __LEAF_T_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace leaf_t_nm
{

    
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class DATA_REG : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = DATA_REG<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 31, TYPE> data;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



}


template <uint32_t BASE, typename PARENT_TYPE>
class LEAF_T_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = LEAF_T_HAL<BASE, PARENT_TYPE>;

    static leaf_t_nm::DATA_REG<0x0, 32, TYPE> data_reg;
};

#endif // !__LEAF_T_HAL_H_