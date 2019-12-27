import re


class DependenciesMarshalling(object):

    def marshall(self, source, is_link: bool = False, processor_name: str = None):
        if isinstance(source, list):
            return [self.__marshall(src, is_link, processor_name) for src in source]
        if isinstance(source, str):
            return self.__marshall(source, is_link, processor_name)
        raise ValueError('source must be a string or list of strings')

    def __marshall(self, source: str, is_link: bool = False, processor_name: str = None):
        return '{}{}{}'.format(self.__str_link(is_link), self.__str_processor_name(processor_name), self.__str_source(source))

    def unmarshall(self, source):
        if isinstance(source, list):
            return [self.__unmarshall(src) for src in source]
        if isinstance(source, str):
            return self.__unmarshall(source)
        raise ValueError('source must be a string or list of strings')

    def __unmarshall(self, source: str):
        matches = re.search('^(?P<link>@)?((?P<proc_name>[\w-]+):)?(?P<source_value>[\w-]+)$', source.strip(), re.IGNORECASE)
        if matches:
            return {
                'link': True if matches.group('link') else False,
                'processor_name': matches.group('proc_name'),
                'source': matches.group('source_value')
            }
        else:
            raise ValueError('unmarshall failed, invalid source: {} .allowed character must match regex: [\\w-]+'.format(source))

    def __str_link(self, is_link: bool):
        return '@' if is_link else ''

    def __str_processor_name(self, processor_name: str):
        return '{}:'.format(processor_name.strip()) if processor_name else ''

    def __str_source(self, source):
        if source:
            return source.strip()
        raise ValueError('Source cannot be empty')

