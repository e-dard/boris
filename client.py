import datetime
import argparse
import re

import boris

POSTCODE_REGEX = re.compile("[a-z]{1,2}[0-9r][0-9a-z]?[0-9][a-z]{2}")
bc = boris.BikeChecker()

def get_bikes(search):
    res = None
    # decipher input.
    try:
        nums = [float(x) for x in search]
    except ValueError:
        # try for postcode
        as_postcode = ''.join(search).lower()
        if POSTCODE_REGEX.match(as_postcode):
            res = bc.find_with_postcode(as_postcode)
        else:
            # search by name
            res = bc.get(' '.join(search), fuzzy_matches=1)
    else: 
        # lat / lng match
        if len(nums) == 2:
            try:
                res = bc.find_with_geo(nums[0], nums[1])
            except boris.IllegalPointException:
                print "Sorry, (%s, %s) doesn't seem like a valid point" % nums
        else:
            print "Wrong number of arguments (%d) for a geo point." % len(nums)
    return res   

def _plural(num, string='s'):
    return string[num==1:]

def _distance_as_string(dist):
    if dist < 1:
        metres = int(dist * 100) * 10
        return "%d metre%s" % (metres, _plural(metres))
    else:
        return "%s km" % "{0:.1f}".format(dist)

def display_bikes(results, updated):
    diff = datetime.datetime.utcnow() - updated
    seconds_diff = diff.seconds
    days_diff = diff.days
    time_str = "\nAvailability data last updated "
    if days_diff == 0:
        if seconds_diff > 3600:
            time_str += "over an hour ago."
        elif seconds_diff > 60:
            time_str += "%d minutes ago." % (seconds_diff / 60)
        elif seconds_diff > 10:
            time_str += "%d seconds ago." % seconds_diff 
        else:
            time_str += "just now."
    else:
        time_str += " %d day%s ago" % (days_diff, _plural(days_diff))
    
    result = time_str
    if isinstance(results, dict):
        results = [results]
    for station in results:
        st = station
        dist = None
        if 'distance' in station: 
            st = station['station']
            dist = station['distance']

        details = [st['name']]
        if dist is not None:
            details.append(" (distance: %s)" % _distance_as_string(dist))
        details.append("\n\tBikes available: %d" % st['nbBikes'])
        result = '%s\n\n%s\n' % (result, ''.join(details))
    return result




if __name__ == '__main__':
    msg = 'Easily lookup current Barclays Bike availability by name, '\
          'postcode or geographical position.'
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('search', metavar='string', type=unicode, nargs='+',
               help='the search term (postcode, station name or lat,lng point')

    parser.add_argument('--fuzzy', metavar='fuzzy matches', type=int,
               help='the number of fuzzy matches')

    args = parser.parse_args()
    bikes = get_bikes(args.search)
    print display_bikes(bikes, bc.last_updated)

