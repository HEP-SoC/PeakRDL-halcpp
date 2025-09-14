include_guard(GLOBAL)

function(add_hal_test IP_LIB)
    cmake_parse_arguments(ARG "" "" "" ${ARGN})
    if(ARG_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "${CMAKE_CURRENT_FUNCTION} passed unrecognized argument " "${ARG_UNPARSED_ARGUMENTS}")
    endif()

    alias_dereference(IP_LIB ${IP_LIB})
    set(OUTDIR "${CMAKE_BINARY_DIR}/${IP_LIB}_halcpp")

    peakrdl_halcpp(${IP_LIB} GENERATE_TESTS
        OUTDIR  ${OUTDIR})

    include(ExternalProject)
    ExternalProject_Add(test_${IP_LIB}_hal
        SOURCE_DIR ${OUTDIR}/tests
        DOWNLOAD_COMMAND ""
        TEST_COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
        INSTALL_COMMAND ""
        DEPENDS ${IP_LIB}_halcpp
        BUILD_ALWAYS TRUE
        CMAKE_ARGS
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        )
endfunction()
