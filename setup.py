from setuptools import setup

setup(
    name='gazoo',
    version='0.0.0',
    author='John Schroeder',
    author_email='john@schroedernet.software',
    description='Minecraft bedrock server wrapper',
    url='https://gitlab.com/thesmiley1',
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'gazoo=gazoo:main',
        ],
    },
)
