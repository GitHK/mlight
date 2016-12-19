import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
    "motor"
]

tests_require = [
    'mock',
    'nose',
]

setup(
    name='mlight',
    version='0.0.1',
    packages=['mlight'],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
)
