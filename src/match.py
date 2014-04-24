#!/bin/bash
import json

import pandora_client as pandora
from mwapi import MWApi


class PandoItem(object):
    def __init__(self, id, enwiki_title):
        self.id = id
        self.enwiki_title = enwiki_title

class PandoItemList(object):
    def __init__(self, items):
        self.items = items
        self.items_missing_wikidata = []

    def get_one_item(self, filter):
        for item in self.items:
            if filter(item):
                return item
        return None

    def is_empty(self):
        return len(self.items) == 0

    def get_wikidata_items(self):
        enwiki_titles = []
        for pi in self.items:
            enwiki_titles.append(pi.enwiki_title)
        resp = mwapi.get(
            action="wbgetentities",
            sites="enwiki",
            titles="|".join(enwiki_titles),
            props="info|claims"
        )
        itemsJSON = resp["entities"].values()

        for item in itemsJSON:
            title = item["title"]
            if "id" in item:
                id = item["id"]
            else:
                # Item has been deleted
                id = None
                self.items_missing_wikidata.append(
                    self.get_one_item(lambda pi: pi.enwiki_title == item["title"])
                )
            claims = {}
            if "claims" in item:
                for property, claimJSON in item["claims"].iteritems():
                    datavalue = claimJSON[0]["mainsnak"]["datavalue"]
                    if "type" in datavalue and datavalue["type"] == "wikibase-entityid":
                        value = "Q" + unicode(datavalue["value"]["numeric-id"])
                    else:
                        value = datavalue["value"]
                    claims[property] = value

            yield WikiDataItem(id, title, claims)


class PandoQuery(object):
    def __init__(self, conditions, operator="&", items_per_page=50):
        self._query = {
            'conditions': conditions,
            'operator': operator
        }
        self._items_per_page = items_per_page
        self._start_item_number = 0
        self._api = pandora.API("https://indiancine.ma/api")

    def get_next_page(self):
        resp = self._api.find(
            query=self._query,
            keys=["links", "id"],
            range=[self._start_item_number, self._start_item_number + self._items_per_page]
        )
        itemsJSON = resp["data"]["items"]
        items = []
        for itemJSON in itemsJSON:
            items.append(PandoItem(
                itemJSON["id"],
                itemJSON["links"][0].replace("http://en.wikipedia.org/wiki/", "")
            ))

        self._start_item_number += self._items_per_page

        return PandoItemList(items)


missing_titles = []

mwapi = MWApi("https://www.wikidata.org")

class WikiDataItem(object):
    def __init__(self, id, title, claims):
        self.claims = claims
        self.id = id
        self.title = title


class WikiDataProperty(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title


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
    wds.extend(pando_items.get_wikidata_items())
    missing_ids.extend([pi.id for pi in pando_items.items_missing_wikidata])
    print "Done for %d, missing %d" % (len(wds), len(missing_titles))
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
