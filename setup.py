from distutils.core import setup

setup(
    name='fastpac',
    description='Arch Linux package downloader',
    version='0.1',
    author='Quinn Parrott',
    url='https://github.com/parrottq/fastpac',
    packages=['fastpac'],
    install_requires=['requests'],
    extras_require={
        'dev': [
            'pytest',
        ],
    },
    license='GPL3'
)
