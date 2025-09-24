from abc import ABC, abstractmethod

class MelodyReader(ABC):
    """
    Abstract base class for reading melodies.
    """

    @abstractmethod
    def read(self, melody_id, path):
        """
        Reads a melody from a file path.

        Args:
            melody_id (str): Unique identifier for the melody.
            path (str): Path to the file.

        Returns:
            Melody: The parsed melody object.
        """
        pass

    @abstractmethod
    def accept(self, file_name):
        """
        Checks if the file is supported by this reader.

        Args:
            file_name (str): Name of the file.

        Returns:
            bool: True if the file is supported, False otherwise.
        """
        pass
