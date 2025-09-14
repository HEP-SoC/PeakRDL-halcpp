set(FETCHCONTENT_BASE_DIR "${CMAKE_CURRENT_LIST_DIR}/_deps")
include(FetchContent)
FetchContent_Declare(SoCMake
    GIT_REPOSITORY "https://github.com/HEP-SoC/SoCMake.git"
    GIT_TAG 2b88773d2f21)
FetchContent_MakeAvailable(SoCMake)

include("${CMAKE_CURRENT_LIST_DIR}/add_hal_test.cmake")
