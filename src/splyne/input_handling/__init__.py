"""
This module handles input processing for MIDI and ABC files formatting them into Melody objects.
"""

from .melody import Melody
from .note import Note
from .melody_reader import MelodyReader
from .tunes_reader import MidiReader, AbcReader
from .melody_collection import MelodyCollection
from .in_memory_melody_collection import InMemoryMelodyCollection

__all__ = [
    'Melody',
    'Note',
    'MelodyReader',
    'MidiReader',
    'AbcReader',
    'MelodyCollection',
    'InMemoryMelodyCollection'
]
