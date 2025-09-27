## 09/24/2025
- Update `input_handling/tunes_reader.py` logic to compute rest durations correctly.
- Create test cases for `input_handling/tunes_reader.py`.
- Add midi and abc files for testing in `tests/test_data/`.
Plans:
- Generate a test ABC files from the MIDI files.
- Update the `AbcReader` to show consistency between MIDI and ABC parsing.
- Implement `BSpline` module to fit the melody to B-splines curves.
Issues:
- Program cannot handle multiple voices in MIDI and ABC files yet.
- `rest` is not used in the current implementation.

## 09/26/2025
- Create a `comparison` module to compare the output of the melody from a query to the collection of melodies.
- Implemented `NGram` class to generate n-grams from a sequence of notes.
- Implemented `BSpline` module to fit the melody to B-splines curves.
ISSUE:
The current implementation of the `input_handling` module is not as powerful as music21. Consider refactor the code to use music21 Note and Stream object rather than oldNote and oldMelody object which is not as powerful.
