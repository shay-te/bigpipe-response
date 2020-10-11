from abc import ABC, abstractmethod


class JavascriptDOMBind(ABC):

    @abstractmethod
    def generate_bind_command(self, render_source: str, render_context: dict, target_element: str):
        pass
