from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="overlay-cheetah",
    version="3.0.0",
    author="tap919",
    author_email="support@overlaycheetah.com",
    description="Advanced AI-powered autocoder tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tap919/Overlay-Cheetah-V3",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "overlay-cheetah=autocoder.main:main",
        ],
    },
    include_package_data=True,
    keywords="autocoder, code generation, ai, development tools, branding",
    project_urls={
        "Bug Reports": "https://github.com/tap919/Overlay-Cheetah-V3/issues",
        "Source": "https://github.com/tap919/Overlay-Cheetah-V3",
        "Documentation": "https://github.com/tap919/Overlay-Cheetah-V3/blob/main/docs/README.md",
    },
)
