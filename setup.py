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
        executables=[Executable('HaxballParser/__main__.py')]
    )

setup(
    name = "HaxballParser",
    version = "0.1",
    author = "drivfe",
    description = (
        "Parses Haxball replay files"
    ),
    keywords = "hax haxball parse parser dump dumper",
    packages = ['HaxballParser'],
    entry_points={
        'console_scripts': [
            'haxballparser = HaxballParser.__main__:main',
        ]
    },
    **cx
)