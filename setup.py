from setuptools import setup, find_packages

setup(name='calphad_tdb_ingester',
    version='2.0.1',
    url='http://github.com/CitrineInformatics/calphad-tdb-ingester',
    description='This ingester converts CALPHAD database files (with extension .TDB) into PIFs',
    author='Saurabh Bajaj',
    author_email='saurabh@citrine.io',
    packages=find_packages(),
    install_requires=[
        'pypif',
    ],
    entry_points={
        'citrine.dice.converter': [
            'calphad_tdb_ingester = calphad_tdb_ingester.converter',
        ],
    },
)
