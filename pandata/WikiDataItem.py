class WikiDataItem(object):
    def __init__(self, id, title, claims):
        self.claims = claims
        self.id = id
        self.title = title