import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shapely_ext",
    version="0.1.4",
    author="pd",
    author_email="pyeprog@foxmail.com",
    description="a shapely extension package providing magic function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyeprog/shapely_ext",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Shapely>=1.7.0",
        "scipy>=1.4.1",
        "numpy>=1.18.4"
    ]
)