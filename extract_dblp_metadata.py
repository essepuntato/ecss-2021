# This script is responsible for extracting relevant metadata from 
# a DBLP XML dump. The DBLP XML dump is one single XML file of 
# more than 3 GB, that is parsed in streaming for retrieving 
# all the needed data.

from argparse import ArgumentParser
import lxml.etree as ET
from re import sub
from urllib.parse import unquote
from collections import defaultdict
from os.path import exists
from csv import DictWriter

csv_headers = (
    "doi", "dblp_id", "type", "title", "year", "venue_dblp_id", "additional_dois"
)


def normalise_doi(id_string):
    try:
        doi_string = sub("\0+", "", sub("\s+", "", unquote(id_string[id_string.index("10."):])))
        return doi_string.lower().strip()
    except:  # Any error in processing the DOI will return None
        return None


def get_dois(elem):
    result = []

    for child in elem.findall("ee"):
        child_text = get_text(child)
        if "doi.org/" in child_text:
            doi_string = normalise_doi(child_text)
            if doi_string is not None:
                result.append(doi_string)

    return result


def get_venue_dblp_id(elem):
    result = ""

    crossref = elem.find("crossref")
    if crossref is not None:
        result = get_text(crossref)
    else:
        url = elem.find("url")
        if url is not None:
            result = "/".join(get_text(url).split("/")[:3])

    return result


def store_csv_on_file(f_path, header, json_obj):
    f_exists = exists(f_path)
    with open(f_path, "a", encoding="utf8") as f:
        dw = DictWriter(f, header)
        if not f_exists:
            dw.writeheader()
        dw.writerow(json_obj)


def get_text(elem):
    return ''.join(elem.itertext())


def process(data_path, dtd_path, out_path):
    ET.DTD(file=dtd_path)
    
    for event, elem in ET.iterparse(
        data_path, events=("end",), load_dtd=True, remove_blank_text=True, 
        tag=("article", "inproceedings", "proceedings", "book", "incollection")):

        dois = get_dois(elem)
        if dois: 
            cur_el = defaultdict(str)

            # Get all DOIs
            for idx, doi in enumerate(dois):
                if idx == 0:
                    cur_el["doi"] = doi
                else:
                    cur_el["additional_dois"] += doi + " "
            cur_el["additional_dois"] = cur_el["additional_dois"].strip()
            
            # Get DBLP identifier
            cur_el["dblp_id"] = elem.get("key")

            # Get type
            cur_el["type"] = elem.tag

            # Get title
            title_string = get_text(elem.find("title"))
            if title_string.endswith("."):
                title_string = title_string[:-1]
            cur_el["title"] = title_string

            # Get year
            cur_el["year"] = get_text(elem.find("year"))

            # Get venue
            cur_el["venue_dblp_id"] = get_venue_dblp_id(elem)

            # Store data
            store_csv_on_file(out_path, csv_headers, cur_el)
        
        elem.clear()


if __name__ == "__main__":
    arg_parser = ArgumentParser("Extract metadata from DBLP")
    arg_parser.add_argument("-i", "--input", required=True,
                            help="The input XML file containing the DBLP dump.")
    arg_parser.add_argument("-d", "--dtd", required=True,
                            help="The input DTD file referring to the DBLP dump.")
    arg_parser.add_argument("-o", "--output", required=True,
                            help="The output CSV file where to store relevant information.")
    args = arg_parser.parse_args()

    print("Start process")
    process(args.input, args.dtd, args.output)
    print("Process finished")