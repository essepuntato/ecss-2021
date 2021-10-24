import lxml.etree as ET

ET.DTD(file="dblp.dtd")

counter = 0

for event, elem in ET.iterparse("dblp.xml", events=("end",), tag=("book", ), load_dtd=True):
    print("\n")
    print(ET.tostring(elem, pretty_print=True).decode("UTF-8"))
    elem.clear()
    if counter == 10:
        break
    counter += 1
print("Finished")

# I would search only for these types (tags): article|inproceedings|proceedings|book|incollection

# in all: '@key' contains url of the object, 'year' the year of publication, and 'title' the title of the work. All titles finish with a "."

# in "inproceedings" and "incollection", 'crossref' contains id of conference/container

# in "journal", no 'crossref' found, it is necessary to derive the value from 'url' that have, usually, the following form: "/db/<type>/<name>/.+", e.g. "db/journals/www/...".

# in "book" and "proceeding" there is no container

# table to create
# doi, dblp_id, title, year, dblp_venue_id, additional_dois

# BE AWARE: before storing DOIs, normalise them! See code developed in opencitations/index, see:
# def normalise(self, id_string, include_prefix=False):
#     try:
#         doi_string = sub("\0+", "", sub("\s+", "", unquote(id_string[id_string.index("10."):])))
#         return "%s%s" % (self.p if include_prefix else "", doi_string.lower().strip())
#     except:  # Any error in processing the DOI will return None
#         return None

# to store line by line in a CSV (so as to avoid processing same data twice) see:
# @staticmethod
# def __store_csv_on_file(f_path, header, json_obj):
#     f_exists = exists(f_path)
#     with open(f_path, "a", encoding="utf8") as f:
#         dw = DictWriter(f, header)
#         if not f_exists:
#             dw.writeheader()
#         dw.writerow(json_obj)