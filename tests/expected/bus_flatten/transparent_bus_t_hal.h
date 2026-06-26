// Generated with PeakRD-halcpp : https://github.com/HEP-SoC/PeakRDL-halcpp
#ifndef __TRANSPARENT_BUS_T_HAL_H_
#define __TRANSPARENT_BUS_T_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

#include "leaf_t_hal.h"


template <uint32_t BASE, typename PARENT_TYPE>
class TRANSPARENT_BUS_T_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = TRANSPARENT_BUS_T_HAL<BASE, PARENT_TYPE>;

    static LEAF_T_HAL<0x0, TYPE> leaf;
};

#endif // !__TRANSPARENT_BUS_T_HAL_H_