set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
cmake_minimum_required(VERSION 3.25)
project(test_simple CXX)

message("PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")

include("../cmake/deps.cmake")

add_hal_test(test_simple
    SYSTEMRDL ./simple.rdl
    CPP ./test_simple.cpp
    )

# add_hal_test(test_simple_ro
#     SYSTEMRDL ./simple_ro.rdl
#     CPP ./test_simple_ro.cpp
#     )

add_hal_test(test_fixp
    SYSTEMRDL ./fixp.rdl
    CPP ./test_fixp.cpp
    )


