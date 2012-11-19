# Boris

You'll find more detailed documentation [over here](http://boris.readthedocs.org/en/latest/).

Boris is a Python client library for the Barclays Bike availability web-service provided by Transport For London.

Using Boris you can get real-time availability of barclays bikes at all station across London. Unlike some other thin-wrappers over the 
tfl data, Boris also allows you to:

 - do a fuzzy search on bike station name;
 - search for the nearest bike station to any UK  postcode (via the postcodes library);
 - search for the nearest bike station to any geographical point;
 - apply arbitrary filter functions to two previous abilities (so you can, for example, get the nearest bike station with 3 bikes available); and
 - provides a caching layer over the tfl web-service.

 Nearest stations are calculated using the [Haversine](http://en.wikipedia.org/wiki/Haversine_formula) formula (which calculates the 
 shortest distance between two points on a sphere). Therefore, the distances calculated are probably shorter than the actual walking 
 distance, due to pesky things like buildings and hills, but all things considered, the nearest station is *probably* also the nearest station 
 in terms of walking.

#### NOTE
In order to use the Boris library, the machine the Python process is running on must have had its IP address registered to use the 
Barclays Cycle Hire availability feed with the TFL in its [Developer Area](http://www.tfl.gov.uk/businessandpartners/syndication/16492.aspx).

## Installation

If you use pip then installation is simply:

    $ pip install boris

or, if you want the latest github version:

    $ pip install git+git://github.com/e-dard/boris.git

You can also install Postcodes via Easy Install:

    $ easy_install boris

## Using Boris

The easiest way to use Boris is to use the `BikeChecker` object, which provides some caching and input validation, over the TFL's 
web-service.

For any request using the Boris library, bike station data is returned as native Python objects. Bike station data is either  returned in 
isolation, or in the case of geographical and postcode related searches, along with some distance information to the point of interest. Of 
course, you can also use the library to pull all available bike station data, using the BikeChecker's `all` method. Here are some more 
useful ways to use the library.

### Fuzzy matching of Barclays Bike Station

A BikeChecker's `get` method allows you to do a direct lookup of bike station data using its name.

``` python
>>> from boris import BikeChecker
>>> from pprint import PrettyPrinter
>>> bc = BikeChecker()
>>> pp = PrettyPrinter()
>>> pp.pprint(bc.get("Alderney Street, Pimlico"))
[{'id': 185,
  'installDate': 1279365360000L,
  'installed': True,
  'lat': 51.48805753,
  'locked': False,
  'long': -0.140741432,
  'name': u'Alderney Street, Pimlico',
  'nbBikes': 13,
  'nbDocks': 14,
  'nbEmptyDocks': 1,
  'removalDate': None,
  'temporary': False,
  'terminalName': u'001174'}]
>>> 
```

However, names are a bit fiddly to remember, so Boris employs some fuzzy matching. The `get` method allows you to provide an 
optional number of close stations to return if there is no exact match:

``` python
>>> ...
>>> bikes = bc.get("westminster", fuzzy_matches=5)
>>> matching_names = [station['name'] for station in bikes]
>>> pp.pprint(matching_names)
[u'Smith Square, Westminster',
 u'Howick Place, Westminster',
 u'Butler Place, Westminster',
 u'Rochester Row, Westminster',
 u'Vincent Square, Westminster']
 >>>
 ```

 ### Nearest Bike Stations

Using either the `find_with_postcode`, or the `find_with_geo` methods you can get the station information associated with station nearest. 
Not only that, but you can specify that the nearest station must satisfy arbitrary *predicates*.

For example, let's get the current station information near us:

```python
>>> ...
>>> nearest = bc.find_with_postcode("EC2A 1AD")
>>> pp.pprint(nearest)
{'distance': 0.13012545345491472,
 'station': {'id': 140,
             'installDate': 1279205580000L,
             'installed': True,
             'lat': 51.52096262,
             'locked': False,
             'long': -0.085634242,
             'name': u'Finsbury Square , Moorgate',
             'nbBikes': 1,
             'nbDocks': 33,
             'nbEmptyDocks': 32,
             'removalDate': None,
             'temporary': False,
             'terminalName': u'001056'}}
>>> 
```

When either `find_with_postcode`, or the `find_with_geo` are called, the station dictionary is wrapped in a further dictionary that also 
provides distance information, using the `distance` key. **All distances are represented in kilometres**.

OK, but suppose we need to know the nearest bike station with at least 3 bikes currently available. No problem:

```python
>>> ...
>>> min_bikes_predicate = lambda x: x['nbBikes'] >= 3
>>> nearest = bc.find_with_postcode("EC2A 1AD", predicate=min_bikes_predicate)
>>> pp.pprint(nearest)
{'distance': 0.16879147599046088,
 'station': {'id': 331,
             'installDate': 1280141460000L,
             'installed': True,
             'lat': 51.52085887,
             'locked': False,
             'long': -0.089887855,
             'name': u'Bunhill Row, Moorgate',
             'nbBikes': 5,
             'nbDocks': 30,
             'nbEmptyDocks': 24,
             'removalDate': None,
             'temporary': True,
             'terminalName': u'001211'}}
>>>

Both the `find_with_postcode` and `find_with_geo` accept functions as optional arguments.

## Boris Client


© 2012, [Edward Robinson](http://twitter.com/eddrobinson)
