from WikiDataItem import WikiDataItem


class PandoItemList(object):
    def __init__(self, items):
        self.items = items

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

        for itemJSON in itemsJSON:
            yield WikiDataItem.parse(itemJSON)