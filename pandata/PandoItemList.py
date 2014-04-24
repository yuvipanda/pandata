from WikiDataItem import WikiDataItem


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

    def get_wikidata_items(self, mwapi):
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