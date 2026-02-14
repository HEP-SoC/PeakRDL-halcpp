#ifndef _ARCH_IO_H_
#define _ARCH_IO_H_

#include <array>
#include <cstdint>
#include <iostream>
#include <ostream>



class MockMemIO
{
public:
    static inline std::array<uint32_t, 4096> mem;

    static inline uint32_t read32(uint32_t addr) {
        // std::cout << "Read32 at addr 0x" << std::hex << addr << " Read data: 0x" << std::hex << MockMemIO::mem[addr] << std::endl;
        return MockMemIO::mem[addr];
    }

    static inline void write32(uint32_t addr, uint32_t val) {
        // std::cout << "Write32 at addr 0x" << std::hex << addr << " Write data: 0x" << std::hex << val << std::endl;
        MockMemIO::mem[addr] = val;
    }
};

class ArchIoNode : public MockMemIO
{
public:
};

#endif // !_ARCH_IO_H_


