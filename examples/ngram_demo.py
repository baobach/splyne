#!/usr/bin/env python3
"""
Simple NGram Demo - Generate 4-grams from a MIDI file and display their values.
"""

import os
import sys

from splyne.input_handling.tunes_reader import MidiReader
from splyne.comparision.ngram import NGram


def main():
    """Generate 4-grams from a MIDI file and display them."""
    print("NGram Demo - Generating 4-grams")
    print("=" * 40)

    # Load the MIDI file
    midi_reader = MidiReader()
    test_data_dir = os.path.join(os.path.dirname(__file__), '../tests/test_data/midi')
    midi_file_path = os.path.join(test_data_dir, '0A2A.mid')

    if not os.path.exists(midi_file_path):
        print(f"Error: MIDI file not found at {midi_file_path}")
        return

    # Read the melody
    melody = midi_reader.read('0A2A', midi_file_path)
    print(f"Loaded melody with {len(melody.notes)} notes")

    # Generate 4-grams
    ngrams = NGram.get_ngrams(melody, 4)
    print(f"Generated {len(ngrams)} 4-grams")
    print()

    # Display each 4-gram
    for i, ngram in enumerate(ngrams):
        print(f"4-gram {i+1:2d}: {ngram}")


if __name__ == "__main__":
    main()
