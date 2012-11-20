# Boris

Boris is a Python library that leverages the [Barclays Bike](http://www.tfl.gov.uk/roadusers/cycling/14808.aspx) availability [web-service](http://www.tfl.gov.uk/businessandpartners/syndication/16493.aspx), provided by Transport For London.

Using Boris you can get (almost) real-time bike availability at all Barclays Bike stations across London, as well as associated data. Unlike some other thin-wrappers over the TFL data, Boris also allows you to:

 - do a fuzzy search on bike station name;
 - search for the nearest bike station to any UK  postcode (via the [postcodes](https://github.com/e-dard/postcodes) library);
 - search for the nearest bike station to any geographical point;
 - apply arbitrary predicates to the two previous abilities (so you can, for example, get the nearest bike station with 3 bikes available); and
 - provides a caching layer over the TFL web-service.

 Nearest stations are calculated using the [Haversine](http://en.wikipedia.org/wiki/Haversine_formula) formula (which calculates the 
 shortest distance between two points on a sphere). Therefore, the distances calculated are probably shorter than the actual walking 
 distance, due to pesky things like buildings and hills, but all things considered, the nearest station is *probably* also the nearest station 
 in terms of walking.

#### NOTE

---

The Boris library utilises the official TFL Bike availability syndication feed, and from my *limited* testing I've found that the web-service 
is publicly accessible, however, this may not always be the case. So, it might be an idea to register the IP address associated with the 
machine running this library, in the TFL's [Developer Area](http://www.tfl.gov.uk/businessandpartners/syndication/16492.aspx). The specific 
feed used by Boris is the Barclays Cycle Hire availability feed. This process is pretty simple and you will usually just be emailed confirmation 
you have access.

---

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

For example, let's get the current station information for the bike station nearest `EC2A 1AD`:

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

When either `find_with_postcode` or the `find_with_geo` are called, the station dictionary is wrapped in a further dictionary that also 
provides distance information (accessed using the `distance` key). **All distances are represented in kilometres**.

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
```
Both the `find_with_postcode` and `find_with_geo` accept functions as optional arguments.

## The Boris Client

Included in the library is a simple client, which is suitable for use on the command line, and shows off a basic implementation on top of the 
Boris library.

```
$ python -m boris.client -h   
usage: client.py [-h] [--fuzzy fuzzy] [--min min_bikes] string [string ...]

Easily lookup current Barclays Bike availability by name, postcode or
geographical position.

positional arguments:
  string           the search term (postcode, station name or lat, lng point)

optional arguments:
  -h, --help       show this help message and exit
  --fuzzy fuzzy    the number of fuzzy matches
  --min min_bikes  for geo/postcode based queries, only show stations with
                   minimum available bikes
```

### Simple Usage

Search by name for bike availability:

```bash
$ python -m boris.client soho
Availability data last updated 2 minutes ago.

Moor Street, Soho
  Bikes available: 4
```

Optionally specify the number of fuzzy matches:

```bash
$ python -m boris.client --fuzzy 4 camden town

Availability data last updated 1 minutes ago.

Parkway, Camden Town
  Bikes available: 27


Bonny Street, Camden Town
  Bikes available: 24


Greenland Road, Camden Town
  Bikes available: 26


Arlington Road, Camden Town
  Bikes available: 1
  ```

Search based on location (postcode or latitude, longitude pair), optionally adding  the minimum number of bikes required. Distances to the 
station are provided:

```bash
$ python -m boris.client W1F 8PZ

Availability data last updated 1 minutes ago.

Great Marlborough Street, Soho (distance: 70 metres)
  Bikes available: 0
```

with minimum bike requirement:

```bash
$ python -m boris.client --min 1 W1F 8PZ

Availability data last updated 1 minutes ago.

Charles II Street, West End (distance: 750 metres)
  Bikes available: 5
  ```

  and finally using coordinates (note there is *no* comma between latitude and longitude:

  ```bash
$ python -m boris.client 51.506 -0.168 

Availability data last updated 35 seconds ago.

Triangle Car Park, Hyde Park (distance: 160 metres)
  Bikes available: 8
  ```


© 2012, [Edward Robinson](http://twitter.com/eddrobinson)
