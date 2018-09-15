from setuptools import setup, find_packages

setup(
    name = "configpp",
    version = "0.0.1",
    description = "A config manager library for a brighter future!",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@gmail.com',
    url = '',
    license = 'MIT',
    install_requires = [
        'voluptuous~=0.10',
        'command-tree~=0.7',
        'python-slugify~=1.2',
        'python-dateutil~=2.7',
        'ruamel.yaml~=0.15.44',
        'PyYAML~=3.12',
    ],
    packages = find_packages(),
    extras_require = {
        'test': [
            'pytest~=3.2',
            'pytest-cov~=2.5',
            'voidpp-tools~=1.10',
            'pytest-watch~=4.1',
        ],
    },
    scripts = [
        'bin/evolution'
    ],
)
