from setuptools import find_packages, setup


setup(
    name="econet24_api",
    packages=find_packages(include=["econet24_api"]),
    version="0.0.4",
    description="Basic Econet24 API",
    author="Andis Roze",
    license="MIT",
    install_requires=["requests==2.26.0"],
    setup_requires=["pytest-runner==5.3.1"],
    tests_require=["pytest==6.2.5"],
    test_suite="tests",
)
