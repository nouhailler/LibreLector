from setuptools import setup, find_packages

setup(
    name="librelector",
    version="0.1.0",
    description="Lecteur EPUB open-source avec TTS neuronal offline pour Linux",
    author="LibreLector Contributors",
    license="GPL-3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "ebooklib>=0.18",
        "beautifulsoup4>=4.12",
        "lxml>=4.9",
        "nltk>=3.8",
        "PyGObject>=3.44",
        "pydub>=0.25",
    ],
    extras_require={
        "dev": ["pytest", "black", "ruff"],
    },
    entry_points={
        "console_scripts": [
            "librelector=librelector.main:main",
        ],
    },
)
