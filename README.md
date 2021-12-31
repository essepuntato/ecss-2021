# Scripts for analysing open citations in the Computer Science domain

**How to cite this software:** Peroni, S. (2021). Scripts for analysing open citations in the Computer Science domain (Version 1.0.0) [Computer software]. [https://doi.org/10.5281/zenodo.5812081](https://doi.org/10.5281/zenodo.5812081)

This repository contains a collection of scripts used to retrieve citation data from [OpenCitations' COCI](http://opencitations.net/index/coci) and bibliographic metadata from [DBLP](https://dblp.org) to provide a snapshot of the current availability of open citation data of publications in Informatics. The source datasets used by these scripts, i.e. COCI citation data and DBLP bibliographic metadata, can be retrieved in the websites of the two infrastructures mentioned above.


## A. Bibliographic data from DBLP
**Task:** retrieve all the DOIs (only proceedings, journals, books) included in DBLP, and include basic info (e.g. title and venue URL).

All DBLP data are available in one bit XML file that must be parsed in a streaming fashion. In order to do that in Python, there is a wonderful article at http://blog.behnel.de/posts/faster-xml-stream-processing-in-python.html which suggests to use `itemparse` method of `lxml`.

**Script:** `python extract_dblp_metadata.py -i dblp.xml -d dblp.dtd -o 01_dblp_data.csv`


## B. Citation data from COCI
**Task:** retrieve all citations involving any DBLP DOI, keeping track of citation creation date/year and if the citing and cited DOIs belong to the DBLP set (i.e. to understand if a citation is internal to DBLP, come from an external domain or goes to an external domain).

This can be done starting from the information retrived in A.

**Script:** `python extract_coci_citations.py -i coci_data/ -d 01_dblp_data.csv -o 02_citations.csv`


## C. Publishers from Crossref
**Task:** retrieve all the publishers available in Crossref.

**Script:** `python extract_crossref_publishers.py -o 03_crossref_publishers.csv`


## D. Publishers involved in open citations
**Task:** retrieve all the publishers involved in incoming and outgoing citations.

This can be done starting from the information retrived after having all the DOIs obtained from B complemented with publishers information extracted in C. This script will use also calls to the DataCite API to try to retrieve any missing publisher for cited entities.

**Script:** `python retrive_involved_publishers.py -i 02_citations.csv -p 03_crossref_publishers.csv -o 04_publishers.csv`


## E. Publishers' citations
**Task:** retrieve the number of entities, incoming citations and outgoing citations grouped by publisher.

It reuses all the data produced in A, B and D to produce the final outcome.

**Script:** `python analyse_publisher_citations.py -i 02_citations.csv -p 04_publishers.csv -d 01_dblp_data.csv -o 05_publisher_citations.csv`
