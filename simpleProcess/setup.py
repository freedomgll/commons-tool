__author__ = 'lgu'

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [],includes =['re'],
                    include_files=['config/','icons/tank.ico','config.ini','readme.txt',
                                   (r"D:/Python33/tcl/tix8.4.3","tcl/tix8.4.3")],
                    optimize = 2, compressed = True)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

base = None

executables = [
    Executable('simpleProcess.py', base=base, targetName = 'simpleProcess.exe',icon='icons/tank.ico')
]

setup(name='simpleProcess',
      version = '0.7',
      description = 'Simple Process',
      options = dict(build_exe = buildOptions),
      executables = executables)