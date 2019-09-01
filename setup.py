from setuptools import setup, find_packages

setup(name='domain_powerplan_compare',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'xlrd',
        'deepdiff',
        'openpyxl',
        'fleep',
    ]
)