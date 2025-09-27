"""
This module implements the NGram class for generating and representing n-grams from a melody.
An NGram represents a sequence of Note objects and provides methods for n-gram operations.
"""

from typing import List
from ..input_handling.note import Note
from ..input_handling.melody import Melody


class NGram:
    """
    Represents a sequence of Note objects and provides methods for n-gram operations.
    """

    def __init__(self, notes: List[Note]):
        """
        Initializes an NGram object with a list of Note objects.

        Args:
            notes (List[Note]): A list of Note objects representing the n-gram.
        """
        self.notes = notes

    def get_null_span(self) -> 'NGram':
        """
        Returns a "null" n-gram where all notes have the same pitch as the first note.
        This preserves the onset, duration, and rest fraction of each note while
        normalizing the pitch to create a rhythmic pattern.

        Returns:
            NGram: A new NGram where all notes have the same pitch as the first note.
        """
        if not self.notes:
            return NGram([])

        first_pitch = self.notes[0].pitch
        null_notes = []

        for note in self.notes:
            null_note = Note(
                pitch=first_pitch,
                onset=note.onset,
                duration=note.duration,
                rest_fraction=note.rest_fraction
            )
            null_notes.append(null_note)

        return NGram(null_notes)

    def __str__(self) -> str:
        """
        Returns a string representation of the n-gram in the format
        {pitch,duration,rest_fraction} for each note.

        Returns:
            str: String representation of the n-gram.
        """
        if not self.notes:
            return ""

        note_strings = []
        for note in self.notes:
            note_str = f"{{{note.pitch},{note.duration},{note.rest_fraction}}}"
            note_strings.append(note_str)

        return "".join(note_strings)

    @staticmethod
    def get_ngrams(melody: Melody, n: int) -> List['NGram']:
        """
        Generates a list of n-grams from a melody.

        Args:
            melody (Melody): The melody object to generate n-grams from.
            n (int): The size of each n-gram (number of notes).

        Returns:
            List[NGram]: A list of NGram objects representing all possible n-grams
                        from the melody.
        """
        if n <= 0:
            return []

        if len(melody.notes) < n:
            return []

        ngrams = []
        for i in range(len(melody.notes) - n + 1):
            ngram_notes = melody.notes[i:i + n]
            ngrams.append(NGram(ngram_notes))

        return ngrams

    def __eq__(self, other) -> bool:
        """
        Checks equality between two NGram objects.

        Args:
            other (NGram): Another NGram object to compare with.

        Returns:
            bool: True if the NGrams are equal, False otherwise.
        """
        if not isinstance(other, NGram):
            return False

        if len(self.notes) != len(other.notes):
            return False

        for i, note in enumerate(self.notes):
            other_note = other.notes[i]
            if (note.pitch != other_note.pitch or
                note.duration != other_note.duration or
                note.rest_fraction != other_note.rest_fraction):
                return False

        return True

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the NGram object.

        Returns:
            str: Detailed string representation.
        """
        return f"NGram(notes={self.notes})"
