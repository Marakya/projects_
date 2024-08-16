from setuptools import setup, find_packages

# Fallback for README.md
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name='audio_augmenter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'torch',
        'soundfile',
        'matplotlib',
        'IPython',
        'click',

    ],
    entry_points={
        'console_scripts': [
            'audio-augmenter=audio_augmenter.cli:main',
        ],
    },

    author="Ekaterina Maiatskaia",
    author_email="mayatskaya.katya@mail.ru",
    description="CLI tool for audio augmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Marakya/projects_/tree/main/Audio/Open_Media",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
