import os
import unittest
from splyne.input_handling.tunes_reader import MidiReader, AbcReader

class TestInputHandling(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.midi_reader = MidiReader()
        self.abc_reader = AbcReader()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    def test_midi_reader_pitch_sequence(self):
        """
        Test that MidiReader extracts the correct pitch sequence matching Java MelodyShape
        """
        # Expected pitch sequence from Java MelodyShape software for 0A2A.mid
        java_reference_pitches = [
            71, 71, 74, 74, 72, 69, 67, 69, 71, 72, 69, 72,
            72, 71, 71, 76, 74, 74, 72, 71, 69, 67
        ]

        # Path to the test MIDI file
        midi_file_path = os.path.join(self.test_data_dir, 'midi', '0A2A.mid')
        self.assertTrue(os.path.exists(midi_file_path), f"Test file {midi_file_path} does not exist")

        # Parse the MIDI file
        melody = self.midi_reader.read('0A2A', midi_file_path)

        # Test basic properties
        self.assertEqual(melody.get_id(), '0A2A', "Melody ID should match")
        self.assertEqual(len(melody.notes), len(java_reference_pitches),
                        f"Expected {len(java_reference_pitches)} notes, got {len(melody.notes)}")

        # Test pitch sequence matches Java reference exactly
        python_pitches = [note.pitch for note in melody.notes]
        self.assertEqual(python_pitches, java_reference_pitches,
                        "Pitch sequence should match Java MelodyShape reference exactly")

    def test_midi_reader_duration_ratios(self):
        """
        Test that MidiReader produces correct duration ratios matching Java MelodyShape
        Java uses ticks, Python uses quarter notes, but ratios should be consistent
        """
        # Java reference durations in ticks
        java_durations_ticks = [
            48, 48, 48, 48, 96, 96, 48, 48, 48, 48, 96, 48,
            48, 48, 48, 96, 96, 48, 48, 48, 48, 96
        ]

        midi_file_path = os.path.join(self.test_data_dir, 'midi', '0A2A.mid')
        melody = self.midi_reader.read('0A2A', midi_file_path)

        # Test that we have the right number of notes
        self.assertEqual(len(melody.notes), len(java_durations_ticks))

        # Test duration ratios - convert Java ticks to expected quarter note values
        # Assuming 96 ticks per quarter note: 48 ticks = 0.5 quarter, 96 ticks = 1.0 quarter
        expected_durations = [ticks / 96.0 for ticks in java_durations_ticks]
        python_durations = [note.duration for note in melody.notes]

        # Test that duration ratios are consistent (allow small floating point differences)
        for i, (py_dur, expected_dur) in enumerate(zip(python_durations, expected_durations)):
            self.assertAlmostEqual(py_dur, expected_dur, places=2,
                                 msg=f"Duration mismatch at note {i+1}: Python={py_dur}, Expected={expected_dur}")

        # Test specific duration patterns
        self.assertAlmostEqual(melody.notes[0].duration, 0.5, places=2, msg="First note should be 0.5 quarter notes")
        self.assertAlmostEqual(melody.notes[4].duration, 1.0, places=2, msg="Fifth note should be 1.0 quarter notes")

    def test_midi_reader_rest_fractions(self):
        """
        Test that MidiReader calculates rest fractions matching Java MelodyShape
        Rest fraction represents silence before a note relative to total time span
        """
        # Java reference rest fractions - most are 0.0 except note 12
        java_rest_fractions = [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.6666666666666666,  # Note 12 - the important one!
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]

        midi_file_path = os.path.join(self.test_data_dir, 'midi', '0A2A.mid')
        melody = self.midi_reader.read('0A2A', midi_file_path)

        # Test that we have the right number of notes
        self.assertEqual(len(melody.notes), len(java_rest_fractions))

        # Test rest fractions
        python_rest_fractions = [note.rest_fraction for note in melody.notes]

        for i, (py_rest, java_rest) in enumerate(zip(python_rest_fractions, java_rest_fractions)):
            self.assertAlmostEqual(py_rest, java_rest, places=3,
                                 msg=f"Rest fraction mismatch at note {i+1}: Python={py_rest}, Java={java_rest}")

        # Special test for the critical note 12 (0-indexed: note 11)
        note_12 = melody.notes[11]
        self.assertAlmostEqual(note_12.rest_fraction, 0.6666666666666666, places=3,
                              msg="Note 12 should have rest fraction ~0.667 matching Java output")
        self.assertEqual(note_12.pitch, 72, msg="Note 12 should have pitch 72")

        # Test that most other notes have rest_fraction = 0.0
        zero_rest_notes = [i for i, rest in enumerate(java_rest_fractions) if rest == 0.0]
        for i in zero_rest_notes[:5]:  # Test first 5 zero-rest notes
            self.assertEqual(melody.notes[i].rest_fraction, 0.0,
                           msg=f"Note {i+1} should have rest fraction 0.0")

    def test_midi_reader_timing_consistency(self):
        """
        Test that onset times are monotonically increasing and reasonable
        """
        midi_file_path = os.path.join(self.test_data_dir, 'midi', '0A2A.mid')
        melody = self.midi_reader.read('0A2A', midi_file_path)

        # Test that onset times are non-decreasing
        onsets = [note.onset for note in melody.notes]
        for i in range(1, len(onsets)):
            self.assertGreaterEqual(onsets[i], onsets[i-1],
                                   f"Onset times should be non-decreasing: note {i+1} onset {onsets[i]} < note {i} onset {onsets[i-1]}")

        # Test that first note starts at time 0
        self.assertEqual(melody.notes[0].onset, 0.0, "First note should start at time 0")

        # Test that timing makes musical sense (reasonable total duration)
        total_duration = onsets[-1] + melody.notes[-1].duration
        self.assertGreater(total_duration, 10.0, "Total melody should be longer than 10 quarter notes")
        self.assertLess(total_duration, 20.0, "Total melody should be shorter than 20 quarter notes")

if __name__ == '__main__':
    unittest.main()
