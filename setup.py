import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytct",
    version="0.0.1",
    author="Ruggero Turra",
    author_email="ruggero.turra@cern.ch",
    description="Read, manipulate and visualize data taken by PSTCT by Particulars",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wiso/pytct",
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    python_requires='>=3.4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
    ],
)
