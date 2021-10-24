import pandas as pd
from argparse import ArgumentParser
from os.path import exists
from json import load, dump

from pandas.io.formats.format import Datetime64TZFormatter
from extract_crossref_publishers import get_via_requests
from collections import deque, defaultdict
from extract_coci_citations import store_csv_on_file

chunksize = 10 ** 5
csv_headers = ("publisher", "n_entity", "outgoing", "incoming")


def get_all_prefix_citations(citation_path):
    incoming = defaultdict(int)
    outgoing = defaultdict(int)

    print("Counting DOI prefixes in citations")
    chunk_idx = 0
    for chunk in pd.read_csv(citation_path, chunksize=chunksize, 
                             dtype={"citing": "str", "cited": "str", "creation": "str", "dblp_citing": "str", "dblp_cited": "str"}):
        chunk_idx += 1
        print("\t reading chuck", chunk_idx)
        for index, row in chunk.iterrows():
            citing_prefix = row["citing"].split("/")[0]
            outgoing[citing_prefix] += 1

            cited_prefix = row["cited"].split("/")[0]
            incoming[cited_prefix] += 1

    return incoming, outgoing


def process(citation_path, publisher_path, dblp_path, out_path):
    tmp_incoming_file = out_path + "_tmp_prefix_incoming.json"
    tmp_outgoing_file = out_path + "_tmp_prefix_outgoing.json"
    if exists(tmp_incoming_file):
        with open(tmp_incoming_file, encoding="utf-8") as f:
            incoming = load(f)
        with open(tmp_outgoing_file, encoding="utf-8") as f:
            outgoing = load(f)
    else:
        incoming, outgoing = get_all_prefix_citations(citation_path)
        with open(tmp_incoming_file, "w", encoding="utf-8") as f:
            dump(incoming, f, ensure_ascii=False)
        with open(tmp_outgoing_file, "w", encoding="utf-8") as f:
            dump(outgoing, f, ensure_ascii=False)

    publishers = pd.read_csv(publisher_path)
    dblp = pd.read_csv(dblp_path)
    publisher_groupby = publishers.groupby(["name"])
    publisher_keys = publisher_groupby.groups.keys()
    for key in publisher_keys:
        publisher_citations = defaultdict(int)
        publisher_citations["publisher"] = key

        print("Processing publisher:", key)
        for idx, prefix in publisher_groupby.get_group(key).prefix.iteritems():
            publisher_citations["incoming"] += incoming.get(prefix, 0)
            publisher_citations["outgoing"] += outgoing.get(prefix, 0)
            publisher_citations["n_entity"] += len(dblp[dblp.doi.str.startswith(prefix + "/", na=False)])
        
        store_csv_on_file(out_path, csv_headers, publisher_citations)
        

if __name__ == "__main__":
    arg_parser = ArgumentParser("Extract citations from COCI")
    arg_parser.add_argument("-i", "--input", required=True,
                            help="The input directory containing citations of interest.")
    arg_parser.add_argument("-p", "--publishers", required=True,
                            help="The CSV file with all the publishers.")
    arg_parser.add_argument("-d", "--dblp", required=True,
                            help="The CSV file with all DBLP articles.")
    arg_parser.add_argument("-o", "--output", required=True,
                            help="The output CSV file where to store citation information "
                                 "per publisher.")
    args = arg_parser.parse_args()

    print("Start process")
    process(args.input, args.publishers, args.dblp, args.output)
    print("Process finished")