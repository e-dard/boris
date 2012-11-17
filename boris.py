# -- coding: utf-8 --
import datetime
from math import sin, cos, atan2, sqrt, radians
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

def _haversine(first, second):
    """
    Calculate the `haversine`_ distance between two points on a sphere.

    :param first: the first (latitude, longitude) tuple.

    :param second: the second (latitude, longitude) tuple.
    
    Forumula is as follows:

    a = sin²(Δφ/2) + cos(φ1).cos(φ2).sin²(Δλ/2)
    c = 2.atan2(√a, √(1−a))
    d = R.c

    where:

    φ1 - latitude of the first point.
    φ2 - latitude of the second point.
    Δφ - latitude delta.
    Δλ - longitude delta.
    R - is the Earth's radius in km (we will use 6371 km)

    :returns: the distance in km between two points.

    .. _haversine: http://en.wikipedia.org/wiki/Haversine_formula
    """
    lat_1 = radians(first[0])
    lat_2 = radians(second[0])
    d_lat = radians(second[0] - first[0])
    d_lng = radians(second[1] - first[1])
    R = 6371.0
    a = pow(sin(d_lat / 2.0), 2) + cos(lat_1) * \
        cos(lat_2) * pow(sin(d_lng / 2.0), 2)
    c = 2.0 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


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
