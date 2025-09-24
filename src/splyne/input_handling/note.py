"""
This class represents a musical note with its pitch, duration, and onset time.
"""

class Note:
    def __init__(self, pitch, onset, duration, rest_fraction=0.0):
        """
        Initializes a Note object.

        Args:
            pitch (int): MIDI pitch number.
            onset (float): Onset time in seconds or ticks.
            duration (float): Duration in seconds or ticks.
            rest_fraction (float): Fraction of the duration that is a rest.
        """
        self.pitch = pitch
        self.onset = onset
        self.duration = duration
        self.rest_fraction = rest_fraction

    def __repr__(self):
        """
        Returns a string representation of the note.

        Returns:
            str: String representation.
        """
        return f"Note(pitch={self.pitch}, onset={self.onset}, duration={self.duration}, rest_fraction={self.rest_fraction})"
