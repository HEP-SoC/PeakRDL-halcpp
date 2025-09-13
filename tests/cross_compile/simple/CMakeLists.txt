set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
cmake_minimum_required(VERSION 3.25)
project(test_cross_compile CXX)

include("../../cmake/deps.cmake")


add_ip(${PROJECT_NAME}_ip)

ip_sources(${IP} SYSTEMRDL
    ../../simple/simple.rdl
)

peakrdl_halcpp(${IP})

add_executable(${PROJECT_NAME}
    ./main.cpp
)

target_include_directories(${PROJECT_NAME} PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(${PROJECT_NAME}
    ${IP}
  )

target_compile_options(${PROJECT_NAME} PUBLIC
    -Os
    -fno-delete-null-pointer-checks
    -Wall -Wextra -Wpedantic -Werror
)

firmware_size(${PROJECT_NAME})
firmware_disasemble(${PROJECT_NAME})



