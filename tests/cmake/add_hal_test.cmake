include_guard(GLOBAL)

macro(add_hal_test TEST_NAME)
    cmake_parse_arguments(ARG "" "" "SYSTEMRDL;CPP" ${ARGN})
    if(ARG_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "${CMAKE_CURRENT_FUNCTION} passed unrecognized argument " "${ARG_UNPARSED_ARGUMENTS}")
    endif()

    add_ip(${TEST_NAME}_ip)

    ip_sources(${IP} SYSTEMRDL
        ${ARG_SYSTEMRDL}
    )

    peakrdl_halcpp(${IP})

    add_executable(${TEST_NAME}
        ${ARG_CPP}
    )

    target_include_directories(${TEST_NAME} PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}
    )

    target_link_libraries(${TEST_NAME}
        ${IP}
        GTest::gtest_main
        test_utils
      )

    enable_testing()
    include(GoogleTest)
    gtest_discover_tests(${TEST_NAME})


endmacro()
