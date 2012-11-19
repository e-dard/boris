# -- coding: utf-8 --
import datetime
import difflib
from math import sin, cos, atan2, sqrt, radians

from lxml import etree
from postcodes import PostCoder

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

def _is_geo_valid(lat, lng):
    """ Checks if geographical point valid """
    if abs(lat) > 90 or abs(lng) > 180:
        return False
    return True

def _haversine(first, second):
    """
    Calculate the `haversine`_ distance between two points on a sphere.

    .. _haversine: http://en.wikipedia.org/wiki/Haversine_formula

    :param first: the first (latitude, longitude) tuple specified in 
                  decimal degrees.

    :param second: the second (latitude, longitude) tuple specified in 
                   decimal degrees.
    
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
    """
    for point in (first, second):
        if not _is_geo_valid(*point):
            msg = "(%s, %s) is not a valid decimal lat/lng" % point
            raise IllegalPointException(msg)

    lat_1 = radians(first[0])
    lat_2 = radians(second[0])
    d_lat = radians(second[0] - first[0])
    d_lng = radians(second[1] - first[1])
    R = 6371.0
    a = pow(sin(d_lat / 2.0), 2) + cos(lat_1) * cos(lat_2) * \
        pow(sin(d_lng / 2.0), 2)
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

    def __init__(self, endpoint=None):
        self.pc = PostCoder()
        self._last_updated = 0
        self._etree = None
        self._stations_lst = []
        self._stations_map = {}
        self.endpoint = endpoint or TFL_DATA_LOC

    def _process_stations(self):
        stations = _parse_feed(self.endpoint)
        self._last_updated = long(stations.get("lastUpdate"))
        self._stations_lst = [dict(_convert(e) for e in st) for st in stations] 
        if not self._stations_lst:
            raise InvalidDataException("No Station data available")
        for station in self._stations_lst:
            self._stations_map[station['name'].lower()] = station

    @property
    def last_updated(self):
        if self._last_updated:
            return datetime.datetime.fromtimestamp(self._last_updated / 1000)

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
            self._process_stations()
        return self._stations_lst

    def get(self, name, fuzzy_matches=0, skip_cache=False):
        """
        Availability information for the station(s) matching `name`.

        `get` allows fuzzy matching of stations based on their name, and 
        returns up to `fuzzy_matches` stations; a station's inclusion 
        is dependent on how close its name is to `name`, based on the 
        result of the `Ratcliff/Obershelp`_ algorithm.

        .. _Ratcliff/Obershelp: http://xlinux.nist.gov/dads/HTML/ratcliffObershelp.html

        :param name: the name of the bike station

        :param fuzzy_matches: optional argument specifying how many 
                              fuzzy matches to return. By default 
                              `fuzzy_matches` is 0 and so `get` will 
                              return an empty list if `name` does not 
                              exactly match a station name.

        :param skip_cache: optional argument specifying whether to 
                           check the cache (default) or skip it and 
                           explicitly request fresh data.

        :returns: a list of station availability data ordered by how 
                  closely the station name matches `name`.
        """
        now = _time_ms(datetime.datetime.utcnow())
        if skip_cache or now - self._last_updated > CACHE_LIMIT:
            self._process_stations()

        name = name.strip().lower()
        station = self._stations_map.get(name, None)
        if station is None:
            if not fuzzy_matches:
                return []
            names = self._stations_map.keys()
            matches = difflib.get_close_matches(name, names, n=fuzzy_matches, 
                                                cutoff=0)
            if matches:
                return [self._stations_map[x] for x in matches]
        else:
            return [station]

    def find_with_geo(self, lat, lng, predicate=None, skip_cache=False):
        """
        Availability information for the nearest station to 
        (`lat`, `lng`). Using `predicate` you can ensure that any 
        returned stations also satisfy certain properties.

        For example, ensuring there are at least five bikes available:

        >>> bc = BikeChecker()
        >>> bike_predicate = lambda x: x['nbBikes'] >= 4 
        >>> bc.find_with_geo(51.49, -0.19, predicate=bike_predicate)
        >>> # results here.

        :param lat: latidude of position

        :param lng: longitude of position

        :parma predicate: optional argument specifying a predicate 
                          which must be satisfied by any station 
                          returned.

        :param skip_cache: optional argument specifying whether to 
                           check the cache (default) or skip it and 
                           explicitly request fresh data.

        :returns: a `dict` containing an availability `dict` for the 
                  nearest station, as well as the distance to that 
                  station in kilometres. If no stations satisfy 
                  `predicate`, and empty `dict` is returned.
        """
        now = _time_ms(datetime.datetime.utcnow())
        if skip_cache or now - self._last_updated > CACHE_LIMIT:
            self._process_stations()

        if predicate is None: 
            predicate = lambda x: True
        if not self._stations_lst: 
            self._process_stations()

        near, near_dist = None, None
        for station in self._stations_lst:
            st_geo = (station['lat'], station['long'])
            station_dist = _haversine((lat, lng), st_geo)
            if predicate(station) and \
               (not near_dist or station_dist < near_dist):
                near, near_dist = station, station_dist
        return {'station': near, 'distance': near_dist} if near else {}

    def find_with_postcode(self, postcode, predicate=None, skip_cache=False):
        """ 
        Availability information for the nearest station to `postcode`.

        Using `predicate` you can ensure that any returned stations 
        also satisfy certain properties, for example that they have a 
        certain number of bikes available.

        :param postcode: the postcode to search

        :parma predicate: optional argument specifying a predicate 
                          which must be satisfied by any station 
                          returned.

        :param skip_cache: optional argument specifying whether to 
                           check the cache (default) or skip it and 
                           explicitly request fresh data.

        :returns: a `dict` containing an availability `dict` for the 
                  nearest station, as well as  the distance to that 
                  station in kilometres. If no stations satisfy 
                  `predicate`, and empty `dict` is returned.
        """
        now = _time_ms(datetime.datetime.utcnow())
        if skip_cache or now - self._last_updated > CACHE_LIMIT:
            self._process_stations()

        info = self.pc.get(postcode)
        if not info:
            raise InvalidPostcodeException("No known postcode %s" % postcode)
        if 'geo' not in info or not set(['lat', 'lng']) <= set(info['geo']):
            raise InvalidDataException("Missing latitude and/or longitude")
        lat, lng = float(info['geo']['lat']), float(info['geo']['lng'])
        return self.find_with_geo(lat, lng, predicate=predicate)

class IllegalPointException(Exception): pass
class StationDataException(Exception): pass
class InvalidDataException(Exception): pass
class InvalidPostcodeException(Exception): pass
        
