import logging

logger = logging.getLogger('utils')


def get_class(path):
    try:
        from importlib import import_module

        module_path, _, class_name = path.rpartition(".")
        mod = import_module(module_path)
        try:
            klass = getattr(mod, class_name)
        except AttributeError:
            raise ImportError("Class {} is not in module {}".format(class_name, module_path))
        return klass
    except ValueError as e:
        logger.error("Error initializing class " + path)
        raise e