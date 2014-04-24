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
