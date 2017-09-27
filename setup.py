#!/usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


from tbone import __version__


setup(
    name='tbone',
    version=__version__,
    description='Full-duplex RESTful APIs for asyncio web applications',
    author="475 Cumulus Ltd.",
    author_email='dev@475cumulus.com',
    url='https://github.com/475Cumulus/TBone',
    license='MIT',
    long_description=open('README.md', 'r').read(),
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    tests_require=[],
)