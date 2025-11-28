import os
import sys

from setuptools import find_packages, setup

from dj_authkit import get_version

long_description = open("README.md").read()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


setup(
    name="dj_authkit",
    packages=find_packages(where="."),
    version=get_version(),
    description="A Django app that provides a customizable, pluggable user authentication and management system.",
    data_files=[("", ["README.md"])],
    license="MIT",
    author="Ngahunj",
    install_requires=[
        "django>=5.1",
        # "guardian",
    ],
    python_requires=">=3.8",
    author_email="joe@shopyangu.com",
    url="https://github.com/Ngahu/commerce_hub",
    keywords="Django, auth",
    classifiers=[
        "Development Status :: 1 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Shopyangu clients",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
)
