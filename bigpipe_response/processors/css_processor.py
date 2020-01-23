import os
import sass
from bigpipe_response.processors.base_file_processor import BaseFileProcessor


class CSSProcessor(BaseFileProcessor):

    def __init__(self, processor_name: str, source_paths: list, source_ext: list, target_ext: str):
        BaseFileProcessor.__init__(self, processor_name, source_paths, source_ext, target_ext, 'node_modules')
        self.include_paths = self.__generate_include_paths()
        self.is_production_mode = None

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        effected_files = []

        def importer_returning_one_argument(path, prev):
            effected_file = os.path.splitext(os.path.basename(path))[0]
            effected_files.append(effected_file)
            if effected_file in exclude_dependencies:
                return []
            return [(path, )]

        if not self.is_production_mode:  # on development mode files may change
            self.include_paths = self.__generate_include_paths()

        import_full_paths = []
        if not self.is_component_virtual(os.path.splitext(os.path.basename(input_file))[0]):
            import_full_paths.append(input_file)
        import_paths = []
        for dependency in include_dependencies:
            component_file = self._component_to_file[dependency]
            import_full_paths.append(component_file)
            import_paths.append(os.path.dirname(component_file))

        source_list = []
        for full_path in list(set(import_full_paths)):
            source_list.append('@import \'{}\';'.format(full_path.replace('\\', '/')))  # replace case of windows
        compiled = sass.compile(string=''.join(source_list),
                                include_paths=import_paths + self.include_paths,
                                importers=((0, importer_returning_one_argument,),),
                                output_style='compressed' if self.is_production_mode else 'expanded')

        fp = open(output_file, "w", encoding='utf-8')
        fp.write(compiled)
        fp.close()

        return effected_files

    def render_resource(self, input_file, context, i18n):
        raise ValueError('render resource not available for css processor.')

    def __generate_include_paths(self):
        result = []
        for code_base_dir in self.source_paths:
            for dir in os.walk(code_base_dir):
                result.append(dir[0])
        return result