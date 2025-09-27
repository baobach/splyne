#!/usr/bin/env python3
"""
ABC Chord Analysis Demo - Show how chords are handled in ABC files.
"""

import os
import sys
import music21 as m21

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from splyne.input_handling.note import Note


def analyze_abc_chords():
    """Analyze how ABC chords are parsed by music21."""
    abc_file_path = os.path.join(os.path.dirname(__file__), '../tests/test_data/fur_elise_short.abc')

    print("ABC CHORD ANALYSIS")
    print("=" * 50)

    if not os.path.exists(abc_file_path):
        print(f"ABC file not found: {abc_file_path}")
        return

    # Parse the ABC file
    score = m21.converter.parse(abc_file_path)
    parts = score.getElementsByClass(m21.stream.Part)

    if not parts:
        print("No parts found in ABC file")
        return

    # Look at the first part
    part = parts[1] if len(parts) > 1 else parts[0]  # Use part 1 as shown in your output
    measures = part.getElementsByClass(m21.stream.Measure)

    print(f"Analyzing {len(measures)} measures for chord content...")

    chord_measures = []

    for i, measure in enumerate(measures[:10]):  # Check first 10 measures
        print(f"\nMeasure {i+1}:")

        # Look for chords in this measure
        chords = measure.getElementsByClass(m21.chord.Chord)
        notes = measure.getElementsByClass(m21.note.Note)
        rests = measure.getElementsByClass(m21.note.Rest)

        print(f"  - {len(notes)} individual notes")
        print(f"  - {len(chords)} chords")
        print(f"  - {len(rests)} rests")

        # Show chord details
        for j, chord in enumerate(chords):
            pitches = [n.pitch.midi for n in chord.notes]
            print(f"    Chord {j+1}: pitches {pitches} at offset {chord.offset}, duration {chord.quarterLength}")
            chord_measures.append((i+1, pitches, chord.offset, chord.quarterLength))

        # Show individual notes
        for j, note in enumerate(notes):
            print(f"    Note {j+1}: pitch {note.pitch.midi} at offset {note.offset}, duration {note.quarterLength}")

    print(f"\nSummary:")
    print(f"Found {len(chord_measures)} chords in the first 10 measures")

    if chord_measures:
        print("\nChord details:")
        for measure_num, pitches, offset, duration in chord_measures:
            print(f"  Measure {measure_num}: Chord {pitches} (offset: {offset}, duration: {duration})")

        print(f"\nThe issue: Your [CA] chord from measure 9 appears as:")
        print(f"  - Two notes with the same onset time")
        print(f"  - Current Melody class can only store one note per time point")
        print(f"  - This is why some chord notes might be missing or overlapping")


def show_abc_notation_examples():
    """Show how different ABC notations should be interpreted."""
    print("\n" + "=" * 50)
    print("ABC NOTATION GUIDE")
    print("=" * 50)

    examples = [
        ("|1 [CA] z e/^d/ :|", "Measure with first ending: chord [CA], rest z, notes e and ^d (D#)"),
        ("[CA]", "Chord: C and A played simultaneously"),
        ("z", "Rest"),
        ("e/^d/", "Two eighth notes: E and D# (^ means sharp)"),
        ("|:", "Repeat start"),
        (":|", "Repeat end"),
        ("|1", "First ending (volta 1)"),
        ("|2", "Second ending (volta 2)")
    ]

    for notation, explanation in examples:
        print(f"  {notation:<15} -> {explanation}")


def main():
    """Run the chord analysis demo."""
    analyze_abc_chords()
    show_abc_notation_examples()


if __name__ == "__main__":
    main()
