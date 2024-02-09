set(CMAKE_BUILD_TYPE Release CACHE STRING "")

set(LLVM_ENABLE_RUNTIMES "compiler-rt;libcxx;libcxxabi;libunwind" CACHE STRING "")

# Do not build shared libraries
set(LIBCXX_ENABLE_SHARED    OFF CACHE BOOL "")
set(LIBCXXABI_ENABLE_SHARED OFF CACHE BOOL "")
set(LIBUNWIND_ENABLE_SHARED OFF CACHE BOOL "")

# Use musl libc for libc++ locale
set(LIBCXX_HAS_MUSL_LIBC ON CACHE BOOL "")

# Insist on -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON CACHE BOOL "")
set(LLVM_ENABLE_PIC                 ON CACHE BOOL "")

# Build only the bits of compiler-rt required to produce executables
# TODO: linux headers are busted (can't find __NR_mmap2, bad unistd include?)
# TODO: can we get some way of turning this all off by default, or of picking only certain dirs?
#       only really want builtins, crt (just build builtins folder??)
set(COMPILER_RT_DEFAULT_TARGET_ONLY ON  CACHE BOOL "")
set(COMPILER_RT_BUILD_SANITIZERS    OFF CACHE BOOL "")
set(COMPILER_RT_BUILD_XRAY          OFF CACHE BOOL "")
set(COMPILER_RT_BUILD_MEMPROF       OFF CACHE BOOL "")
set(COMPILER_RT_BUILD_ORC           OFF CACHE BOOL "")
set(COMPILER_RT_BUILD_LIBFUZZER     OFF CACHE BOOL "")
