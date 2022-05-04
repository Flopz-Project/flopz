from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='flopz',
    version='0.1.1',
    packages=find_packages(),
    url='https://github.com/Flopz-Project/flopz',
    license='Apache License',
    author='Noelscher Consulting GmbH',
    author_email='ferdinand@noelscher.com',
    description='flopz - Low Level Assembler and Firmware Instrumentation Toolkit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['bitstring'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
)
