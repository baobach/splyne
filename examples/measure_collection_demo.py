#!/usr/bin/env python3
"""
ABC Measure Collection Demo - Extract collections of notes organized by measures from ABC files.
"""

import os
import sys
import music21 as m21

from splyne.input_handling.tunes_reader import AbcReader
from splyne.input_handling.note import Note
from splyne.input_handling.melody import Melody


class MeasureCollection:
    """A collection of notes that represent one measure."""

    def __init__(self, measure_number, notes):
        self.measure_number = measure_number
        self.notes = notes

    def __str__(self):
        note_strs = [f"({note.pitch},{note.duration})" for note in self.notes]
        total_duration = self.get_total_duration()
        return f"Measure {self.measure_number}: [{', '.join(note_strs)}] (total: {total_duration})"

    def get_pitches(self):
        """Get just the pitches from this measure."""
        return [note.pitch for note in self.notes]

    def get_total_duration(self):
        """Calculate the total duration of all notes in this measure."""
        return sum(note.duration for note in self.notes)


def extract_measures_from_abc(abc_file_path):
    """
    Extract measures from an ABC file using music21 to access measure structure.

    Args:
        abc_file_path (str): Path to the ABC file

    Returns:
        list: List of MeasureCollection objects
    """
    print(f"Extracting measures from ABC file: {os.path.basename(abc_file_path)}")
    print("WARNING: music21's ABC parser may not correctly handle measure boundaries,")
    print("         repeats, endings, and chords. Results may not match actual ABC structure.")

    try:
        # Parse the ABC file with music21 to get measure structure
        score = m21.converter.parse(abc_file_path)

        # Analyze time signature
        time_sigs = score.getTimeSignatures()
        if time_sigs:
            time_sig = time_sigs[0]
            # Correct calculation: numerator * (1/denominator) in quarter note units
            # For 3/8: 3 * (1/8) = 3/8 = 0.375 quarter notes
            expected_duration = time_sig.numerator / time_sig.denominator
            print(f"Time signature: {time_sig.numerator}/{time_sig.denominator}")
            print(f"Expected measure duration: {expected_duration} quarter notes ({time_sig.numerator}/{time_sig.denominator} = {expected_duration})")
        else:
            expected_duration = None
            print("No time signature found")

        # Debug: Let's see what we actually got
        print(f"Score type: {type(score)}")
        print(f"Score elements: {len(list(score.elements))}")

        # Try different ways to access measures
        measures = score.getElementsByClass(m21.stream.Measure)
        print(f"Found {len(measures)} measures using getElementsByClass")

        # Alternative: try to get measures from parts
        parts = score.getElementsByClass(m21.stream.Part)
        print(f"Found {len(parts)} parts")

        if parts:
            for i, part in enumerate(parts):
                part_measures = part.getElementsByClass(m21.stream.Measure)
                print(f"  Part {i}: {len(part_measures)} measures")
                if not measures and part_measures:  # Use part measures if direct measures failed
                    measures = part_measures

        # If still no measures, try flattening and looking for notes directly
        if not measures:
            print("No measures found, trying to extract notes directly...")
            flattened = score.flatten()
            all_notes = flattened.notes
            print(f"Found {len(all_notes)} notes in flattened score")

            # Create one big "measure" with all notes if we can't find measure structure
            if all_notes:
                measure_notes = []
                for element in all_notes:
                    if isinstance(element, m21.note.Note):
                        note = Note(
                            pitch=element.pitch.midi,
                            onset=element.offset,
                            duration=element.quarterLength,
                            rest_fraction=0.0
                        )
                        measure_notes.append(note)

                if measure_notes:
                    measure_collection = MeasureCollection(1, measure_notes)
                    return [measure_collection]

        measure_collections = []

        for i, measure in enumerate(measures):
            measure_notes = []

            # Extract notes from this measure
            for element in measure.notes:
                if isinstance(element, m21.note.Note):
                    note = Note(
                        pitch=element.pitch.midi,
                        onset=element.offset,
                        duration=element.quarterLength,
                        rest_fraction=0.0  # ABC reader doesn't calculate rest fractions like MIDI
                    )
                    measure_notes.append(note)

            if measure_notes:  # Only add measures that have notes
                measure_collection = MeasureCollection(i + 1, measure_notes)

                # Validate measure duration if we have time signature info
                if expected_duration is not None:
                    actual_duration = measure_collection.get_total_duration()
                    if abs(actual_duration - expected_duration) > 0.01:  # Allow small floating point differences
                        print(f"  WARNING: Measure {i+1} duration {actual_duration} != expected {expected_duration}")

                measure_collections.append(measure_collection)

        return measure_collections

    except Exception as e:
        print(f"Error extracting measures from ABC: {e}")
        return []


def demo_abc_measures():
    """Demonstrate measure extraction from ABC file."""
    print("\n" + "="*60)
    print("ABC MEASURE EXTRACTION DEMO")
    print("="*60)

    abc_file_path = './tests/test_data/fur_elise_short.abc'

    if not os.path.exists(abc_file_path):
        print(f"ABC file not found: {abc_file_path}")
        return

    measures = extract_measures_from_abc(abc_file_path)

    if measures:
        print(f"\nExtracted {len(measures)} measures from ABC file:")
        for measure in measures:
            print(f"  {measure}")
    else:
        print("No measures extracted from ABC file")


def main():
    """Run ABC measure extraction demo."""
    print("ABC MEASURE COLLECTION DEMO")
    print("Shows how to extract collections of notes organized by measures from ABC files")

    demo_abc_measures()


if __name__ == "__main__":
    main()
