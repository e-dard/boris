import datetime

from lxml import etree

# Configuration variables
TFL_DATA_LOC = "http://www.tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
CACHE_LIMIT = 180 * 1000

# dictionary for typing the web-service data
boolean = lambda x: x.lower() == "true"
TAG_TYPES = {
                'id': int, 
                'name': unicode, 
                'terminalName': unicode, 
                'lat': float, 
                'long': float,
                'installed': boolean,
                'locked': boolean,
                'installDate': long,
                'removalDate': long,
                'temporary': boolean,
                'nbBikes': int,
                'nbEmptyDocks': int,
                'nbDocks': int
            }

def _time_ms(dt):
    """ Convert datetime into milliseconds since the epoch """
    epoch = datetime.datetime.utcfromtimestamp(0)
    diff = dt - epoch
    return diff.total_seconds() * 1000

def _convert(element):
    """ Convert value associated with an element's tag to right type """
    value = element.text
    if value is not None:
        value = TAG_TYPES.get(element.tag, unicode)(value)
    return (element.tag, value)


class BikeChecker(object):
    """
    The BikeChecker object allows you to access Barclay's Bike 
    availabily.

    It maintains of the most recent availabily data, so you don't need 
    to worry about refreshing the data source; simply use the methods 
    provided to access bike data and the :class:`boris.BikeChecker` 
    class will take care of whether to request new bike availabily data.

    :param url: optional web-service url. You _may_ need to change this
    if `TFL`_ change the endpoint in the future.
    :type url: `basestring`

    .. _TFL: http://www.tfl.gov.uk/
    """
    def all(self, force=False):
        """
        Gets all available bike data.

        :param force: if set to True will ignore cache and request 
        fresh data.
        :type force: boolean

        :returns: a list of dictionaries describing current status of 
        bike stations
        """
        now = _time_ms(datetime.datetime.utcnow())
        if force or now - self.last_updated > CACHE_LIMIT:
            self.etree = etree.parse(self.url)
        return [dict(_convert(e) for e in st) for st in self.etree.getroot()] 

    def __init__(self, url=None):
        self.url = TFL_DATA_LOC
        self.last_updated = 0
        self.etree = None
        if url:
            self.url = url
