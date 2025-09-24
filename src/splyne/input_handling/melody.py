"""
This class represents a musical melody, which is a sequence of notes.
"""

class Melody:
    def __init__(self, melody_id):
        """
        Initializes a Melody object.

        Args:
            melody_id (str): Unique identifier for the melody.
        """
        self.id = melody_id
        self.notes = []  # List to store Note objects

    def add_note(self, note):
        """
        Adds a Note object to the melody.

        Args:
            note (Note): The Note object to add.
        """
        self.notes.append(note)

    def get_id(self):
        """
        Returns the unique ID of the melody.

        Returns:
            str: The unique ID.
        """
        return self.id

    def __repr__(self):
        """
        Returns a string representation of the melody.

        Returns:
            str: String representation.
        """
        return f"Melody(id={self.id}, notes={self.notes})"
