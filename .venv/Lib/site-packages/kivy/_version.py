# This file is imported from __init__.py and exec'd from setup.py

MAJOR = 2
MINOR = 3
MICRO = 2
RELEASE = True

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not RELEASE:
    # if it's a rcx release, it's not proceeded by a period. If it is a
    # devx release, it must start with a period
    __version__ += '.dev0'


_kivy_git_hash = 'ec09ee880c666e70de42501f36dbc43e349e3712'
_kivy_build_date = '20261107'

