import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='coder-dojo-paris',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='A simple Django app',
    author='Tchekda',
    author_email='contact@tchekda.fr',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
