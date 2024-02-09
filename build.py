import os
import subprocess
import shutil
from pathlib import Path

script_dir = Path(__file__).parent

runtimes_dir = Path('/tmp/llvm-project/runtimes')
llvm_dir = Path('/tmp/llvm-project/llvm')
musl_dir = Path('/tmp/musl')
cross_linux_headers_dir = Path('/tmp/cross-linux-headers')

musl_arch = 'x86_64'
kernel_arch = 'x86'
kernel_version = '4.14.x'

def clean_dir(d: Path):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(exist_ok=True, parents=True)

    assert(not list(d.iterdir())), 'clean_dir failed'

    return d

def build_host_compiler():
    build_dir = clean_dir(Path('/tmp/moss-build-host-llvm'))
    stage_dir = clean_dir(Path('/tmp/moss-stage-host-llvm'))
    install_dir = clean_dir(Path('/tmp/moss-host-toolchain'))

    env = {
        **os.environ,
        'CC' : 'clang-15',
        'CXX' : 'clang++-15',
    }

    subprocess.check_call([
            'cmake',
            '-G', 'Ninja',
            '-DCMAKE_C_COMPILER_LAUNCHER=ccache',
            '-DCMAKE_CXX_COMPILER_LAUNCHER=ccache',
            f'-DCMAKE_INSTALL_PREFIX={stage_dir.as_posix()}',
            '-C', script_dir / 'host.cmake',
            llvm_dir,
        ],
        cwd=build_dir,
        env=env)

    subprocess.check_call([
            'ninja', 'install-distribution',
        ],
        cwd=build_dir)

    # TODO:
    # * CUDA
    # * non-root user
    # * check-all: (just check-clang / check-lld?)
    # subprocess.check_call([
    #         'ninja', 'check-all',
    #     ],
    #     cwd=build_dir)

    shutil.copytree(stage_dir, install_dir, dirs_exist_ok=True)
    shutil.copy(script_dir / 'host-toolchain.cmake', install_dir / 'bin')

def make_canadian_host_isolation():
    isolation_dir = clean_dir(Path('/tmp/moss-host-binaries/bin'))

    for x in [
        'rm',
        'sed',
        'tr',
        'cat',
        'ln',
        'make',
        'mkdir',
        'cp',
        'mv',
        'chmod',
        'cmake',
        'ninja',
        'sh',
        'uname',
    ]:
        z = shutil.which(x)
        if z:
            os.symlink(z, isolation_dir / x)

        else:
            raise RuntimeError(f'could not find {x}')

def build_canadian_host_headers():
    headers_dir = clean_dir(Path('/tmp/moss-headers-canadian-host/usr'))

    musl_headers_dir = clean_dir(Path('/tmp/moss-headers-canadian-host-musl'))

    subprocess.check_call([
            'make', 'install-headers',
            f'DESTDIR={musl_headers_dir.as_posix()}',
            f'ARCH={musl_arch}',
            'prefix=',
        ],
        cwd=musl_dir)

    kernel_headers_dir = cross_linux_headers_dir / kernel_version / kernel_arch / 'include'
    shutil.copytree(kernel_headers_dir, headers_dir / 'include', dirs_exist_ok=True)
    shutil.copytree(musl_headers_dir, headers_dir, dirs_exist_ok=True)

def build_musl():
    isolation_dir = Path('/tmp/moss-host-binaries/bin')
    toolchain_dir = Path('/tmp/moss-host-toolchain/bin')

    env = {
        **os.environ,
        'PATH' : ':'.join(x.as_posix() for x in [
            toolchain_dir,
            isolation_dir,
        ]),
        'CC' : 'clang',
        'CXX' : 'clang++',
        'AR' : 'llvm-ar',
        'RANLIB' : 'llvm-ranlib',
    }

    musl_build_dir = clean_dir(Path('/tmp/moss-build-canadian-host-musl'))
    musl_stage_dir = clean_dir(Path('/tmp/moss-stage-canadian-host-musl'))

    subprocess.check_call([
            musl_dir / 'configure',
            f'ARCH={musl_arch}',
            '--disable-shared',
        ],
        cwd=musl_build_dir,
        env=env)

    subprocess.check_call([
            'make',
            'install-libs',
            '-j',
            f'DESTDIR={musl_stage_dir.as_posix()}',
            'prefix=',
        ],
        cwd=musl_build_dir,
        env=env)

def build_llvm_runtimes():
    isolation_dir = Path('/tmp/moss-host-binaries/bin')
    toolchain_dir = Path('/tmp/moss-host-toolchain/bin')

    headers_dir = Path('/tmp/moss-headers-canadian-host/usr')

    env = {
        **os.environ,
        'PATH' : ':'.join(x.as_posix() for x in [
            toolchain_dir,
            isolation_dir,
        ]),
        'CC' : 'clang',
        'CXX' : 'clang++',
    }

    runtimes_build_dir = clean_dir(Path('/tmp/moss-build-canadian-host-runtimes'))
    runtimes_stage_dir = clean_dir(Path('/tmp/moss-stage-canadian-host-runtimes'))

    toolchain_file = toolchain_dir / 'host-toolchain.cmake'

    subprocess.check_call([
            'cmake',
            '-G', 'Ninja',
            f'-DCMAKE_TOOLCHAIN_FILE={toolchain_file.as_posix()}',
            f'-DCMAKE_SYSROOT={headers_dir.as_posix()}',
            f'-DCMAKE_INSTALL_PREFIX={runtimes_stage_dir.as_posix()}',
            '-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY',
            '-C', script_dir / 'canadian-host-runtimes.cmake',
            runtimes_dir
        ],
        cwd=runtimes_build_dir,
        env=env)

    subprocess.check_call([
            'ninja', 'install',
        ],
        cwd=runtimes_build_dir)

def build_canadian_host_sysroot():
    sysroot_dir = clean_dir(Path('/tmp/moss-sysroot-canadian-host/usr'))

    build_musl()
    build_llvm_runtimes()

    headers_dir = Path('/tmp/moss-headers-canadian-host/usr')
    musl_stage_dir = Path('/tmp/moss-stage-canadian-host-musl')
    runtimes_stage_dir = Path('/tmp/moss-stage-canadian-host-runtimes')

    shutil.copytree(musl_stage_dir, sysroot_dir, dirs_exist_ok=True)
    shutil.copytree(runtimes_stage_dir, sysroot_dir, dirs_exist_ok=True)
    shutil.copytree(headers_dir, sysroot_dir, dirs_exist_ok=True)


def build_canadian_host_compiler():
    build_dir = clean_dir(Path('/tmp/moss-build-canadian-host-llvm'))
    stage_dir = clean_dir(Path('/tmp/moss-stage-canadian-host-llvm'))
    install_dir = clean_dir(Path('/tmp/moss-canadian-host-toolchain'))

    isolation_dir = Path('/tmp/moss-host-binaries/bin')
    toolchain_dir = Path('/tmp/moss-host-toolchain/bin')

    env = {
        **os.environ,
        'PATH' : ':'.join(x.as_posix() for x in [
            toolchain_dir,
            isolation_dir,
        ]),
        'CC' : 'clang',
        'CXX' : 'clang++',
    }

    toolchain_file = toolchain_dir / 'host-toolchain.cmake'
    sysroot_dir = Path('/tmp/moss-sysroot-canadian-host')

    subprocess.check_call([
            'cmake',
            '-G', 'Ninja',
            f'-DCMAKE_INSTALL_PREFIX={stage_dir.as_posix()}',
            f'-DCMAKE_TOOLCHAIN_FILE={toolchain_file.as_posix()}',
            f'-DCMAKE_SYSROOT={sysroot_dir.as_posix()}',
            '-C', script_dir / 'canadian-host.cmake',
            llvm_dir,
        ],
        cwd=build_dir,
        env=env)

    subprocess.check_call([
            'ninja', 'install-distribution',
        ],
        cwd=build_dir)

def main():
    # build_host_compiler()

    make_canadian_host_isolation()

    # build_canadian_host_headers()
    # build_canadian_host_sysroot()

    build_canadian_host_compiler()

if __name__ == '__main__':
    main()
