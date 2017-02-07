from setuptools import setup


setup(
    name='potfiles',
    version='0.1.0',
    packages=['potfiles'],
    entry_points={
        'console_scripts': [
            'potfiles = potbin.__main__:main'
        ]
    },
)
