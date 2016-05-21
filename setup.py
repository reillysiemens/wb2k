#!/usr/bin/env python3
import re
import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

readme_path = os.path.join(here, 'README.md')
with open(readme_path, 'r') as readme_file:
    readme = readme_file.read()

# Borrowed from https://github.com/Gandi/gandi.cli/blob/master/setup.py
version_path = os.path.join(here, 'wb2k', '__init__.py')
with open(version_path, 'r') as version_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version_file.read()).group(1)

requirements = [
    'click',
    'slackclient'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='wb2k',
    version=version,
    description='Welcome new folks to #general.',
    long_description=readme,
    author='Reilly Tucker Siemens',
    author_email='reilly@tuckersiemens.com',
    url='https://github.com/reillysiemens/wb2k',
    packages=find_packages(),
    package_dir={'wb2k': 'wb2k'},
    include_package_data=True,
    install_requires=requirements,
    license='ISCL',
    zip_safe=False,
    py_modules=['wb2k'],
    keywords='welcome bot Slack',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python :: 3 :: Only',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'wb2k=wb2k.__main__:cli',
        ],
    },
)
