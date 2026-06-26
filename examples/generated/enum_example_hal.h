// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp
#ifndef __ENUM_EXAMPLE_HAL_H_
#define __ENUM_EXAMPLE_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace enum_example_nm
{
    class system_state_e
    {
    public:
        static constexpr halcpp::Const<2, 0> IDLE{}; // The system is idle and ready for input
        static constexpr halcpp::Const<2, 1> BUSY{}; // Busy processing an input
        static constexpr halcpp::Const<2, 2> SLEEP{}; // None
        static constexpr halcpp::Const<2, 3> SHUTDOWN{}; // None
    };

    
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class R1 : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = R1<BASE, WIDTH, PARENT_TYPE>;

        static inline halcpp::FieldRW<0, 1, TYPE> f1{};

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



}


template <uint32_t BASE, typename PARENT_TYPE=void>
class ENUM_EXAMPLE_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = ENUM_EXAMPLE_HAL<BASE, PARENT_TYPE>;

    static enum_example_nm::R1<0x0, 2, TYPE> r1;
};

#endif // !__ENUM_EXAMPLE_HAL_H_
