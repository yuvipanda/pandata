#!/bin/bash
import pandora_client as pandora
from mwapi import MWApi


class PandoItem(object):
    def __init__(self, id, enwiki_title):
        self.id = id
        self.enwiki_title = enwiki_title


class PandoQuery(object):
    def __init__(self, conditions, operator="&", items_per_page=100):
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

        return items

missing_titles = []

mwapi = MWApi("https://www.wikidata.org")
def claims_for_pando_items(pando_items, wiki="enwiki"):
    enwiki_titles = []
    for pi in pando_items:
        enwiki_titles.append(pi.enwiki_title)
    resp = mwapi.get(
        action="wbgetentities",
        sites=wiki,
        titles="|".join(enwiki_titles),
        props="info|claims"
    )
    items = resp["entities"].values()

    for item in items:
        title = item["title"]
        if "id" in item:
            id = item["id"]
        else:
            # Item has been deleted
            id = None
            missing_titles.append(item["title"])
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


class WikiDataItem(object):
    def __init__(self, id, title, claims):
        self.claims = claims
        self.id = id
        self.title = title

properties_count = {}

query = PandoQuery([
    {"key": "list", "value": "j:Wikipedia"}
])
wds = []

pando_items = query.get_next_page()
while len(pando_items):
    claims_for_pando_items(pando_items)
    wds.extend(claims_for_pando_items(pando_items))
    print "Done for %d, missing %d" % (len(wds), len(missing_titles))
    pando_items = query.get_next_page()

for wd in wds:
    for prop in wd.claims:
        properties_count[prop] = properties_count.get(prop, 0) + 1

print properties_count
print missing_titles
