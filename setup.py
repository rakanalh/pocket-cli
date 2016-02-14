from setuptools import setup, find_packages

setup(
    name='pocket-cli',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==6.2',
        'requests==2.9.1',
        'pocket-api'
    ],
    entry_points={
        'console_scripts': [
            'pocket-cli=pocket_cli.cli:main'
        ]
    },
)
