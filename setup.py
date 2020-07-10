#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='paranestamol',
    version='0.0.9',
    description='A QtQuick-based nested sampling visualisation tool.',
    author='Aleksandr Petrosyan',
    author_email='a-p-petrosyan@yandex.ru',
    url='https://github.com/appetrosyan/paranestamol',
    packages=find_packages(),
    install_requires=['matplotlib_backend_qtquick', 'anesthetic', 'pyside2',
                      'numpy', 'matplotlib'],

    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research'
    ]
)
