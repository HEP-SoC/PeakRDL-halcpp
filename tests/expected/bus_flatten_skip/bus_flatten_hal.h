// Generated with PeakRD-halcpp : https://github.com/HEP-SoC/PeakRDL-halcpp
#ifndef __BUS_FLATTEN_HAL_H_
#define __BUS_FLATTEN_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

#include "leaf_t_hal.h"
namespace bus_flatten_nm
{

    
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class TOP_CTRL : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = TOP_CTRL<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 31, TYPE> ctrl;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



}


template <uint32_t BASE, typename PARENT_TYPE=void>
class BUS_FLATTEN_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = BUS_FLATTEN_HAL<BASE, PARENT_TYPE>;

    static bus_flatten_nm::TOP_CTRL<0x0, 32, TYPE> top_ctrl;
    static LEAF_T_HAL<0x100, TYPE> leaf;
};

#endif // !__BUS_FLATTEN_HAL_H_