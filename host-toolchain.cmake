set(CMAKE_ASM_COMPILER ${CMAKE_CURRENT_LIST_DIR}/clang)
set(CMAKE_C_COMPILER   ${CMAKE_CURRENT_LIST_DIR}/clang)
set(CMAKE_CXX_COMPILER ${CMAKE_CURRENT_LIST_DIR}/clang++)

set(CMAKE_AR      ${CMAKE_CURRENT_LIST_DIR}/llvm-ar)
set(CMAKE_OBJCOPY ${CMAKE_CURRENT_LIST_DIR}/llvm-objcopy)
set(CMAKE_RANLIB  ${CMAKE_CURRENT_LIST_DIR}/llvm-ranlib)

foreach(_lang ASM C CXX)
    set(CMAKE_${_lang}_COMPILER_TARGET x86_64-linux-gnu)
endforeach()

set(CMAKE_CXX_FLAGS "-stdlib=libc++")

foreach(_lld_user EXE MODULE SHARED)
    set(CMAKE_${_lld_user}_LINKER_FLAGS "-fuse-ld=lld -stdlib=libc++ --rtlib=compiler-rt -resource-dir=${CMAKE_SYSROOT} --unwindlib=libunwind -lc++abi")
endforeach()
