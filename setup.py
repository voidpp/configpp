from setuptools import setup, find_packages

setup(
    name = "configpp",
    description = "A config manager library for a brighter future!",
    author = "Lajos Santa",
    author_email = "santa.lajos@gmail.com",
    url = "https://github.com/voidpp/configpp",
    license = "MIT",
    include_package_data = True,
    install_requires = [
        "voluptuous~=0.11",
        "command-tree~=0.7",
        "python-slugify~=1.2",
        "python-dateutil~=2.7",
        "ruamel.yaml~=0.15.44",
        "typing-inspect~=0.3",
        "PyYAML~=5.1",
        "voidpp-tools~=1.11",
        "slugify~=0.0.1"
    ],
    packages = find_packages(),
    extras_require = {
        "test": [
            "pytest~=3.2",
            "pytest-cov~=2.5",
            "voidpp-tools~=1.11",
            "coveralls~=1.2",
            "pytest-watch~=4.1"],
        "docs": [
            "semantic-version~=2.6",
            "sphinx-rtd-theme~=0.4",
            "Sphinx~=1.8",
        ]
    },
    use_scm_version = True,
    setup_requires = [
        "setuptools_scm",
    ],
    scripts = [
        "bin/evolution",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
