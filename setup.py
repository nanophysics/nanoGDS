import os
import setuptools


requirements = ["numpy>=1.13", "setuptools>=40.1.0", "gdspy"]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nanogds",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nanophysics/nanoGDS",
    author="Max Ruckriegel",
    author_email="maxr@ethz.ch",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    keywords="gds gdspy",
    packages=["nanogds"],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
)
