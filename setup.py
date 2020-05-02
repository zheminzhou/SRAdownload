import os, sys
from setuptools import setup, find_packages
from SRAdownload import __VERSION__

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SRAdownload',
    version=__VERSION__,
    #scripts=['PEPPA.py'] ,
    author="Zhemin Zhou",
    author_email="zhemin.zhou@warwick.ac.uk",
    description="downloads SRA short reads from either NCBI or EBI and converts them into fastq.gz files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zheminzhou/SRAdownload",
    packages = ['SRAdownload'],
    package_dir = {'SRAdownload':'.'},
    keywords=['bioinformatics', 'genomics', 'short reads', 'SRA'],
    install_requires=['click'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'SRAdownload = SRAdownload:main',
    ]},
    package_data={'SRAdownload': ['LICENSE', 'README.*']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
    ],
 )

