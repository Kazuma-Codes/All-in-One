from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConverter(ABC):
    """Abstract Base Class for all file converters."""
    
    @abstractmethod
    def validate(self, input_path: str, options: Dict[str, Any]) -> bool:
        """Check if the file is valid and options are supported."""
        pass

    @abstractmethod
    def execute(self, input_path: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Perform the actual conversion."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return supported formats, extensions, and options."""
        pass