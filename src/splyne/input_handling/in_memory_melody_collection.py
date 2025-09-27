"""
In-memory implementation of MelodyCollection that reads MIDI files from directories or ZIP files.
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Iterator, Dict, Union
import logging

from .melody_collection import MelodyCollection
from .melody import Melody
from .tunes_reader import MidiReader


class InMemoryMelodyCollection(MelodyCollection):
    """
    Concrete implementation of MelodyCollection that reads MIDI files from a directory or ZIP file,
    parses them, and stores them in memory.
    """

    def __init__(self, path: Union[str, Path], name: str = None):
        """
        Initializes the InMemoryMelodyCollection by reading MIDI files from the given path.

        Args:
            path (Union[str, Path]): Path to a directory containing MIDI files or a ZIP file.
            name (str, optional): Name of the collection. If not provided, uses the basename of the path.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            ValueError: If the path is neither a directory nor a ZIP file.
        """
        self._path = Path(path)
        self._name = name or self._path.stem
        self._melodies: Dict[str, Melody] = {}
        self._midi_reader = MidiReader()
        
        # Set up logging
        self._logger = logging.getLogger(__name__)
        
        if not self._path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        self._load_melodies()

    def _load_melodies(self) -> None:
        """
        Loads melodies from the specified path (directory or ZIP file).
        """
        if self._path.is_dir():
            self._load_from_directory()
        elif self._path.is_file() and self._path.suffix.lower() == '.zip':
            self._load_from_zip()
        else:
            raise ValueError(f"Path must be a directory or ZIP file: {self._path}")

    def _load_from_directory(self) -> None:
        """
        Loads all MIDI files from a directory.
        """
        midi_files = []
        
        # Find all MIDI files in the directory (including subdirectories)
        for file_path in self._path.rglob("*"):
            if file_path.is_file() and self._midi_reader.accept(file_path.name):
                midi_files.append(file_path)
        
        if not midi_files:
            self._logger.warning(f"No MIDI files found in directory: {self._path}")
            return
        
        self._logger.info(f"Found {len(midi_files)} MIDI files in directory: {self._path}")
        
        for file_path in midi_files:
            self._load_midi_file(file_path, file_path.stem)

    def _load_from_zip(self) -> None:
        """
        Loads all MIDI files from a ZIP archive.
        """
        try:
            with zipfile.ZipFile(self._path, 'r') as zip_file:
                midi_files = [
                    name for name in zip_file.namelist()
                    if not name.endswith('/') and self._midi_reader.accept(name)
                ]
                
                if not midi_files:
                    self._logger.warning(f"No MIDI files found in ZIP archive: {self._path}")
                    return
                
                self._logger.info(f"Found {len(midi_files)} MIDI files in ZIP archive: {self._path}")
                
                # Create a temporary directory to extract files
                with tempfile.TemporaryDirectory() as temp_dir:
                    for midi_file in midi_files:
                        try:
                            # Extract the file to temporary directory
                            zip_file.extract(midi_file, temp_dir)
                            extracted_path = Path(temp_dir) / midi_file
                            
                            # Use the filename without extension as melody ID
                            melody_id = Path(midi_file).stem
                            
                            self._load_midi_file(extracted_path, melody_id)
                            
                        except Exception as e:
                            self._logger.error(f"Failed to extract and parse {midi_file}: {e}")
                            continue
                            
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid ZIP file: {self._path}")
        except Exception as e:
            raise RuntimeError(f"Failed to read ZIP file {self._path}: {e}")

    def _load_midi_file(self, file_path: Path, melody_id: str) -> None:
        """
        Loads a single MIDI file and adds it to the collection.

        Args:
            file_path (Path): Path to the MIDI file.
            melody_id (str): Unique identifier for the melody.
        """
        try:
            melody = self._midi_reader.read(melody_id, str(file_path))
            self._melodies[melody_id] = melody
            self._logger.debug(f"Successfully loaded melody: {melody_id}")
            
        except Exception as e:
            self._logger.error(f"Failed to parse MIDI file {file_path}: {e}")
            # Continue with other files rather than failing completely

    def get_name(self) -> str:
        """
        Returns the name of the collection.

        Returns:
            str: The name of the collection.
        """
        return self._name

    def add(self, melody: Melody) -> None:
        """
        Adds a melody to the collection.

        Args:
            melody (Melody): The melody to add to the collection.

        Raises:
            ValueError: If a melody with the same ID already exists.
        """
        if melody.id in self._melodies:
            raise ValueError(f"Melody with ID '{melody.id}' already exists in collection")
        
        self._melodies[melody.id] = melody
        self._logger.debug(f"Added melody to collection: {melody.id}")

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
        if melody_id not in self._melodies:
            raise KeyError(f"No melody found with ID: {melody_id}")
        
        return self._melodies[melody_id]

    def size(self) -> int:
        """
        Returns the number of melodies in the collection.

        Returns:
            int: The number of melodies in the collection.
        """
        return len(self._melodies)

    def __iter__(self) -> Iterator[Melody]:
        """
        Allows iteration over the melodies in the collection.

        Returns:
            Iterator[Melody]: An iterator over the melodies.
        """
        return iter(self._melodies.values())

    def list_melody_ids(self) -> list[str]:
        """
        Returns a list of all melody IDs in the collection.

        Returns:
            list[str]: List of melody IDs.
        """
        return list(self._melodies.keys())

    def contains(self, melody_id: str) -> bool:
        """
        Checks if a melody with the given ID exists in the collection.

        Args:
            melody_id (str): The melody ID to check.

        Returns:
            bool: True if the melody exists, False otherwise.
        """
        return melody_id in self._melodies

    def remove(self, melody_id: str) -> None:
        """
        Removes a melody from the collection.

        Args:
            melody_id (str): The unique identifier of the melody to remove.

        Raises:
            KeyError: If no melody with the given ID exists.
        """
        if melody_id not in self._melodies:
            raise KeyError(f"No melody found with ID: {melody_id}")
        
        del self._melodies[melody_id]
        self._logger.debug(f"Removed melody from collection: {melody_id}")

    def clear(self) -> None:
        """
        Removes all melodies from the collection.
        """
        self._melodies.clear()
        self._logger.debug("Cleared all melodies from collection")

    def __repr__(self) -> str:
        """
        Returns a string representation of the collection.

        Returns:
            str: String representation.
        """
        return f"InMemoryMelodyCollection(name='{self._name}', size={self.size()})"