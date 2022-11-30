import re

from setuptools import find_packages, setup

with open("carbon/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras_require = {}
extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))

setup(
    name="carbon-simulator",
    version=version,
    author="Bancor Network",
    author_email="mike@bancor.network",
    description="""
                    Bancor python carbon and carbon library. 
                    This python package is developed and maintained by Bancor Research. 
                    It is meant to assist in the design, testing, and validating of Bancor protocol behavior.
                """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bancorprotocol/carbon-simulator",
    install_requires=open("requirements.txt").readlines(),
    extras_require=extras_require,
    # tests_require=open("requirements-test.txt").readlines(),
    packages=find_packages(),
    include_package_data=True,
)
