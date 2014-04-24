#!/bin/bash
import json

from mwapi import MWApi
from PandoQuery import PandoQuery
from PanDataItem import *

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

pd_items = PanDataItemList.from_pando_query(query, mwapi)

print list(pd_items.get_missing_wikidata())

