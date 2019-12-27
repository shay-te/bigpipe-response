import unittest

from bigpipe_response.dependencies_marshalling import DependenciesMarshalling


class TestDependenciesMarshalling(unittest.TestCase):
    def setUp(self):
        self.dep_mar = DependenciesMarshalling()

    def test_unmarshall_string(self):
        result = self.dep_mar.unmarshall('@s_tr')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], None)
        self.assertEqual(result['source'], 's_tr')

        result = self.dep_mar.unmarshall('s_tr')
        self.assertEqual(result['link'], False)
        self.assertEqual(result['processor_name'], None)
        self.assertEqual(result['source'], 's_tr')

        result = self.dep_mar.unmarshall('s_tr:strr')
        self.assertEqual(result['link'], False)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 'strr')

        result = self.dep_mar.unmarshall('@s_tr:s__t__r__')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 's__t__r__')

        result = self.dep_mar.unmarshall('@s_tr:str1-11   ')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 'str1-11')

        self.assertRaises(ValueError, self.dep_mar.unmarshall, '@s_tr:str%1-11   ')
        self.assertRaises(ValueError, self.dep_mar.unmarshall, '       ')
        self.assertRaises(ValueError, self.dep_mar.unmarshall, '')
        self.assertRaises(ValueError, self.dep_mar.unmarshall, None)

    def test_marshall_string(self):
        self.assertEqual(self.dep_mar.marshall('s1', False, None), 's1')
        self.assertEqual(self.dep_mar.marshall('s1', True, None), '@s1')
        self.assertEqual(self.dep_mar.marshall('s1', True, ''), '@s1')
        self.assertEqual(self.dep_mar.marshall('s1', False, 'processor'), 'processor:s1')
        self.assertEqual(self.dep_mar.marshall('s1', True, 'processor'), '@processor:s1')

        self.assertRaises(ValueError, self.dep_mar.marshall, '', False, None)

