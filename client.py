import argparse
import re

import boris

POSTCODE_REGEX = re.compile("[a-z]{1,2}[0-9r][0-9a-z]?[0-9][a-z]{2}")

def get_bikes(search):
    bc = boris.BikeChecker()
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


if __name__ == '__main__':
    msg = 'Easily lookup current Barclays Bike availability by name, '\
          'postcode or geographical position.'
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('search', metavar='string', type=unicode, nargs='+',
               help='the search term (postcode, station name or lat,lng point')

    parser.add_argument('--fuzzy', metavar='fuzzy matches', type=int,
               help='the number of fuzzy matches')

    args = parser.parse_args()
    print get_bikes(args.search)

