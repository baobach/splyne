# Splyne Input Handling Refactoring Plan: Migration to Music21

## Overview
This document outlines a comprehensive step-by-step plan to refactor the `input_handling` module from custom `Note` and `Melody` classes to native music21 objects (`music21.note.Note` and `music21.stream.Stream`).

## Current State Analysis

### Files Affected by Refactoring:
1. **Core Classes (to be removed/modified):**
   - `src/splyne/input_handling/note.py` - Custom Note class
   - `src/splyne/input_handling/melody.py` - Custom Melody class
   - `src/splyne/input_handling/tunes_reader.py` - Uses both classes

2. **Dependent Modules:**
   - `src/splyne/comparision/ngram.py` - Heavy usage of custom classes
   - `src/splyne/input_handling/melody_collection.py` - Uses Melody interface
   - `src/splyne/input_handling/in_memory_melody_collection.py` - Stores Melody objects

3. **Tests:**
   - `tests/test_ngram.py` - Tests NGram with custom objects
   - All tests in `tests/test_input_handling.py` - Tests custom classes

4. **Examples:**
   - `examples/measure_collection_demo.py`
   - `examples/abc_chord_analysis.py`
   - `examples/melody_collection_demo.py`

### Current Custom Classes Limitations:
- **Note**: Only pitch (int), onset (float), duration (float), rest_fraction (float)
- **Melody**: Only id (str) and notes (list)
- **Missing**: Time signatures, key signatures, measures, rich pitch info, export capabilities

### Music21 Advantages:
- **Rich Note objects**: pitch.midi, pitch.name, pitch.frequency, pitch.octave
- **Rich Stream objects**: measures, time signatures, key signatures, export to MIDI/XML/ABC
- **Industry standard**: Wide ecosystem compatibility
- **Built-in analysis**: Chord detection, scale analysis, etc.

## Migration Strategy: 3-Phase Approach

### Phase 1: Create Compatibility Layer (Minimal Breaking Changes)
**Goal**: Introduce music21 objects while maintaining existing API

#### Step 1.1: Create Adapter Functions
Create `src/splyne/input_handling/adapters.py`:

```python
"""
Adapter functions to bridge between music21 objects and legacy interfaces.
"""
import music21 as m21
from typing import List, Tuple, Optional

def extract_pitch_sequence(stream: m21.stream.Stream) -> List[int]:
    """Extract MIDI pitch numbers from a music21 stream."""
    return [note.pitch.midi for note in stream.flatten().notes
            if isinstance(note, m21.note.Note)]

def extract_duration_sequence(stream: m21.stream.Stream) -> List[float]:
    """Extract quarter-length durations from a music21 stream."""
    return [note.quarterLength for note in stream.flatten().notes
            if isinstance(note, m21.note.Note)]

def extract_offset_sequence(stream: m21.stream.Stream) -> List[float]:
    """Extract onset times from a music21 stream."""
    return [note.offset for note in stream.flatten().notes
            if isinstance(note, m21.note.Note)]

def calculate_rest_fractions(stream: m21.stream.Stream) -> List[float]:
    """Calculate rest fractions using the same logic as MidiReader."""
    notes_data = []

    for element in stream.flatten().notes:
        if isinstance(element, m21.note.Note):
            notes_data.append({
                'pitch': element.pitch.midi,
                'onset': element.offset,
                'duration': element.quarterLength,
                'end': element.offset + element.quarterLength
            })

    notes_data.sort(key=lambda x: x['onset'])
    rest_fractions = []
    last_off = 0.0

    for i, note_data in enumerate(notes_data):
        onset = note_data['onset']
        end = note_data['end']

        if i == 0:
            rest_fraction = 0.0
        else:
            time_span = end - last_off
            gap_before = onset - last_off
            rest_fraction = gap_before / time_span if time_span > 0 else 0.0

        rest_fractions.append(rest_fraction)
        last_off = end

    return rest_fractions

class LegacyNote:
    """Compatibility wrapper that provides the old Note interface."""
    def __init__(self, m21_note: m21.note.Note, rest_fraction: float = 0.0):
        self._m21_note = m21_note
        self._rest_fraction = rest_fraction

    @property
    def pitch(self) -> int:
        return self._m21_note.pitch.midi

    @property
    def onset(self) -> float:
        return self._m21_note.offset

    @property
    def duration(self) -> float:
        return self._m21_note.quarterLength

    @property
    def rest_fraction(self) -> float:
        return self._rest_fraction

    def __eq__(self, other):
        if not isinstance(other, LegacyNote):
            return False
        return (self.pitch == other.pitch and
                self.onset == other.onset and
                self.duration == other.duration and
                self.rest_fraction == other.rest_fraction)

    def __repr__(self):
        return f"Note(pitch={self.pitch}, onset={self.onset}, duration={self.duration}, rest_fraction={self.rest_fraction})"

class LegacyMelody:
    """Compatibility wrapper that provides the old Melody interface."""
    def __init__(self, melody_id: str, m21_stream: m21.stream.Stream):
        self.id = melody_id
        self._m21_stream = m21_stream
        self._notes = None  # Lazy loading

    @property
    def notes(self) -> List[LegacyNote]:
        if self._notes is None:
            self._notes = self._create_legacy_notes()
        return self._notes

    def _create_legacy_notes(self) -> List[LegacyNote]:
        rest_fractions = calculate_rest_fractions(self._m21_stream)
        legacy_notes = []

        for i, note in enumerate(self._m21_stream.flatten().notes):
            if isinstance(note, m21.note.Note):
                rest_frac = rest_fractions[i] if i < len(rest_fractions) else 0.0
                legacy_notes.append(LegacyNote(note, rest_frac))

        return legacy_notes

    def add_note(self, note):
        """For backward compatibility - not recommended for new code."""
        raise NotImplementedError("Use music21 stream methods instead")

    def get_id(self) -> str:
        return self.id

    @property
    def m21_stream(self) -> m21.stream.Stream:
        """Access to the underlying music21 stream."""
        return self._m21_stream

    def __repr__(self):
        return f"Melody(id={self.id}, notes={self.notes})"
```

#### Step 1.2: Update Readers to Return Music21 Objects
Modify `src/splyne/input_handling/tunes_reader.py`:

```python
"""
Updated readers that return music21 streams with legacy compatibility.
"""
import music21 as m21
from .melody_reader import MelodyReader
from .adapters import LegacyMelody

class AbcReader(MelodyReader):
    """Parse ABC files and return music21-based melody objects."""

    def read(self, melody_id, path):
        score = m21.converter.parse(path)
        # Return compatibility wrapper
        return LegacyMelody(melody_id, score)

    def read_m21(self, melody_id, path) -> m21.stream.Stream:
        """New method that returns pure music21 stream."""
        return m21.converter.parse(path)

    def accept(self, file_name):
        return file_name.lower().endswith('.abc')

class MidiReader(MelodyReader):
    """Parse MIDI files and return music21-based melody objects."""

    def read(self, melody_id, path):
        score = m21.converter.parse(path)
        # Return compatibility wrapper
        return LegacyMelody(melody_id, score)

    def read_m21(self, melody_id, path) -> m21.stream.Stream:
        """New method that returns pure music21 stream."""
        return m21.converter.parse(path)

    def accept(self, file_name):
        return file_name.lower().endswith('.mid') or file_name.lower().endswith('.midi')
```

#### Step 1.3: Update NGram to Support Both Interfaces
Modify `src/splyne/comparision/ngram.py`:

```python
"""
Updated NGram class supporting both legacy and music21 interfaces.
"""
import music21 as m21
from typing import List, Union
from ..input_handling.adapters import LegacyNote, LegacyMelody, extract_pitch_sequence, extract_duration_sequence

class NGram:
    def __init__(self, notes: List[Union[LegacyNote, m21.note.Note]]):
        # Convert music21.note.Note to LegacyNote for backward compatibility
        if notes and isinstance(notes[0], m21.note.Note):
            self.notes = [LegacyNote(note) for note in notes]
        else:
            self.notes = notes

    @classmethod
    def from_m21_notes(cls, m21_notes: List[m21.note.Note], rest_fractions: List[float] = None):
        """Create NGram directly from music21 notes."""
        if rest_fractions is None:
            rest_fractions = [0.0] * len(m21_notes)

        legacy_notes = []
        for i, note in enumerate(m21_notes):
            rest_frac = rest_fractions[i] if i < len(rest_fractions) else 0.0
            legacy_notes.append(LegacyNote(note, rest_frac))

        return cls(legacy_notes)

    # ... rest of the existing methods remain the same ...

    @staticmethod
    def get_ngrams(melody: Union[LegacyMelody, m21.stream.Stream], n: int) -> List['NGram']:
        """Generate n-grams from melody (supports both legacy and music21)."""
        if isinstance(melody, m21.stream.Stream):
            # Convert music21 stream to legacy format for now
            from ..input_handling.adapters import calculate_rest_fractions
            notes = []
            rest_fractions = calculate_rest_fractions(melody)

            for i, note in enumerate(melody.flatten().notes):
                if isinstance(note, m21.note.Note):
                    rest_frac = rest_fractions[i] if i < len(rest_fractions) else 0.0
                    notes.append(LegacyNote(note, rest_frac))
        else:
            # Legacy melody object
            notes = melody.notes

        if len(notes) < n:
            return []

        ngrams = []
        for i in range(len(notes) - n + 1):
            ngram_notes = notes[i:i + n]
            ngrams.append(NGram(ngram_notes))

        return ngrams
```

### Phase 2: Modernize Core Components
**Goal**: Replace legacy wrappers with native music21 usage

#### Step 2.1: Create New Music21-Native NGram Class
Create `src/splyne/comparision/m21_ngram.py`:

```python
"""
Modern NGram implementation using native music21 objects.
"""
import music21 as m21
from typing import List

class M21NGram:
    """NGram implementation using native music21.note.Note objects."""

    def __init__(self, notes: List[m21.note.Note]):
        self.notes = notes

    def get_null_span(self) -> 'M21NGram':
        """Create a null span where all notes have the same pitch as the first note."""
        if not self.notes:
            return M21NGram([])

        first_pitch = self.notes[0].pitch
        null_notes = []

        for note in self.notes:
            null_note = m21.note.Note()
            null_note.pitch = first_pitch
            null_note.offset = note.offset
            null_note.quarterLength = note.quarterLength
            null_notes.append(null_note)

        return M21NGram(null_notes)

    def __str__(self) -> str:
        """String representation showing pitches and durations."""
        if not self.notes:
            return "[]"

        note_strs = []
        for note in self.notes:
            note_str = f"{{{note.pitch.midi},{note.quarterLength}}}"
            note_strs.append(note_str)

        return "[" + ",".join(note_strs) + "]"

    @staticmethod
    def get_ngrams(stream: m21.stream.Stream, n: int) -> List['M21NGram']:
        """Generate n-grams from a music21 stream."""
        notes = [note for note in stream.flatten().notes
                if isinstance(note, m21.note.Note)]

        if len(notes) < n:
            return []

        ngrams = []
        for i in range(len(notes) - n + 1):
            ngram_notes = notes[i:i + n]
            ngrams.append(M21NGram(ngram_notes))

        return ngrams

    def __eq__(self, other) -> bool:
        if not isinstance(other, M21NGram):
            return False

        if len(self.notes) != len(other.notes):
            return False

        for i, note in enumerate(self.notes):
            other_note = other.notes[i]
            if (note.pitch.midi != other_note.pitch.midi or
                note.quarterLength != other_note.quarterLength):
                return False

        return True

    def __hash__(self) -> int:
        return hash(tuple((note.pitch.midi, note.quarterLength) for note in self.notes))

    def __repr__(self) -> str:
        return f"M21NGram(notes={self.notes})"
```

#### Step 2.2: Update Melody Collections
Modify `src/splyne/input_handling/melody_collection.py`:

```python
"""
Updated melody collection supporting music21 streams.
"""
from abc import ABC, abstractmethod
from typing import Iterator, Union
import music21 as m21
from .adapters import LegacyMelody

class MelodyCollection(ABC):
    """Abstract base class for managing collections of melodies."""

    @abstractmethod
    def add(self, melody: Union[LegacyMelody, m21.stream.Stream], melody_id: str = None) -> None:
        """Add a melody to the collection."""
        pass

    @abstractmethod
    def get(self, melody_id: str) -> Union[LegacyMelody, m21.stream.Stream]:
        """Retrieve a melody by its ID."""
        pass

    @abstractmethod
    def get_m21_stream(self, melody_id: str) -> m21.stream.Stream:
        """Get the underlying music21 stream for a melody."""
        pass
```

### Phase 3: Complete Migration
**Goal**: Remove legacy code and use pure music21

#### Step 3.1: Update All Dependent Code
- Update all example files to use music21 objects
- Update all tests to use the new interfaces
- Remove legacy wrapper classes

#### Step 3.2: Clean Up Architecture
- Remove `src/splyne/input_handling/note.py`
- Remove `src/splyne/input_handling/melody.py`
- Remove adapter wrapper classes
- Update `__init__.py` imports

## Implementation Timeline

### Week 1: Phase 1 Implementation
- [ ] Create `adapters.py` with compatibility wrappers
- [ ] Update readers to support both interfaces
- [ ] Update NGram class to support both interfaces
- [ ] Ensure all existing tests still pass

### Week 2: Phase 2 Implementation
- [ ] Create new M21NGram class
- [ ] Update melody collections
- [ ] Write comprehensive tests for new components
- [ ] Update examples to demonstrate new capabilities

### Week 3: Phase 3 Implementation
- [ ] Migrate all dependent code
- [ ] Remove legacy classes and wrappers
- [ ] Clean up imports and architecture
- [ ] Final testing and documentation

## Testing Strategy

1. **Regression Testing**: Ensure all existing functionality works during Phase 1
2. **Feature Testing**: Test new music21-based features in Phase 2
3. **Integration Testing**: Full system testing in Phase 3
4. **Performance Testing**: Compare performance of old vs new implementations

## Benefits After Migration

1. **Rich Musical Data**: Access to time signatures, key signatures, measures
2. **Export Capabilities**: Save to MIDI, MusicXML, ABC, PNG formats
3. **Analysis Features**: Built-in chord detection, scale analysis
4. **Industry Standard**: Better integration with music software ecosystem
5. **Future-Proof**: Leveraging actively maintained music21 library

## Risk Mitigation

1. **Backward Compatibility**: Phase 1 maintains existing API
2. **Incremental Migration**: Step-by-step approach reduces risk
3. **Comprehensive Testing**: Regression tests catch breaking changes
4. **Rollback Plan**: Keep legacy code until Phase 3 is complete

## Files to Create/Modify

### New Files:
- `src/splyne/input_handling/adapters.py`
- `src/splyne/comparision/m21_ngram.py`
- `tests/test_m21_ngram.py`
- `examples/music21_analysis_demo.py`

### Modified Files:
- `src/splyne/input_handling/tunes_reader.py`
- `src/splyne/input_handling/melody_collection.py`
- `src/splyne/input_handling/in_memory_melody_collection.py`
- `src/splyne/comparision/ngram.py`
- `tests/test_ngram.py`
- All example files
- `src/splyne/input_handling/__init__.py`

### Files to Remove (Phase 3):
- `src/splyne/input_handling/note.py`
- `src/splyne/input_handling/melody.py`

This plan provides a comprehensive, low-risk approach to modernizing your input handling system while preserving existing functionality and opening up new possibilities with music21's rich feature set.
