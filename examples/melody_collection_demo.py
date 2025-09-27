"""
Example usage of MelodyCollection and InMemoryMelodyCollection classes.

This script demonstrates how to:
1. Load MIDI files from a directory
2. Load MIDI files from a ZIP archive
3. Add, retrieve, and iterate over melodies
4. Handle errors gracefully
"""

import os
import tempfile
import zipfile
from pathlib import Path

from splyne.input_handling import InMemoryMelodyCollection, Melody, Note


def demo_directory_loading():
    """Demonstrate loading MIDI files from a directory."""
    print("=== Demo: Loading MIDI files from directory ===")
    
    # Path to test MIDI files
    test_data_dir = Path(__file__).parent.parent / "tests" / "test_data" / "midi"
    
    if not test_data_dir.exists():
        print(f"Test data directory not found: {test_data_dir}")
        return
    
    try:
        # Create collection from directory
        collection = InMemoryMelodyCollection(test_data_dir, "Demo MIDI Collection")
        
        print(f"Collection name: {collection.get_name()}")
        print(f"Number of melodies: {collection.size()}")
        print(f"Melody IDs: {collection.list_melody_ids()[:5]}...")  # Show first 5
        
        # Get information about the first melody
        if collection.size() > 0:
            first_melody_id = collection.list_melody_ids()[0]
            first_melody = collection.get(first_melody_id)
            print(f"\nFirst melody '{first_melody_id}':")
            print(f"  Number of notes: {len(first_melody.notes)}")
            if first_melody.notes:
                first_note = first_melody.notes[0]
                print(f"  First note: pitch={first_note.pitch}, onset={first_note.onset}, duration={first_note.duration}")
        
    except Exception as e:
        print(f"Error loading from directory: {e}")


def demo_zip_loading():
    """Demonstrate loading MIDI files from a ZIP archive."""
    print("\n=== Demo: Loading MIDI files from ZIP archive ===")
    
    test_data_dir = Path(__file__).parent.parent / "tests" / "test_data" / "midi"
    
    if not test_data_dir.exists():
        print(f"Test data directory not found: {test_data_dir}")
        return
    
    # Create a temporary ZIP file with some MIDI files
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "demo_midi.zip"
        
        # Get first few MIDI files
        midi_files = list(test_data_dir.glob("*.mid"))[:3]
        
        if not midi_files:
            print("No MIDI files found in test data directory")
            return
        
        try:
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for midi_file in midi_files:
                    zip_file.write(midi_file, midi_file.name)
            
            print(f"Created ZIP file with {len(midi_files)} MIDI files")
            
            # Load collection from ZIP
            collection = InMemoryMelodyCollection(zip_path, "Demo ZIP Collection")
            
            print(f"Collection name: {collection.get_name()}")
            print(f"Number of melodies: {collection.size()}")
            print(f"Melody IDs: {collection.list_melody_ids()}")
            
        except Exception as e:
            print(f"Error loading from ZIP: {e}")


def demo_manual_operations():
    """Demonstrate manual melody operations."""
    print("\n=== Demo: Manual melody operations ===")
    
    test_data_dir = Path(__file__).parent.parent / "tests" / "test_data" / "midi"
    
    if not test_data_dir.exists():
        print("Creating empty collection for manual operations demo")
        # Create empty collection using a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            collection = InMemoryMelodyCollection(temp_dir, "Manual Demo Collection")
    else:
        collection = InMemoryMelodyCollection(test_data_dir, "Manual Demo Collection")
    
    print(f"Initial collection size: {collection.size()}")
    
    try:
        # Create and add a custom melody
        custom_melody = Melody("custom_melody")
        custom_melody.add_note(Note(pitch=60, onset=0.0, duration=1.0))  # C4
        custom_melody.add_note(Note(pitch=64, onset=1.0, duration=1.0))  # E4
        custom_melody.add_note(Note(pitch=67, onset=2.0, duration=1.0))  # G4
        
        collection.add(custom_melody)
        print(f"Added custom melody. New size: {collection.size()}")
        
        # Retrieve and display the custom melody
        retrieved = collection.get("custom_melody")
        print(f"Retrieved melody '{retrieved.id}' with {len(retrieved.notes)} notes")
        
        # Check if melody exists
        print(f"Collection contains 'custom_melody': {collection.contains('custom_melody')}")
        print(f"Collection contains 'nonexistent': {collection.contains('nonexistent')}")
        
        # Iterate over all melodies
        print(f"\nIterating over {collection.size()} melodies:")
        for i, melody in enumerate(collection):
            print(f"  {i+1}. Melody '{melody.id}' with {len(melody.notes)} notes")
            if i >= 4:  # Limit output
                print("  ...")
                break
        
        # Remove the custom melody
        collection.remove("custom_melody")
        print(f"Removed custom melody. New size: {collection.size()}")
        
    except Exception as e:
        print(f"Error in manual operations: {e}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n=== Demo: Error handling ===")
    
    try:
        # Try to load from nonexistent path
        collection = InMemoryMelodyCollection("/nonexistent/path")
    except FileNotFoundError as e:
        print(f"Expected error for nonexistent path: {e}")
    
    # Create a valid collection for other error demonstrations
    with tempfile.TemporaryDirectory() as temp_dir:
        collection = InMemoryMelodyCollection(temp_dir, "Error Demo Collection")
        
        try:
            # Try to get nonexistent melody
            collection.get("nonexistent")
        except KeyError as e:
            print(f"Expected error for nonexistent melody: {e}")
        
        try:
            # Try to remove nonexistent melody
            collection.remove("nonexistent")
        except KeyError as e:
            print(f"Expected error for removing nonexistent melody: {e}")
        
        try:
            # Try to add duplicate melody
            melody1 = Melody("duplicate")
            melody2 = Melody("duplicate")
            collection.add(melody1)
            collection.add(melody2)
        except ValueError as e:
            print(f"Expected error for duplicate melody: {e}")


def main():
    """Run all demo functions."""
    print("MelodyCollection Demo Script")
    print("=" * 50)
    
    demo_directory_loading()
    demo_zip_loading()
    demo_manual_operations()
    demo_error_handling()
    
    print("\n" + "=" * 50)
    print("Demo completed!")


if __name__ == "__main__":
    main()