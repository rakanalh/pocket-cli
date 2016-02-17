from setuptools import setup, find_packages

setup(
    name='pocket-cli',
    version='0.1.2',
    author='Rakan Alhneiti',
    author_email='rakan.alhneiti@gmail.com',
    url='https://github.com/rakanalh/pocket-api',

    license='LICENSE',
    description='A terminal application for Pocket',
    long_description=open('README.md').read(),

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        'click==6.2',
        'requests==2.9.1',
        'progress==1.2',
        'future==0.15.2',
        'six==1.10.0',
        'pocket-api'
    ],
    entry_points={
        'console_scripts': [
            'pocket-cli=pocket_cli.cli:main'
        ]
    },
)
