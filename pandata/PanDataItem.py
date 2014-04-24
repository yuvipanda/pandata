from WikiDataItem import WikiDataItem
from PandoItem import PandoItem


class PanDataItem(object):
    def __init__(self, wikidata_item, pando_item):
        self.wikidata_item = wikidata_item
        self.pando_item = pando_item


class PanDataItemList(object):
    def __init__(self, items):
        self.items = items

    def get_missing_wikidata(self):
        for item in self.items:
            if item.wikidata_item == None:
                yield item

    @classmethod
    def from_pando_items(cls, pando_items, mwapi):
        enwiki_titles = {}
        for pi in pando_items.items:
            enwiki_titles[pi.enwiki_title] = pi
        resp = mwapi.get(
            action="wbgetentities",
            sites="enwiki",
            titles="|".join(enwiki_titles.keys()),
            props="info|claims|sitelinks"
        )
        itemsJSON = resp["entities"].values()
        items = []

        for itemJSON in itemsJSON:
            wd_item = WikiDataItem.parse(itemJSON)
            pd_item = enwiki_titles[wd_item.title]
            items.append(PanDataItem(wd_item, pd_item))

        return items

    @classmethod
    def from_pando_query(cls, query, mwapi):
        items = []

        cur_items = query.get_next_page()
        while not cur_items.is_empty():
            items.extend(cls.from_pando_items(cur_items, mwapi))
            print "Done for %d" % len(items)
            cur_items = query.get_next_page()
            break

        return cls(items)
