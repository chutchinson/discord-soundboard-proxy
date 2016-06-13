import setuptools

setuptools.setup(
    name='soundboard',
    version='0.0.1',
    author='Chris Hutchinson',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=[
        'PyYAML>=3.11'
    ],
    scripts=[
        'bin/lab2635_soundboard.py'
    ]
)
