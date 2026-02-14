
function(firmware_size EXE)
    message("EXECUTING ${CMAKE_SIZE} $<TARGET_FILE:${EXE}> --format=sysv")
    add_custom_command(TARGET ${EXE} POST_BUILD
        COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${EXE}> --format=sysv 
        COMMENT "Printing size"
    )
endfunction()


function(firmware_disasemble EXE)
    get_target_property(BINARY_DIR ${EXE} BINARY_DIR)
    set(ASM_FILE "${BINARY_DIR}/${EXE}.asm")
    add_custom_command(TARGET ${EXE} POST_BUILD
        BYPRODUCTS ${ASM_FILE}
        COMMAND ${CMAKE_OBJDUMP} -DgrwCS $<TARGET_FILE:${EXE}> > ${ASM_FILE}
        COMMENT "GEnerating disasembly"
    )
endfunction()
