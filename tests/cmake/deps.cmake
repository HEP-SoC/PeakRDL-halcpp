set(FETCHCONTENT_BASE_DIR "${CMAKE_CURRENT_LIST_DIR}/_deps")
include(FetchContent)
FetchContent_Declare(SoCMake
    GIT_REPOSITORY "https://github.com/HEP-SoC/SoCMake.git"
    GIT_TAG 40feb77)
FetchContent_MakeAvailable(SoCMake)

if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
    FetchContent_Declare(googletest
      URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
    )
    FetchContent_MakeAvailable(googletest)
    add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../test_utils/" "test_utils")
    include("${CMAKE_CURRENT_LIST_DIR}/add_hal_test.cmake")
endif()

include("${CMAKE_CURRENT_LIST_DIR}/fw_utils.cmake")

