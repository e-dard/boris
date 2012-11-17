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
    """ 
    Convert value associated with an element's tag to correct data type 
    """
    value = element.text
    if value is not None:
        value = TAG_TYPES.get(element.tag, unicode)(value)
    return (element.tag, value)

def _parse_feed(endpoint):
    """ Parses a web-feed and returns the root XML element """
    return etree.parse(endpoint).getroot()


class BikeChecker(object):
    """
    The BikeChecker object allows you to access Barclay's Bike 
    availabily.

    It maintains the most recent availabily data, so you don't need 
    to worry about refreshing the data source; simply use the methods 
    provided to access bike data and the :class:`boris.BikeChecker` 
    class will take care of whether to request new bike availabily data.

    :param url: optional web-service url. You _may_ need to change this
                if `TFL`_ change the endpoint in the future.

    .. _TFL: http://www.tfl.gov.uk/

    :returns: a list of dictionaries containing bike station data
    """

    def _process_stations(self, stations):
        self._stations_lst = [dict(_convert(e) for e in st) for st in stations] 

    def all(self, skip_cache=False):
        """
        Gets all available bike data.

        :param skip_cache: optional argument specifying whether to 
                           check the cache (default) or skip it and 
                           explicitly request fresh data.

        :returns: a list of dictionaries describing current status of 
                  bike stations
        """
        now = _time_ms(datetime.datetime.utcnow())
        if skip_cache or now - self._last_updated > CACHE_LIMIT:
            self._process_stations(_parse_feed(self.endpoint))
        return self._stations_lst

    def __init__(self, endpoint=None):
        self._last_updated = 0
        self._etree = None
        self._stations_lst = []
        self._stations_map = {}
        self.endpoint = endpoint or TFL_DATA_LOC
