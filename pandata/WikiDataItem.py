class WikiDataItem(object):
    def __init__(self, id, title, claims):
        self.claims = claims
        self.id = id
        self.title = title

    @classmethod
    def parse(cls, data):
        title = data["title"]
        if "id" in data:
            id = data["id"]
        else:
            # Item has been deleted
            id = None
        claims = {}
        if "claims" in data:
            for property, claimJSON in data["claims"].iteritems():
                datavalue = claimJSON[0]["mainsnak"]["datavalue"]
                if "type" in datavalue and datavalue["type"] == "wikibase-entityid":
                    value = "Q" + unicode(datavalue["value"]["numeric-id"])
                else:
                    value = datavalue["value"]
                claims[property] = value
        return cls(id, title, claims)
