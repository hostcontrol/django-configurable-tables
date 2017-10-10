import os

from setuptools import setup, find_packages

VERSION = '0.0.1'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-configurable-tables',
    version=VERSION,
    long_description=README,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    extras_require={
        'dev': [
            'bumpversion==0.5.3',
            'twine == 1.6.5',
        ],
        'doc': [
            'Sphinx==1.4.4',
            'sphinx-autobuild==0.6.0',
        ]
    },
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'Django>=1.8,<1.9',
        'jsonfield',
        'six>=1.10.0,<1.11'
    ],
    tests_require=[
        'pytest-django',
        'pytest-cov',
        'mock>=2.0',
    ],
    url='https://github.com/hostcontrol/django-configurable-tables',
    license='MIT',
    author='Hostcontrol',
    author_email='info@hostcontrol.com',
    description='Install Django configurable tables.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]

)
