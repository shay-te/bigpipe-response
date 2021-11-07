from hydra.core.config_search_path import ConfigSearchPath
from hydra.plugins.search_path_plugin import SearchPathPlugin


class BigpipeResponseSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        assert isinstance(search_path, ConfigSearchPath)
        # Appends the search path for this plugin to the end of the search path
        search_path.append("bigpipe-response", "pkg://bigpipe_response.config")
