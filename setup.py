#!/usr/bin/env python
# encoding: utf-8
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


from tbone import __version__

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

setup(
    name='tbone',
    version=__version__,
    description='Full-duplex RESTful APIs for asyncio web applications',
    long_description= read('README.md'),
    author="475 Cumulus Ltd.",
    author_email='dev@475cumulus.com',
    url='https://github.com/475Cumulus/TBone',
    license='MIT',
    python_requires='>=3.5.0',
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    tests_require=[],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
