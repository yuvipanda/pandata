import pandora_client as pandora
from PandoItem import PandoItem
from PandoItemList import PandoItemList


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