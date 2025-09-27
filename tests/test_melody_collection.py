"""
Test cases for MelodyCollection and InMemoryMelodyCollection classes.
"""

import os
import tempfile
import zipfile
import unittest
from pathlib import Path

from splyne.input_handling import (
    Melody,
    Note,
    MelodyCollection,
    InMemoryMelodyCollection
)


class TestMelodyCollection(unittest.TestCase):
    """Test cases for MelodyCollection abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that MelodyCollection cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            MelodyCollection()


class TestInMemoryMelodyCollection(unittest.TestCase):
    """Test cases for InMemoryMelodyCollection class."""

    def setUp(self):
        """Set up test data directory."""
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.midi_dir = os.path.join(self.test_data_dir, 'midi')

        # Ensure the test data directory exists
        self.assertTrue(os.path.exists(self.test_data_dir),
                       f"Test data directory not found: {self.test_data_dir}")
        self.assertTrue(os.path.exists(self.midi_dir),
                       f"MIDI test data directory not found: {self.midi_dir}")

    def test_directory_initialization(self):
        """Test initialization with a directory containing MIDI files."""
        collection = InMemoryMelodyCollection(self.midi_dir, "Test MIDI Collection")

        self.assertEqual(collection.get_name(), "Test MIDI Collection")
        self.assertGreater(collection.size(), 0)
        self.assertIsInstance(collection.size(), int)

    def test_directory_initialization_default_name(self):
        """Test initialization with a directory using default name."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        self.assertEqual(collection.get_name(), "midi")
        self.assertGreater(collection.size(), 0)

    def test_nonexistent_path_raises_error(self):
        """Test that initializing with nonexistent path raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            InMemoryMelodyCollection("/nonexistent/path")

    def test_invalid_path_type_raises_error(self):
        """Test that initializing with a regular file (not ZIP) raises ValueError."""
        # Use a regular MIDI file instead of directory or ZIP
        midi_file = os.path.join(self.test_data_dir, 'fur_elise_short.mid')
        if os.path.exists(midi_file):
            with self.assertRaises(ValueError):
                InMemoryMelodyCollection(midi_file)

    def test_add_melody(self):
        """Test adding a melody to the collection."""
        collection = InMemoryMelodyCollection(self.midi_dir)
        initial_size = collection.size()

        # Create a test melody
        test_melody = Melody("test_melody")
        test_melody.add_note(Note(60, 0.0, 1.0))

        collection.add(test_melody)

        self.assertEqual(collection.size(), initial_size + 1)
        self.assertTrue(collection.contains("test_melody"))
        retrieved_melody = collection.get("test_melody")
        self.assertEqual(retrieved_melody.id, "test_melody")

    def test_add_duplicate_melody_raises_error(self):
        """Test that adding a melody with duplicate ID raises ValueError."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        test_melody1 = Melody("duplicate_id")
        test_melody2 = Melody("duplicate_id")

        collection.add(test_melody1)

        with self.assertRaises(ValueError):
            collection.add(test_melody2)

    def test_get_nonexistent_melody_raises_error(self):
        """Test that getting a nonexistent melody raises KeyError."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        with self.assertRaises(KeyError):
            collection.get("nonexistent_melody")

    def test_iteration(self):
        """Test iterating over melodies in the collection."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        melody_count = 0
        for melody in collection:
            self.assertIsInstance(melody, Melody)
            melody_count += 1

        self.assertEqual(melody_count, collection.size())

    def test_list_melody_ids(self):
        """Test listing all melody IDs."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        melody_ids = collection.list_melody_ids()
        self.assertIsInstance(melody_ids, list)
        self.assertEqual(len(melody_ids), collection.size())

        # Check that all IDs are strings
        for melody_id in melody_ids:
            self.assertIsInstance(melody_id, str)

    def test_contains(self):
        """Test checking if melody exists in collection."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        # Add a test melody
        test_melody = Melody("test_contains")
        collection.add(test_melody)

        self.assertTrue(collection.contains("test_contains"))
        self.assertFalse(collection.contains("nonexistent"))

    def test_remove_melody(self):
        """Test removing a melody from the collection."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        # Add a test melody
        test_melody = Melody("test_remove")
        collection.add(test_melody)
        initial_size = collection.size()

        # Remove the melody
        collection.remove("test_remove")

        self.assertEqual(collection.size(), initial_size - 1)
        self.assertFalse(collection.contains("test_remove"))

    def test_remove_nonexistent_melody_raises_error(self):
        """Test that removing a nonexistent melody raises KeyError."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        with self.assertRaises(KeyError):
            collection.remove("nonexistent_melody")

    def test_clear_collection(self):
        """Test clearing all melodies from the collection."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        # Ensure collection is not empty
        self.assertGreater(collection.size(), 0)

        collection.clear()

        self.assertEqual(collection.size(), 0)
        self.assertEqual(len(collection.list_melody_ids()), 0)

    def test_zip_file_initialization(self):
        """Test initialization with a ZIP file containing MIDI files."""
        # Create a temporary ZIP file with some MIDI files
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "test_midi.zip")

            # Get some test MIDI files
            midi_files = []
            for file_name in os.listdir(self.midi_dir):
                if file_name.endswith('.mid'):
                    midi_files.append(os.path.join(self.midi_dir, file_name))
                    if len(midi_files) >= 3:  # Limit to first 3 files
                        break

            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for midi_file in midi_files:
                    zip_file.write(midi_file, os.path.basename(midi_file))

            # Test loading from ZIP
            collection = InMemoryMelodyCollection(zip_path, "Test ZIP Collection")

            self.assertEqual(collection.get_name(), "Test ZIP Collection")
            self.assertEqual(collection.size(), len(midi_files))

    def test_empty_directory(self):
        """Test initialization with an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            collection = InMemoryMelodyCollection(temp_dir, "Empty Collection")

            self.assertEqual(collection.get_name(), "Empty Collection")
            self.assertEqual(collection.size(), 0)

    def test_zip_file_with_no_midi_files(self):
        """Test initialization with a ZIP file containing no MIDI files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "no_midi.zip")

            # Create ZIP with non-MIDI files
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("test.txt", "This is not a MIDI file")
                zip_file.writestr("readme.md", "# No MIDI files here")

            collection = InMemoryMelodyCollection(zip_path, "No MIDI Collection")

            self.assertEqual(collection.get_name(), "No MIDI Collection")
            self.assertEqual(collection.size(), 0)

    def test_invalid_zip_file_raises_error(self):
        """Test that initializing with an invalid ZIP file raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with .zip extension but not actually a ZIP file
            fake_zip_path = os.path.join(temp_dir, "fake.zip")
            with open(fake_zip_path, 'w') as f:
                f.write("This is not a ZIP file")

            with self.assertRaises(ValueError):
                InMemoryMelodyCollection(fake_zip_path)

    def test_repr(self):
        """Test string representation of the collection."""
        collection = InMemoryMelodyCollection(self.midi_dir, "Test Repr")

        repr_str = repr(collection)
        self.assertIn("InMemoryMelodyCollection", repr_str)
        self.assertIn("Test Repr", repr_str)
        self.assertIn(str(collection.size()), repr_str)

    def test_loaded_melodies_have_notes(self):
        """Test that loaded melodies contain notes."""
        collection = InMemoryMelodyCollection(self.midi_dir)

        if collection.size() > 0:
            # Get the first melody
            melody_ids = collection.list_melody_ids()
            first_melody = collection.get(melody_ids[0])

            self.assertIsInstance(first_melody, Melody)
            self.assertIsInstance(first_melody.notes, list)
            # Most MIDI files should have at least some notes
            if len(first_melody.notes) > 0:
                self.assertIsInstance(first_melody.notes[0], Note)


if __name__ == '__main__':
    unittest.main()
