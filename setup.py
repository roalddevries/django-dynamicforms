from setuptools import setup, find_packages

setup(
    name                 = 'django-dynamicforms',
    version              = '0.1',
    packages             = find_packages(),
    install_requires     = ['html2text'],
    author               = 'Roald de Vries'
    author_email         = 'roald@go2people.nl'
    include_package_data = True,
    url                  = 'https://github.com/roalddevries/django-dynamicforms/',
    license              = 'LICENSE.txt',
    long_description     = open('README.rst').read(),
)
