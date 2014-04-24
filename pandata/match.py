#!/bin/bash
import json

from mwapi import MWApi
from PandoQuery import PandoQuery


missing_titles = []

mwapi = MWApi("https://www.wikidata.org")


def get_property(id):
    resp = mwapi.get(
        action="wbgetentities",
        ids=id,
        props="labels",
        languages="en"
    )
    return resp["entities"].values()[0]["labels"]["en"]["value"]

properties_count = {}

query = PandoQuery([
    {"key": "list", "value": "j:Wikipedia"}
])
wds = []
missing_ids = []

pando_items = query.get_next_page()
while not pando_items.is_empty():
    wds.extend(pando_items.get_wikidata_items(mwapi))
    missing_ids.extend([pi.id for pi in pando_items.items_missing_wikidata])
    print "Done for %d, missing %d" % (len(wds), len(missing_ids))
    pando_items = query.get_next_page()
    break

for wd in wds:
    for prop in wd.claims:
        properties_count[prop] = properties_count.get(prop, 0) + 1

open("missing_ids.json", "w").write(json.dumps(missing_ids))
properties_json = sorted(
    [(get_property(id), count) for id, count in properties_count.iteritems()],
    key=lambda p: -p[1]
)
open("properties.json", "w").write(json.dumps(properties_json))

