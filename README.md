# CALPHAD .TDB Ingester

## Description
The CALPHAD .TDB ingester is an ingester used for extracting data, about a thermodynamic system described in the raw .TDB file, in to records ([PIFs](http://citrineinformatics.github.io/pif-documentation/)) on the Citrination platform. The ingester extracts information on only the elements, phases, and species in the system, and not the full thermodynamic functions.

## Example input file
To see sample TDB files, see [here](https://github.com/CitrineInformatics/calphad_tdb_ingester/tree/make-public-ready/test_files).

## Example output dataset
A sample dataset created by ingesting the two test files in the repository can be seen [here](https://citrination.com/datasets/157270).

## Related useful resources
- [Ingester documentation](http://help.citrination.com/knowledgebase/articles/1834348)
- [PIF schema](http://citrineinformatics.github.io/pif-documentation/)
- [Video tutorial on creating a dataset and using an ingester to upload data to it](https://youtu.be/g9DTHnIp1kQ)
- [Tutorials on using various features of the Citrination platform](https://citrination.org/learn/)