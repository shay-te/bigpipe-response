import unittest

from bigpipe_response.dependencies_marshalling import DependenciesMarshalling


class TestDependenciesMarshalling(unittest.TestCase):

    def test_unmarshall_string(self):
        result = DependenciesMarshalling.unmarshall('@s_tr')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], None)
        self.assertEqual(result['source'], 's_tr')

        result = DependenciesMarshalling.unmarshall('s_tr')
        self.assertEqual(result['link'], False)
        self.assertEqual(result['processor_name'], None)
        self.assertEqual(result['source'], 's_tr')

        result = DependenciesMarshalling.unmarshall('s_tr:strr')
        self.assertEqual(result['link'], False)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 'strr')

        result = DependenciesMarshalling.unmarshall('@s_tr:s__t__r__')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 's__t__r__')

        result = DependenciesMarshalling.unmarshall('@s_tr:str1-11   ')
        self.assertEqual(result['link'], True)
        self.assertEqual(result['processor_name'], 's_tr')
        self.assertEqual(result['source'], 'str1-11')

        result = DependenciesMarshalling.unmarshall(['aa1', 'aa2'])
        self.assertEqual(result[0]['link'], False)
        self.assertEqual(result[0]['processor_name'], None)
        self.assertEqual(result[0]['source'], 'aa1')
        self.assertEqual(result[1]['link'], False)
        self.assertEqual(result[1]['processor_name'], None)
        self.assertEqual(result[1]['source'], 'aa2')

        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '@s_tr:str%1-11   ')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '       ')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, None)

    def test_marshall_string(self):
        self.assertEqual(DependenciesMarshalling.marshall('s1', False, None), 's1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, None), '@s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, ''), '@s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', False, 'processor'), 'processor:s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, 'processor'), '@processor:s1')

        marshall_results = DependenciesMarshalling.marshall(['s1', 's2', 's3'], True, 'proc2')
        self.assertEqual(len(marshall_results), 3)
        self.assertEqual(marshall_results[0], '@proc2:s1')
        self.assertEqual(marshall_results[1], '@proc2:s2')
        self.assertEqual(marshall_results[2], '@proc2:s3')

        self.assertRaises(ValueError, DependenciesMarshalling.marshall, '', False, None)

