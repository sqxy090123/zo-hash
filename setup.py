from setuptools import setup, find_packages

setup(
    name='zo-hash',
    version='1.0.0',
    description='A custom sponge-based 256-bit hash with ZO encoding',
    author='sqxy090123',
    author_email='sqx20150423@gmail.com',
    url='https://github.com/sqxy090123/zo-hash',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)