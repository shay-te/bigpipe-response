import unittest

from bigpipe_response.dependencies_marshalling import DependenciesMarshalling


class TestDependenciesMarshalling(unittest.TestCase):

    def test_unmarshall_string(self):
        result = DependenciesMarshalling.unmarshall('index.html')
        self.assertEqual(result[0]['link'], False)
        self.assertEqual(result[0]['processor_name'], None)
        self.assertEqual(result[0]['source'], 'index.html')

        result = DependenciesMarshalling.unmarshall('@proc_name:index.tag.gz.html.some_ext')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], 'proc_name')
        self.assertEqual(result[0]['source'], 'index.tag.gz.html.some_ext')

        result = DependenciesMarshalling.unmarshall('@proc_name:in.............some_ex-t')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], 'proc_name')
        self.assertEqual(result[0]['source'], 'in.............some_ex-t')

        result = DependenciesMarshalling.unmarshall('@s_tr')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], None)
        self.assertEqual(result[0]['source'], 's_tr')

        result = DependenciesMarshalling.unmarshall('s_tr')
        self.assertEqual(result[0]['link'], False)
        self.assertEqual(result[0]['processor_name'], None)
        self.assertEqual(result[0]['source'], 's_tr')

        result = DependenciesMarshalling.unmarshall('s_tr:strr')
        self.assertEqual(result[0]['link'], False)
        self.assertEqual(result[0]['processor_name'], 's_tr')
        self.assertEqual(result[0]['source'], 'strr')

        result = DependenciesMarshalling.unmarshall('@s_tr:s__t__r__')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], 's_tr')
        self.assertEqual(result[0]['source'], 's__t__r__')

        result = DependenciesMarshalling.unmarshall('@s_tr:str1-11   ')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], 's_tr')
        self.assertEqual(result[0]['source'], 'str1-11')

        result = DependenciesMarshalling.unmarshall(['aa1', 'aa2'])
        self.assertEqual(result[0]['link'], False)
        self.assertEqual(result[0]['processor_name'], None)
        self.assertEqual(result[0]['source'], 'aa1')
        self.assertEqual(result[1]['link'], False)
        self.assertEqual(result[1]['processor_name'], None)
        self.assertEqual(result[1]['source'], 'aa2')

        result = DependenciesMarshalling.unmarshall('@proc2:s3=SS3')
        self.assertEqual(result[0]['link'], True)
        self.assertEqual(result[0]['processor_name'], 'proc2')
        self.assertEqual(result[0]['source'], 's3=SS3')

        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '@s_tr:str%1-11   ')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '       ')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, '')
        self.assertRaises(ValueError, DependenciesMarshalling.unmarshall, None)

    def test_marshall_string(self):
        self.assertEqual(DependenciesMarshalling.marshall('s1.html', False, None)[0], 's1.html')
        self.assertEqual(DependenciesMarshalling.marshall('s1.html', True, 'processor')[0], '@processor:s1.html')

        self.assertEqual(DependenciesMarshalling.marshall('s1', False, None)[0], 's1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, None)[0], '@s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, '')[0], '@s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', False, 'processor')[0], 'processor:s1')
        self.assertEqual(DependenciesMarshalling.marshall('s1', True, 'processor')[0], '@processor:s1')

        marshall_results = DependenciesMarshalling.marshall(['s1', 's2', 's3'], True, 'proc2')
        self.assertEqual(len(marshall_results), 3)
        self.assertEqual(marshall_results[0], '@proc2:s1')
        self.assertEqual(marshall_results[1], '@proc2:s2')
        self.assertEqual(marshall_results[2], '@proc2:s3')

        marshall_results = DependenciesMarshalling.marshall(['s1=SS1', 's2=SS2', 's3=SS3'], True, 'proc2')
        self.assertEqual(len(marshall_results), 3)
        self.assertEqual(marshall_results[0], '@proc2:s1=SS1')
        self.assertEqual(marshall_results[1], '@proc2:s2=SS2')
        self.assertEqual(marshall_results[2], '@proc2:s3=SS3')

        self.assertRaises(ValueError, DependenciesMarshalling.marshall, '', False, None)
