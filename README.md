# List of things to todo

## A. From DBLP
1. retrieve all the DOIs (only proceedings, journals, books) included in DBLP, and include basic info (e.g. title and venue URL)

All DBLP data are available in one bit XML file that must be parsed in a streaming fashion. In order to do that in Python, there is a wonderful article at http://blog.behnel.de/posts/faster-xml-stream-processing-in-python.html. The idea is to use the `itemparse` method of `lxml`.

## B. From COCI
1. retrieve all citations involving any DBLP DOI, keeping track of citation creation date/year and if the citing and cited DOIs belong to the DBLP set (i.e. to understand if a citation is internal to DBLP, come from an external domain or goes to an external domain)

This can be done starting from the information retrived after A.1.


## C. From Crossref
1. retrieve all the publishers involved in incoming and outgoing citations

This can be done starting from the information retrived after having all the DOIs obtained in A.1 union B.1.


## D. What to retrieve
1. incoming and outgoing citations to/from DBLP entities
2. publishers providing incoming and outgoing citations

## E. Execution
1. `python extract_dblp_metadata.py -i dblp.xml -d dblp.dtd -o 01_dblp_data.csv`
2. `python extract_coci_citations.py -i coci_data/ -d 01_dblp_data.csv -o 02_citations.csv`
3. `python extract_crossref_publishers.py -o 03_crossref_publishers.csv`
4. `python retrive_involved_publishers.py -i 02_citations.csv -p 03_crossref_publishers.csv -o 04_publishers.csv`
5. `python analyse_publisher_citations.py -i 02_citations.csv -p 04_publishers.csv -d 01_dblp_data.csv -o 05_publisher_citations.csv`