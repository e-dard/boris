import unittest
import datetime
from StringIO import StringIO

from lxml import etree
from mock import patch, Mock

import boris
from boris import BikeChecker



class TestBoris(unittest.TestCase):

    def test_time_ms(self):
        """ Tests boris._time_ms """
        dt = datetime.datetime(1970, 1, 1, 00, 30)
        self.assertEquals(boris._time_ms(dt), 30 * 60 * 1000)

    @patch.dict('boris.TAG_TYPES', {'foo': int, 'bar': float})
    def test_convert(self):
        """ Tests boris._convert """
        inputs = [Mock(tag='foo', text='22'), 
                  Mock(tag='bar', text='1.21'),
                  Mock(tag='zoo', text='hello')]
        expected = [('foo', 22), ('bar', 1.21), ('zoo', 'hello')]
        actual = [boris._convert(x) for x in inputs]
        self.assertEquals(expected, actual)


class TestBikeChecker(unittest.TestCase):

    def setUp(self):
        x = """
                <stations>
                    <station>
                        <id>8</id>
                        <name>Lodge Road, St. John's Wood</name>
                        <terminalName>003423</terminalName>
                        <lat>51.5</lat>
                        <long>-0.14</long>
                        <installed>true</installed>
                        <locked>false</locked>
                        <installDate>1278241920000</installDate>
                        <removalDate/>
                        <temporary>false</temporary>
                        <nbBikes>3</nbBikes>
                        <nbEmptyDocks>15</nbEmptyDocks>
                        <nbDocks>18</nbDocks>
                    </station>
                </stations>
            """
        self.bc = BikeChecker(endpoint=StringIO(x))

    def test_all_result(self):
        """ Tests boris.BikeChecker.all parses correct result """
        expected = [dict([('id', 8), ('name', u"Lodge Road, St. John's Wood"), 
                          ('terminalName', u'003423'), ('lat', 51.5), 
                          ('long', -0.14), ('installed', True), 
                          ('locked', False), 
                          ('installDate', 1278241920000), 
                          ('removalDate', None), ('temporary', False), 
                          ('nbBikes', 3), ('nbEmptyDocks', 15), 
                          ('nbDocks', 18)])] 
        self.assertEquals(expected, self.bc.all())

    @patch('boris.etree.parse', wraps=etree.parse)
    @patch('boris.datetime', wraps=datetime)
    def test_all_cache(self, dt_mock, etree_mock):
        """ Tests boris.BikeChecker.all respects the cache """
        now = dt_mock.datetime.utcnow
        now.return_value = datetime.datetime.utcfromtimestamp(0)
        # attribute error because etree will never be set.
        self.assertRaises(AttributeError, self.bc.all)
        self.assertFalse(etree_mock.called)

        # now we force an update
        self.bc.all(force=True)
        self.assertTrue(etree_mock.called)

        # reset the mock and exceed the cache
        etree_mock.reset_mock()
        now.return_value = datetime.datetime.\
                                        utcfromtimestamp(boris.CACHE_LIMIT + 1)
        self.bc.all()
        self.assertTrue(etree_mock.called)


if __name__ == '__main__':
    unittest.main()