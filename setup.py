from setuptools import setup, find_packages

setup(
    name = 'jpath',
    version = '0.1',
    author = 'Spondon Saha',
    author_email = 'spondonsaha@gmail.com',
    url='https://github.com/shuvozula/python-jpath',
    license = 'Apache Software License (ASF)',
    long_description="Python JSON parser using JPath strings",
    keywords="JSON xpath jpath python",
    packages = find_packages(),
    zip_safe = True,
)