#!/bin/bash
import pandora_client as pandora
from mwapi import MWApi

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_pando_links():
    api = pandora.API("https://indiancine.ma/api")
    resp = api.find(
        query={
            'conditions': [
                {
                    'key': 'list',
                    'value': 'j:Wikipedia',
                    'operator': ''
                }
            ],
            'operator': '&'
        },
        keys=['links'],
        range=[0, 5000]
    )
    items = resp["data"]["items"]
    for item in items:
        yield item["links"][0].replace("http://en.wikipedia.org/wiki/", "")

missing_titles = []

mwapi = MWApi("https://www.wikidata.org")
def claims_for_titles(titles, wiki="enwiki"):
    resp = mwapi.get(
        action="wbgetentities",
        sites=wiki,
        titles="|".join(titles),
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

title_chunks = chunks(list(get_pando_links()), 100)
wds = []
for title_chunk in title_chunks:
    wds.extend(claims_for_titles(title_chunk))
    print "Done for %d, missing %d" % (len(wds), len(missing_titles))

for wd in wds:
    for prop in wd.claims:
        properties_count[prop] = properties_count.get(prop, 0) + 1

print properties_count
print missing_titles
