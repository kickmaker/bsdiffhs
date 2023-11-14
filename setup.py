import re
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


kwds = {}
try:
    kwds['long_description'] = open('README.rst').read()
except IOError:
    pass

# Read version from bsdiff/__init__.py
pat = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open('bsdiffhs/__init__.py').read()
kwds['version'] = eval(pat.search(data).group(1))

setup(
    name = "bsdiffhs",
    author = "Kickmaker",
    author_email = "romainp@kickmaker.net",
    url = "https://github.com/kickmaker/bsdiffhs",
    license = "BSD",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    description = "binary diff and patch using the BSDIFFHS-format",
    long_description_content_type = "text/x-rst",
    packages = ["bsdiffhs"],
    ext_modules = [Extension(name = "bsdiffhs.core",
                             sources = ["bsdiffhs/core.c"])],
    install_requires = ["heatshrink2"],
    entry_points = {
        'console_scripts': [
            'bsdiffhs = bsdiffhs.cli:main_bsdiffhs',
            'bspatchhs = bsdiffhs.cli:main_bspatchhs',
        ],
    },
    **kwds
)
