# -*- coding: utf-8 -*-
# Copyright (c) 2021, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

# This script is responsible for extracting citations involving
# any DOI included in the DBLP dump. The citations come from 
# a COCI dump. Each COCI dump is a huge ZIP archive composed by
# other ZIP archives, each containing new citation data added
# in the various release of COCI. It is important to unzip the
# initial big archive in one directory, which will contain all the
# other ZIP archives of each COCI release.
import pandas as pd
from argparse import ArgumentParser
from zipfile import ZipFile
from glob import glob
from os import sep
from extract_dblp_metadata import store_csv_on_file

chunksize = 10 ** 4
csv_headers = (
    "citing", "cited", "creation", "dblp_citing", "dblp_cited"
)


def get_all_dois(dblp_path):
    result = set()

    for chunk in pd.read_csv(dblp_path, chunksize=chunksize):
        result.update(set(chunk.doi.dropna().unique()))
        for idx, value in chunk.additional_dois.dropna().iteritems():
            for doi in value.split(" "):
                result.add(doi)

    return result


def process(dir_path, dblp_path, out_path):
    print("Retrieving all DOIs in DBLP")
    dois = get_all_dois(dblp_path)
    
    print("Extracting relevant citations from COCI")
    for zip_path in glob(dir_path + sep + "*.zip"):
        print("\tProcessing ZIP archive", zip_path)
        with ZipFile(zip_path) as zip_file:
            for inner_file in zip_file.infolist():
                inner_filename = inner_file.filename
                if inner_filename.endswith(".csv"):
                    print("\t\tProcessing CSV file", inner_filename)
                    with zip_file.open(inner_filename) as f:
                        for chunk in pd.read_csv(f, chunksize=chunksize):
                            chunk.fillna("", inplace=True) 
                            for idx, row in chunk.iterrows():
                                citing = row["citing"]
                                dblp_citing = citing in dois
                                cited = row["cited"]
                                dblp_cited = cited in dois

                                if dblp_citing or dblp_cited:
                                    cur_citation = {
                                        "citing": row["citing"],
                                        "cited": row["cited"],
                                        "creation": row["creation"],
                                        "dblp_citing": "yes" if dblp_citing else "no",
                                        "dblp_cited": "yes" if dblp_cited else "no"
                                    }
                                    store_csv_on_file(out_path, csv_headers, cur_citation)
        

if __name__ == "__main__":
    arg_parser = ArgumentParser("Extract citations from COCI")
    arg_parser.add_argument("-i", "--input", required=True,
                            help="The input directory containing COCI dump files.")
    arg_parser.add_argument("-d", "--dblp", required=True,
                            help="The CSV file with DBLP relevant information.")
    arg_parser.add_argument("-o", "--output", required=True,
                            help="The output CSV file where to store relevant citations.")
    args = arg_parser.parse_args()

    print("Start process")
    process(args.input, args.dblp, args.output)
    print("Process finished")