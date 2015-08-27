import sys

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
    }
)