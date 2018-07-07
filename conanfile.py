#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os


class MozJpegConan(ConanFile):
    name = "mozjpeg"
    version = "3.3.1"
    description = "MozJPEG reduces file sizes of JPEG images while retaining quality and compatibility with the " \
                  "ast majority of the world's deployed decoders"
    url = "https://github.com/bincrafters/conan-mozjpeg"
    homepage = "https://github.com/mozilla/mozjpeg"
    author = "Bincrafters <bincrafters@gmail.com>"
    # Indicates License type of the packaged library
    license = "BSD"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "SIMD": [True, False],
               "arithmetic_encoder": [True, False],
               "arithmetic_decoder": [True, False],
               "libjpeg7_compatibility": [True, False],
               "libjpeg8_compatibility": [True, False],
               "mem_src_dst": [True, False],
               "turbojpeg": [True, False],
               "java": [True, False],
               "enable12bit": [True, False]}
    default_options = "shared=False",\
                      "fPIC=True",\
                      "SIMD=True",\
                      "arithmetic_encoder=True",\
                      "arithmetic_decoder=True",\
                      "libjpeg7_compatibility=False",\
                      "libjpeg8_compatibility=False",\
                      "mem_src_dst=True",\
                      "turbojpeg=True",\
                      "java=False",\
                      "enable12bit=False"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/mozilla/mozjpeg"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        # FIXME : write PR, then remove after 3.3.2 release
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              '${CMAKE_SOURCE_DIR}', '${CMAKE_CURRENT_SOURCE_DIR}')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              'install(PROGRAMS ${CMAKE_CURRENT_BINARY_DIR}',
                              'install(PROGRAMS ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              '${CMAKE_BINARY_DIR}', '${CMAKE_CURRENT_BINARY_DIR}')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'sharedlib', 'CMakeLists.txt'),
                              '${CMAKE_SOURCE_DIR}', '${CMAKE_CURRENT_SOURCE_DIR}/..')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'simd', 'CMakeLists.txt'),
                              '${CMAKE_SOURCE_DIR}', '${CMAKE_CURRENT_SOURCE_DIR}/..')

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_TESTING'] = False
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['WITH_SIMD'] = self.options.SIMD
        cmake.definitions['WITH_ARITH_ENC'] = self.options.arithmetic_encoder
        cmake.definitions['WITH_ARITH_DEC'] = self.options.arithmetic_decoder
        cmake.definitions['WITH_JPEG7'] = self.options.libjpeg7_compatibility
        cmake.definitions['WITH_JPEG8'] = self.options.libjpeg8_compatibility
        cmake.definitions['WITH_MEM_SRCDST'] = self.options.mem_src_dst
        cmake.definitions['WITH_TURBOJPEG'] = self.options.turbojpeg
        cmake.definitions['WITH_JAVA'] = self.options.java
        cmake.definitions['WITH_12BIT'] = self.options.enable12bit
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions['WITH_CRT_DLL'] = 'MD' in str(self.settings.compiler.runtime)
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        if self.settings.os == 'Windows':
            self.build_cmake()
        else:
            self.build_configure()

    def build_configure(self):
        with tools.chdir(self.source_subfolder):
            self.run('autoreconf -fiv')
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = self.options.fPIC
            args = ['--prefix=%s' % os.path.abspath(self.package_folder)]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            args.append('--with-pic' if self.options.fPIC else '--without-pic')
            args.append('--with-simd' if self.options.SIMD else '--without-simd')
            args.append('--with-arith-enc' if self.options.arithmetic_encoder else '--without-arith-enc')
            args.append('--with-arith-dec' if self.options.arithmetic_decoder else '--without-arith-dec')
            args.append('--with-jpeg7' if self.options.libjpeg7_compatibility else '--without-jpeg7')
            args.append('--with-jpeg8' if self.options.libjpeg8_compatibility else '--without-jpeg8')
            args.append('--with-mem-srcdst' if self.options.mem_src_dst else '--without-mem-srcdst')
            args.append('--with-turbojpeg' if self.options.turbojpeg else '--without-turbojpeg')
            args.append('--with-java' if self.options.java else '--without-java')
            args.append('--with-12bit' if self.options.enable12bit else '--without-12bit')
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build_cmake(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        if self.settings.os == 'Windows':
            cmake = self.configure_cmake()
            cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
