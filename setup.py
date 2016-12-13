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
    description='Asynchronous Web Framework',
    author="Amit Nabarro",
    author_email='amit.nabarro@gmail.com',
    url='https://github.com/tbone-framework/tbone',
    license='MIT',
    long_description=open('README.md', 'r').read(),
    packages=find_packages(),
    install_requires=[
        'schematics >= 2.0.0a1',
        'motor >= 1.0',
        'python-dateutil >= 2.5.3',
        'aiohttp >= 1.1.6',
        'aiodns >= 1.1.1',
        'aiohttp-cors >= 0.5.0',
        'cchardet >= 1.1.1',
    ],
    tests_require=[],
)