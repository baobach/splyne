"""
Reads Melody objects from files or streams in MIDI or ABC format.
Only the track with the most events is read as the melody.

The melody is read from the track with the most events.
"""
import music21 as m21
from .melody_reader import MelodyReader
from .melody import Melody
from .note import Note

class AbcReader(MelodyReader):
    """
    Parse the input ABC file and return a Melody object.
    """

    def read(self, melody_id, path):
        score = m21.converter.parse(path)
        melody = Melody(melody_id)
        for element in score.flatten().notes:
            if isinstance(element, m21.note.Note):
                melody.add_note(Note(
                    pitch=element.pitch.midi,
                    onset=element.offset,
                    duration=element.quarterLength
                ))
        return melody

    def accept(self, file_name):
        return file_name.lower().endswith('.abc')

class MidiReader(MelodyReader):
    """
    Parse the input MIDI file and return a Melody object.
    Implements the same logic as the Java MelodyShape MidiReader.
    """

    def read(self, melody_id, path):
        score = m21.converter.parse(path)
        melody = Melody(melody_id)

        # Extract all notes with their onset and end times
        notes_data = []
        for element in score.flatten().notes:
            if isinstance(element, m21.note.Note):
                notes_data.append({
                    'pitch': element.pitch.midi,
                    'onset': element.offset,
                    'duration': element.quarterLength,
                    'end': element.offset + element.quarterLength
                })

        # Sort by onset time to ensure proper order
        notes_data.sort(key=lambda x: x['onset'])

        # Calculate rest fractions following Java logic
        last_off = 0.0  # End time of the previous note

        for i, note_data in enumerate(notes_data):
            pitch = note_data['pitch']
            onset = note_data['onset']
            duration = note_data['duration']
            end = note_data['end']

            # Calculate rest fraction following Java formula:
            # rest = (lastOn - lastOff) / (time - lastOff)
            # where:
            # - lastOn = current note onset
            # - lastOff = previous note end time
            # - time = current note end time

            if i == 0:
                # First note: no previous note, so rest = 0
                rest_fraction = 0.0
            else:
                time_span = end - last_off  # Total time from previous note end to current note end
                gap_before = onset - last_off  # Gap before current note starts

                if time_span > 0:
                    rest_fraction = gap_before / time_span
                else:
                    rest_fraction = 0.0

            # Create the note with calculated rest fraction
            melody.add_note(Note(
                pitch=pitch,
                onset=onset,
                duration=duration,
                rest_fraction=rest_fraction
            ))

            # Update last_off for next iteration
            last_off = end

        return melody

    def accept(self, file_name):
        return file_name.lower().endswith('.mid') or file_name.lower().endswith('.midi')
