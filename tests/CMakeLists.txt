cmake_minimum_required(VERSION 3.25)
project(halcpp_tests)

include("./cmake/deps.cmake")
add_subdirectory("./rdl_lib/")

include(CTest)
enable_testing()

add_hal_test(addrmap_rw)
add_hal_test(addrmap_ro)
add_hal_test(addrmap_wo)
add_hal_test(addrmap_mixed_access)

add_hal_test(addrmap_hier_rw)
add_hal_test(addrmap_hier_ro)
add_hal_test(addrmap_hier_wo)
add_hal_test(addrmap_hier_mixed)
add_hal_test(addrmap_hier_mixed2)

add_hal_test(addrmap_rw_reg_1d_array)
add_hal_test(addrmap_rw_reg_2d_array)
add_hal_test(addrmap_rw_reg_4d_array)
add_hal_test(addrmap_hier_rw_reg_arrays)
