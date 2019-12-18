class DependenciesMarshalling(object):

    def marshall(self, source, is_link: bool = False, processor_name: str = None, custom_name: str = None):
        if isinstance(source, list):
            return [self.__marshall(src, is_link, processor_name, custom_name) for src in source]
        if isinstance(source, str):
            return self.__marshall(source, is_link, processor_name, custom_name)
        raise ValueError('source must be a string or list of strings')

    def unmarshall(self, source):
        if isinstance(source, list):
            return [self.__unmarshall(src) for src in source]
        if isinstance(source, str):
            return self.__unmarshall(source)
        raise ValueError('source must be a string or list of strings')

    def __marshall(self, source: str, is_link: bool = False, processor_name: str = None, custom_name: str = None):
        return '{}{}{}{}'.format(self.__str_link(is_link), source, self.__str_processor_name(processor_name), self.__str_custom_name(custom_name))

    def __unmarshall(self, source: str):
        return {}

    def __str_link(self, is_link: bool):
        return '@' if is_link else ''

    def __str_processor_name(self, processor_name: str):
        return '{}:'.format(processor_name) if processor_name else ''

    def __str_custom_name(self, custom_name: str):
        return '${}'.format(custom_name) if custom_name else ''



