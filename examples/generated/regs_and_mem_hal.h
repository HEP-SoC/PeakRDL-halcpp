// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp
#ifndef __REGS_AND_MEM_HAL_H_
#define __REGS_AND_MEM_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"

#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace regs_and_mem_nm
{

    
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class CSR : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = CSR<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 7, TYPE> ctrl;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };


    
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class CSR_2 : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        using TYPE = CSR_2<BASE, WIDTH, PARENT_TYPE>;

        static halcpp::FieldRW<0, 7, TYPE> ctrl;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };



    template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>
    class MEM1 : public halcpp::MemNode<BASE, SIZE, PARENT_TYPE>
    {

    };
    template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>
    class MEM2_T : public halcpp::MemNode<BASE, SIZE, PARENT_TYPE>
    {

    };
}


template <uint32_t BASE, typename PARENT_TYPE=void>
class REGS_AND_MEM_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    using TYPE = REGS_AND_MEM_HAL<BASE, PARENT_TYPE>;

    static regs_and_mem_nm::CSR<0x0, 8, TYPE> csr;
    static regs_and_mem_nm::CSR_2<0x4, 8, TYPE> csr_2;
    static regs_and_mem_nm::MEM1<0x1000, 256, TYPE> mem1;
    static regs_and_mem_nm::MEM2_T<0x2000, 256, TYPE> mem2;
};

#endif // !__REGS_AND_MEM_HAL_H_
