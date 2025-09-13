cmake_minimum_required(VERSION 3.25)
project(soc NONE)

include("../cmake/deps.cmake")

add_ip(soc)
ip_sources(${IP} SYSTEMRDL
    ./soc.rdl
)

add_subdirectory(ips/)

ip_link(${IP}
    gpio
    i2c
)

peakrdl_halcpp(${IP} GENERATE_TESTS)
