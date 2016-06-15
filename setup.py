from setuptools import setup, find_packages

# currently missing discord.py install dependency because this script relies on the async branch

setup(
    name='soundboard',
    version='0.0.1',
    author='Chris Hutchinson',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'PyYAML>=3.11'
    ],
    scripts=[
        'bin/lab2635_soundboard.py'
    ]
)
