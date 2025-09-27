"""
Unit tests for the NGram class.
"""

import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from splyne.input_handling.note import Note
from splyne.input_handling.melody import Melody
from splyne.comparision.ngram import NGram


class TestNGram(unittest.TestCase):
    """Test cases for the NGram class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create some test notes
        self.note1 = Note(pitch=71, onset=0.0, duration=48, rest_fraction=0.0)
        self.note2 = Note(pitch=74, onset=48.0, duration=48, rest_fraction=0.0)
        self.note3 = Note(pitch=72, onset=96.0, duration=96, rest_fraction=0.0)
        self.note4 = Note(pitch=69, onset=192.0, duration=96, rest_fraction=0.0)
        self.note5 = Note(pitch=67, onset=288.0, duration=48, rest_fraction=0.0)

        # Create a test melody
        self.melody = Melody("test_melody")
        self.melody.add_note(self.note1)
        self.melody.add_note(self.note2)
        self.melody.add_note(self.note3)
        self.melody.add_note(self.note4)
        self.melody.add_note(self.note5)

    def test_ngram_init(self):
        """Test NGram initialization."""
        notes = [self.note1, self.note2, self.note3]
        ngram = NGram(notes)

        self.assertEqual(len(ngram.notes), 3)
        self.assertEqual(ngram.notes[0], self.note1)
        self.assertEqual(ngram.notes[1], self.note2)
        self.assertEqual(ngram.notes[2], self.note3)

    def test_ngram_init_empty(self):
        """Test NGram initialization with empty list."""
        ngram = NGram([])
        self.assertEqual(len(ngram.notes), 0)

    def test_get_null_span(self):
        """Test the get_null_span method."""
        notes = [self.note1, self.note2, self.note3]
        ngram = NGram(notes)

        null_ngram = ngram.get_null_span()

        # All notes should have the same pitch as the first note
        first_pitch = self.note1.pitch
        for note in null_ngram.notes:
            self.assertEqual(note.pitch, first_pitch)

        # Other properties should be preserved
        for i, note in enumerate(null_ngram.notes):
            original_note = notes[i]
            self.assertEqual(note.onset, original_note.onset)
            self.assertEqual(note.duration, original_note.duration)
            self.assertEqual(note.rest_fraction, original_note.rest_fraction)

    def test_get_null_span_empty(self):
        """Test get_null_span with empty NGram."""
        ngram = NGram([])
        null_ngram = ngram.get_null_span()
        self.assertEqual(len(null_ngram.notes), 0)

    def test_str_representation(self):
        """Test the string representation of NGram."""
        notes = [self.note1, self.note2, self.note3]
        ngram = NGram(notes)

        expected = "{71,48,0.0}{74,48,0.0}{72,96,0.0}"
        self.assertEqual(str(ngram), expected)

    def test_str_representation_empty(self):
        """Test string representation of empty NGram."""
        ngram = NGram([])
        self.assertEqual(str(ngram), "")

    def test_str_representation_single_note(self):
        """Test string representation of single note NGram."""
        ngram = NGram([self.note1])
        expected = "{71,48,0.0}"
        self.assertEqual(str(ngram), expected)

    def test_get_ngrams_basic(self):
        """Test basic n-gram generation."""
        ngrams = NGram.get_ngrams(self.melody, 3)

        # Should have 3 n-grams from a melody with 5 notes
        self.assertEqual(len(ngrams), 3)

        # Check first n-gram
        first_ngram = ngrams[0]
        self.assertEqual(len(first_ngram.notes), 3)
        self.assertEqual(first_ngram.notes[0], self.note1)
        self.assertEqual(first_ngram.notes[1], self.note2)
        self.assertEqual(first_ngram.notes[2], self.note3)

        # Check second n-gram
        second_ngram = ngrams[1]
        self.assertEqual(len(second_ngram.notes), 3)
        self.assertEqual(second_ngram.notes[0], self.note2)
        self.assertEqual(second_ngram.notes[1], self.note3)
        self.assertEqual(second_ngram.notes[2], self.note4)

        # Check third n-gram
        third_ngram = ngrams[2]
        self.assertEqual(len(third_ngram.notes), 3)
        self.assertEqual(third_ngram.notes[0], self.note3)
        self.assertEqual(third_ngram.notes[1], self.note4)
        self.assertEqual(third_ngram.notes[2], self.note5)

    def test_get_ngrams_n_equals_melody_length(self):
        """Test n-gram generation when n equals melody length."""
        ngrams = NGram.get_ngrams(self.melody, 5)

        # Should have 1 n-gram
        self.assertEqual(len(ngrams), 1)

        # The n-gram should contain all notes
        ngram = ngrams[0]
        self.assertEqual(len(ngram.notes), 5)
        for i, note in enumerate(ngram.notes):
            self.assertEqual(note, self.melody.notes[i])

    def test_get_ngrams_n_greater_than_melody_length(self):
        """Test n-gram generation when n is greater than melody length."""
        ngrams = NGram.get_ngrams(self.melody, 10)

        # Should return empty list
        self.assertEqual(len(ngrams), 0)

    def test_get_ngrams_n_zero_or_negative(self):
        """Test n-gram generation with invalid n values."""
        ngrams_zero = NGram.get_ngrams(self.melody, 0)
        ngrams_negative = NGram.get_ngrams(self.melody, -1)

        self.assertEqual(len(ngrams_zero), 0)
        self.assertEqual(len(ngrams_negative), 0)

    def test_get_ngrams_empty_melody(self):
        """Test n-gram generation with empty melody."""
        empty_melody = Melody("empty")
        ngrams = NGram.get_ngrams(empty_melody, 3)

        self.assertEqual(len(ngrams), 0)

    def test_equality(self):
        """Test NGram equality."""
        notes1 = [self.note1, self.note2, self.note3]
        notes2 = [self.note1, self.note2, self.note3]
        notes3 = [self.note1, self.note2, self.note4]

        ngram1 = NGram(notes1)
        ngram2 = NGram(notes2)
        ngram3 = NGram(notes3)

        self.assertEqual(ngram1, ngram2)
        self.assertNotEqual(ngram1, ngram3)
        self.assertNotEqual(ngram1, "not an ngram")

    def test_repr(self):
        """Test NGram repr method."""
        notes = [self.note1, self.note2]
        ngram = NGram(notes)

        repr_str = repr(ngram)
        self.assertIn("NGram", repr_str)
        self.assertIn("notes=", repr_str)


class TestNGramIntegration(unittest.TestCase):

    """Test NGram implementation against the expected output from Java version."""

    def setUp(self):
        """Set up test fixtures with Java reference output."""
        # Java reference output for 0A2A.mid with n=6
        self.java_reference_output = [
            "{71,48,0.0}{71,48,0.0}{74,48,0.0}{74,48,0.0}{72,96,0.0}{69,96,0.0}",
            "{71,48,0.0}{74,48,0.0}{74,48,0.0}{72,96,0.0}{69,96,0.0}{67,48,0.0}",
            "{74,48,0.0}{74,48,0.0}{72,96,0.0}{69,96,0.0}{67,48,0.0}{69,48,0.0}",
            "{74,48,0.0}{72,96,0.0}{69,96,0.0}{67,48,0.0}{69,48,0.0}{71,48,0.0}",
            "{72,96,0.0}{69,96,0.0}{67,48,0.0}{69,48,0.0}{71,48,0.0}{72,48,0.0}",
            "{69,96,0.0}{67,48,0.0}{69,48,0.0}{71,48,0.0}{72,48,0.0}{69,96,0.0}",
            "{67,48,0.0}{69,48,0.0}{71,48,0.0}{72,48,0.0}{69,96,0.0}{72,48,0.6666666666666666}",
            "{69,48,0.0}{71,48,0.0}{72,48,0.0}{69,96,0.0}{72,48,0.6666666666666666}{72,48,0.0}",
            "{71,48,0.0}{72,48,0.0}{69,96,0.0}{72,48,0.6666666666666666}{72,48,0.0}{71,48,0.0}",
            "{72,48,0.0}{69,96,0.0}{72,48,0.6666666666666666}{72,48,0.0}{71,48,0.0}{71,48,0.0}",
            "{69,96,0.0}{72,48,0.6666666666666666}{72,48,0.0}{71,48,0.0}{71,48,0.0}{76,96,0.0}",
            "{72,48,0.6666666666666666}{72,48,0.0}{71,48,0.0}{71,48,0.0}{76,96,0.0}{74,96,0.0}",
            "{72,48,0.0}{71,48,0.0}{71,48,0.0}{76,96,0.0}{74,96,0.0}{74,48,0.0}",
            "{71,48,0.0}{71,48,0.0}{76,96,0.0}{74,96,0.0}{74,48,0.0}{72,48,0.0}",
            "{71,48,0.0}{76,96,0.0}{74,96,0.0}{74,48,0.0}{72,48,0.0}{71,48,0.0}",
            "{76,96,0.0}{74,96,0.0}{74,48,0.0}{72,48,0.0}{71,48,0.0}{69,48,0.0}",
            "{74,96,0.0}{74,48,0.0}{72,48,0.0}{71,48,0.0}{69,48,0.0}{67,96,0.0}"
        ]

        # Import here to avoid import issues
        from splyne.input_handling.tunes_reader import MidiReader
        self.midi_reader = MidiReader()
        self.test_midi_path = os.path.join(os.path.dirname(__file__), 'test_data', 'midi', '0A2A.mid')

        # Generate expected NGrams from Java reference with converted durations
        self.expected_ngrams = self._convert_java_reference_to_ngrams()

    def _convert_java_reference_to_ngrams(self):
        """
        Convert Java reference output strings to expected NGram objects.
        Parses the Java format {pitch,duration_ticks,rest_fraction} and converts
        duration from MIDI ticks to quarter notes (ticks / 96.0).

        Returns:
            List[NGram]: List of expected NGram objects with converted durations.
        """
        import re
        from splyne.input_handling.note import Note

        expected_ngrams = []

        for java_ngram_str in self.java_reference_output:
            # Parse the Java format: {pitch,duration,rest_fraction}{pitch,duration,rest_fraction}...
            pattern = r'\{(\d+),(\d+(?:\.\d+)?),([\d\.]+)\}'
            matches = re.findall(pattern, java_ngram_str)

            notes = []
            for match in matches:
                pitch = int(match[0])
                duration_ticks = float(match[1])
                rest_fraction = float(match[2])

                # Convert duration from MIDI ticks to quarter notes
                duration_quarter_notes = duration_ticks / 96.0

                # Create Note object (onset doesn't matter for this comparison)
                note = Note(
                    pitch=pitch,
                    onset=0.0,  # Not used in string comparison
                    duration=duration_quarter_notes,
                    rest_fraction=rest_fraction
                )
                notes.append(note)

            # Create NGram from the converted notes
            expected_ngrams.append(NGram(notes))

        return expected_ngrams

    def test_validate_against_java_output(self):
        """Test that Python NGram output matches Java reference output exactly."""
        # Check if test file exists
        self.assertTrue(os.path.exists(self.test_midi_path),
                       f"Test MIDI file not found: {self.test_midi_path}")

        # Load the MIDI file
        melody = self.midi_reader.read("0A2A", self.test_midi_path)

        # Generate 6-grams
        ngrams = NGram.get_ngrams(melody, 6)

        # Convert both to string representations for comparison
        python_output = [str(ngram) for ngram in ngrams]
        expected_output = [str(ngram) for ngram in self.expected_ngrams]

        # Debug information
        print(f"\nLoaded melody with {len(melody.notes)} notes")
        print(f"Generated {len(python_output)} n-grams")
        print(f"Expected {len(expected_output)} n-grams")
        print(f"Java reference has {len(self.java_reference_output)} n-grams")

        # Check that we have the same number of n-grams
        self.assertEqual(len(python_output), len(expected_output),
                        f"Different number of n-grams: Python={len(python_output)}, Expected={len(expected_output)}")

        # Compare each n-gram output
        mismatches = []
        for i, (python_ngram, expected_ngram) in enumerate(zip(python_output, expected_output)):
            if python_ngram != expected_ngram:
                mismatches.append((i, python_ngram, expected_ngram))

        # Print comparison details
        if mismatches:
            print(f"\nFound {len(mismatches)} mismatches:")
            for i, python_ngram, expected_ngram in mismatches[:5]:  # Show first 5 mismatches
                print(f"  N-gram {i}:")
                print(f"    Python:   {python_ngram}")
                print(f"    Expected: {expected_ngram}")
                print(f"    Java ref: {self.java_reference_output[i]}")
        else:
            print("\nAll n-grams match perfectly!")

        # Assert that all n-grams match
        for i, python_ngram, expected_ngram in mismatches:
            self.assertEqual(python_ngram, expected_ngram,
                           f"N-gram {i} mismatch:\nPython:   {python_ngram}\nExpected: {expected_ngram}\nJava ref: {self.java_reference_output[i]}")

    def test_melody_structure_validation(self):
        """Test that the loaded melody has the expected structure."""
        # Load the MIDI file
        melody = self.midi_reader.read("0A2A", self.test_midi_path)

        # Basic validation
        self.assertIsNotNone(melody)
        self.assertGreater(len(melody.notes), 0, "Melody should contain notes")

        # Should have exactly 22 notes to generate 17 6-grams (22 - 6 + 1 = 17)
        expected_note_count = len(self.java_reference_output) + 6 - 1  # 17 + 6 - 1 = 22
        self.assertEqual(len(melody.notes), expected_note_count,
                        f"Expected {expected_note_count} notes, got {len(melody.notes)}")

        # Print first few notes for debugging
        print(f"\nFirst 10 notes from melody:")
        for i, note in enumerate(melody.notes[:10]):
            print(f"  Note {i}: pitch={note.pitch}, duration={note.duration}, rest_fraction={note.rest_fraction}")


if __name__ == '__main__':
    unittest.main()
