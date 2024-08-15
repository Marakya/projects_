from setuptools import setup, find_packages
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
        'unittest',

    ],
    entry_points={
        'console_scripts': [
            'audio-augmenter=audio_augmenter.cli:main',
        ],
    },

    author="Ekaterina Maiatskaia",
    author_email="mayatskaya.katya@mail.ru",
    description="CLI tool for audio augmentation",
    long_description=open("README.md").read(),
    long_description_content_type="",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
