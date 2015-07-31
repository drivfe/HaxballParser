import sys

if not 'build' in sys.argv[1]:
    from setuptools import setup
    cx = {}
else:
    from cx_Freeze import setup, Executable
    cx = dict(
        options={
            "build_exe" : {
                'build_exe' : 'cxbuild/',
                'compressed' : True
            }
        },
        executables=[Executable('HBRDumper/__main__.py')]
    )

setup(
    name = "HBRDumper",
    version = "0.1",
    author = "drivfe",
    description = (
        "Dump Haxball replay file data"
    ),
    keywords = "haxball",
    packages = ['HBRDumper'],
    entry_points={
        'console_scripts': [
            'HBRDumper = HBRDumper.__main__:main',
        ]
    },
    **cx
)