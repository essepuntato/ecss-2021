from argparse import ArgumentParser
from requests import get
from os.path import exists
from csv import DictReader
from json import loads
from time import sleep
from extract_dblp_metadata import store_csv_on_file
from urllib.parse import quote


MAX_TRY = 5
SLEEPING_TIME = 5
csv_headers = (
    "id", "name", "prefix"
)
headers = {
    "User-Agent": 
    "OpenCitations "
    "(http://opencitations.net; mailto:contact@opencitations.net)",
    "Crossref-Plus-API-Token":
    "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vY3Jvc3NyZWYub3JnLyIsImF1ZCI6Im1kcGx1cyIsImp0aSI6IjAwNWZmZGRlLWI1ZTQtNDhlNC05ZDcxLWViOGVhNTk3ZTMyNiJ9.PqG8rxDXCY8JCXitX0j-i2LtozkRcrL_QUwVgqRnLuU"
}


def get_via_requests(get_url):
    tentative = 0
    print("")

    while tentative < MAX_TRY:
        tentative += 1

        try:
            print("Getting data from", get_url, "- tentative:", tentative)
            r = get(get_url, headers=headers, timeout=10)
            if r.status_code == 200:
                print("\tdata downloaded")
                r.encoding = "utf-8"

                return loads(r.text)
            elif r.status_code == 404:
                return None
            else:
                print("\tdata not downloaded, trying again in ", SLEEPING_TIME, "seconds - status:", r.status_code)
                sleep(SLEEPING_TIME)
        except Exception as e:
            print("\tdata not downloaded, trying again in ", SLEEPING_TIME, "seconds - exception:", e.message)
            sleep(SLEEPING_TIME)


def get_publishers(offset):
    get_url = "https://api.crossref.org/members?rows=1000&offset=" + str(offset)
    req = get_via_requests(get_url)
    
    if req is not None:
        r_json = req.get("message")
        if r_json is not None:
            offset += 1000
            print("\tnext offset is", offset)
            total_results = int(r_json.get("total-results"))
            items = r_json.get("items")

            return items, offset, total_results
                

def process(out_path):
    pub_ids = set()

    if exists(out_path):
        with open(out_path) as f:
            csv_reader = DictReader(f, csv_headers)
            for row in csv_reader:
                pub_ids.add(row["id"])

    # cursor = "*"
    offset = 0
    tot = 10000000000
    pub_count = 0
    while offset < tot:
        result, offset, tot = get_publishers(offset)

        if result is not None:
            for publisher in result:
                pub_count += 1
                cur_id = str(publisher["id"])
                if cur_id not in pub_ids:
                    pub_ids.add(cur_id)
                    cur_name = publisher["primary-name"]
                    prefixes = set()
                    for prefix in publisher["prefix"]:
                        prefix_value = prefix["value"]
                        if prefix_value not in prefixes:
                            prefixes.add(prefix_value)
                            store_csv_on_file(out_path, csv_headers, {
                                "id": cur_id, "name": cur_name, "prefix": prefix_value})
    
    if pub_count == tot:
        print("\n\nAll publishers correctly downloaded")
    else:
        print("\n\nOnly %s of the total %s publishers "
              "have been downloaded" % (pub_count, tot))
                    

if __name__ == "__main__":
    arg_parser = ArgumentParser("Extract publisher information from Crossref")
    arg_parser.add_argument("-o", "--output", required=True,
                            help="The output CSV file where to store relevant information.")
    args = arg_parser.parse_args()

    print("Start process")
    process(args.output)
    print("Process finished")