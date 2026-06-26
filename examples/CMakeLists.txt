cmake_minimum_required(VERSION 3.31)
project(example_app CXX)

add_executable(app main.cpp)

target_compile_options(app PRIVATE -O0)
