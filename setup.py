import pathlib
import setuptools

setuptools.setup(
    name="SoccerViz",
    version="0.0.2",
    description="A Package to allow analyzing soccer event data easily",
    long_description = pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Athal Akbar",
    author_email="athalkhan13@gmail.com",
    license="Unlicensed",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Other Audience",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.12"
    ],
    keywords=['python','soccer','soccer analysis','passing network'],
    python_requires = ">=3.8,<=3.12.1",
    packages=setuptools.find_packages(),
    include_package_data=True
)