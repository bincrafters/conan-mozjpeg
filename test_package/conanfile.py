#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    def test(self):
        bin_path = os.path.join("bin", "test_package")
        img_name = os.path.join(self.source_folder, "testimg.jpg")
        self.run('%s %s' % (bin_path, img_name), run_environment=True)
