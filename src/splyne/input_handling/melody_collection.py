"""
Abstract base class for managing collections of melodies.
"""

from abc import ABC, abstractmethod
from typing import Iterator
from .melody import Melody


class MelodyCollection(ABC):
    """
    Abstract base class that defines the interface for managing a collection of melodies.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the collection.

        Returns:
            str: The name of the collection.
        """
        pass

    @abstractmethod
    def add(self, melody: Melody) -> None:
        """
        Adds a melody to the collection.

        Args:
            melody (Melody): The melody to add to the collection.
        """
        pass

    @abstractmethod
    def get(self, melody_id: str) -> Melody:
        """
        Retrieves a melody by its ID.

        Args:
            melody_id (str): The unique identifier of the melody.

        Returns:
            Melody: The melody with the specified ID.

        Raises:
            KeyError: If no melody with the given ID exists.
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Returns the number of melodies in the collection.

        Returns:
            int: The number of melodies in the collection.
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Melody]:
        """
        Allows iteration over the melodies in the collection.

        Returns:
            Iterator[Melody]: An iterator over the melodies.
        """
        pass
