import pandas as pd
from argparse import ArgumentParser
from os.path import exists
from json import load, dump
from extract_crossref_publishers import get_via_requests
from collections import deque

chunksize = 10 ** 5
csv_headers = (
    "citing", "cited", "creation", "dblp_citing", "dblp_cited"
)
MAX_TRY = 5
SLEEPING_TIME = 5
headers = {
    "User-Agent": 
    "OpenCitations "
    "(http://opencitations.net; mailto:contact@opencitations.net)",
}


def get_all_doi_prefixes(citation_path):
    result = {}

    print("Retrieving DOI prefixes in citations")
    chunk_idx = 0
    for chunk in pd.read_csv(citation_path, chunksize=chunksize, 
                             dtype={"citing": "str", "cited": "str", "creation": "str", "dblp_citing": "str", "dblp_cited": "str"}):
        chunk_idx += 1
        print("\t reading chuck", chunk_idx)
        for index, row in chunk.iterrows():
            citing = row["citing"]
            citing_prefix = citing.split("/")[0]
            if citing_prefix not in result:
                result[citing_prefix] = citing

            cited = row["cited"]
            cited_prefix = cited.split("/")[0]
            if cited_prefix not in result:
                result[cited_prefix] = cited

    return result


def get_in_json(json, key_list):
    keys = deque(key_list)

    while json is not None and len(keys) > 0:
        key = keys.popleft()
        json = json.get(key)
    
    return json


def get_datacite_publisher(doi):
    get_url = "https://api.datacite.org/dois/" + doi
    req = get_via_requests(get_url)
    
    if req is not None:
        return get_in_json(req, ["data", "attributes", "publisher"])


def process(citation_path, publisher_path, out_path):
    tmp_file = out_path + "_tmp_doi_prefixes.json"
    if exists(tmp_file):
        with open(tmp_file, encoding="utf-8") as f:
            doi_prefixes = load(f)
    else:
        doi_prefixes = get_all_doi_prefixes(citation_path)
        with open(tmp_file, "w", encoding="utf-8") as f:
            dump(doi_prefixes, f, ensure_ascii=False)


    publishers = pd.read_csv(publisher_path)
    prefixes_to_do = set()
    datacite_counter = 0

    for prefix in doi_prefixes:
        prefix_df = publishers[publishers.prefix == prefix]
        if len(prefix_df) == 0:
            print("\nQuerying DataCite for retrieving info for prefix", prefix)
            doi = doi_prefixes[prefix]
            publisher = get_datacite_publisher(doi)
            if publisher is not None:
                print("\tPublisher found:", publisher, "- via DOI", doi)
                publishers = publishers.append({"id": "dc:" + str(datacite_counter), "name": publisher, "prefix": prefix}, ignore_index=True)
                datacite_counter += 1
            else:
                prefixes_to_do.add(prefix)

    print("Number of prefixes not found:", len(prefixes_to_do))
    print("Saving the updated file into the output path specified")
    publishers.to_csv(out_path, index=False)
        

if __name__ == "__main__":
    arg_parser = ArgumentParser("Extract citations from COCI")
    arg_parser.add_argument("-i", "--input", required=True,
                            help="The input directory containing citations of interest.")
    arg_parser.add_argument("-p", "--publishers", required=True,
                            help="The CSV file with the Crossref publishers.")
    arg_parser.add_argument("-o", "--output", required=True,
                            help="The output CSV file where to store all the publishers.")
    args = arg_parser.parse_args()

    print("Start process")
    process(args.input, args.publishers, args.output)
    print("Process finished")