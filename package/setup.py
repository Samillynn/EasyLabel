from setuptools import setup, find_packages, find_namespace_packages

MAJOR = 0
MINOR = 1
MICRO = 9
VERSION = "%d.%d.%d" % (MAJOR, MINOR, MICRO)

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="easylabeltool",
    version=VERSION,
    author="Mark Huang",
    author_email="mark.h.huang@gmail.com",
    description="Easy Label Tool for internal use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    # package_dir=({"": "src"}),
    packages=find_namespace_packages(include=["easylabeltool"]),
    scripts=["easylabeltool/parse", "easylabeltool/qabank"],
    install_requires=["colorlog>=4.1.0", "markkk", "orderedset", "numpy", "pandas"],
    # extras_require={"dev": ["pytest", "tox", "wheel"]},
    # Classifiers ref: https://pypi.org/classifiers/
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
