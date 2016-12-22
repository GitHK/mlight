import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
    "motor",
    "weakreflist"
]

# test dependencies
setup_requires = [
    'nose',
    'coverage',
]

setup(
    name='mlight',
    version='0.0.1',
    packages=['mlight'],
    install_requires=install_requires,
    setup_requires=setup_requires,
    test_suite="nose.collector",
)
