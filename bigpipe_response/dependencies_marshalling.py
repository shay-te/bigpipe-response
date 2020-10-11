import re


class DependenciesMarshalling(object):

    @staticmethod
    def marshall(source, is_link: bool = False, processor_name: str = None):
        if isinstance(source, list):
            return [DependenciesMarshalling.__marshall(src, is_link, processor_name) for src in source]
        if isinstance(source, str):
            return [DependenciesMarshalling.__marshall(source, is_link, processor_name)]
        raise ValueError("source must be a string or list of strings")

    @staticmethod
    def __marshall(source: str, is_link: bool = False, processor_name: str = None):
        return "{}{}{}".format(DependenciesMarshalling.__str_link(is_link), DependenciesMarshalling.__str_processor_name(processor_name), DependenciesMarshalling.__str_source(source))

    @staticmethod
    def unmarshall(source):
        if isinstance(source, list):
            return [DependenciesMarshalling.__unmarshall(src) for src in source]
        if isinstance(source, str):
            return [DependenciesMarshalling.__unmarshall(source)]
        raise ValueError("source must be a string or list of strings")

    @staticmethod
    def __unmarshall(source: str):
        matches = re.search(r"^(?P<link>@)?((?P<proc_name>[\w-]+):)?(?P<source_value>[\w./=-]+)$", source.strip(), re.IGNORECASE)
        if matches:
            return {
                "link": True if matches.group("link") else False,
                "processor_name": matches.group("proc_name"),
                "source": matches.group("source_value")
            }
        else:
            raise ValueError("unmarshall failed, invalid source: {} .allowed character must match regex: [\\w-]+".format(source))

    @staticmethod
    def __str_link(is_link: bool):
        return "@" if is_link else ""

    @staticmethod
    def __str_processor_name(processor_name: str):
        return "{}:".format(processor_name.strip()) if processor_name else ""

    @staticmethod
    def __str_source(source):
        if source:
            return source.strip()
        raise ValueError("Source cannot be empty")

