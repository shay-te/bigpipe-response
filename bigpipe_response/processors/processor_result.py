class ProcessorResult(object):

    def __init__(self, effected_files: list, output_file: str):
        self.effected_files = effected_files
        self.output_file = output_file
