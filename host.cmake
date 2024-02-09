set(CMAKE_BUILD_TYPE Release CACHE STRING "")
set(LLVM_DISTRIBUTION_COMPONENTS
    clang
    lld

    llvm-ar
    llvm-ranlib
    llvm-objcopy

    clang-resource-headers

    CACHE STRING "")

set(LLVM_ENABLE_PROJECTS "clang;lld" CACHE STRING "")
