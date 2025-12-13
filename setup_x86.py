# -*- coding: utf-8 -*-

from setuptools import setup
from main import VERSION

# NOTE: using py2app because nicegui-pack (based on pyinstaller) isn't working
# - the built app crashes immediately after opening

APP = ['main.py']
DATA_FILES = [('static', ['static/bg1.jpeg']), '.nicegui']
OPTIONS = {
    'argv_emulation': False,
    'arch': 'x86_64',
    'iconfile': 'static/appicon.png',
    'plist': {
        'CFBundleIdentifier': 'com.jriggles.everlight',
        'CFBundleShortVersionString': VERSION,
        'LSUIElement': False,  # not a menu bar app
        'NSHumanReadableCopyright': (
            'Copyright © 2025 John Riggles [sudo_whoami] - MIT License'
        ),
    },
    'packages': ['anyio', 'httpx', 'nicegui', 'phue', 'pygments', 'uvicorn',],
}

setup(
    app=APP,
    name='Everlight',
    version=VERSION,
    description='Lighting controller for our at-home D&D game',
    author='J. Riggles [sudo_whoami]',
    url='https://github.com/JRiggles/Everlight',
    license='MIT',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
