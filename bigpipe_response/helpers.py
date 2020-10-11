from bigpipe_response.dependencies_marshalling import DependenciesMarshalling


def to_include(source, is_link: bool = False, processor_name: str = None):
    return DependenciesMarshalling.marshall(source, is_link, processor_name)
