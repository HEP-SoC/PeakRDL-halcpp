// Generated with PeakRD-halcpp : https://github.com/HEP-SoC/PeakRDL-halcpp
#ifndef __ENUM_FIELD_HAL_H_
#define __ENUM_FIELD_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace enum_field_nm
{
    class mode_e
    {
    public:
        static const halcpp::Const<2, 0> DISABLED; // Module disabled
        static const halcpp::Const<2, 1> ACTIVE; // Module active
        static const halcpp::Const<2, 2> SLEEP; // Sleep mode
    };


    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class CTRL_REG : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = CTRL_REG<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 1, TYPE> mode;
        static halcpp::FieldRW<2, 2, TYPE> en;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



}


template <uint32_t BASE, typename PARENT_TYPE=void>
class ENUM_FIELD_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = ENUM_FIELD_HAL<BASE, PARENT_TYPE>;

    static enum_field_nm::CTRL_REG<0x0, 3, TYPE> ctrl_reg;
};

#endif // !__ENUM_FIELD_HAL_H_
