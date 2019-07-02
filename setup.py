# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup


setup(name='contextplus',
      version='1.0.dev1',
      description='contextplus',
      long_description = open('README.rst').read(),
      classifiers=['Programming Language :: Python', 'Framework :: Pyramid'],
      keywords='traversal context resource',
      author='Adam & Paul Pty Ltd',
      author_email='software@adamandpaul.biz',
      url='https://github.com/adamandpaul/contextplus',
      license='bsd',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ])
