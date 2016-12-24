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
    description='Asynchronous Web Framework based on aiohttp',
    author="Amit Nabarro",
    author_email='amit.nabarro@gmail.com',
    url='https://github.com/tbone-framework/tbone',
    license='MIT',
    long_description=open('README.md', 'r').read(),
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    tests_require=[],
)