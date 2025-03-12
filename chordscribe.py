import librosa
import numpy as np
import sys

# Constants
SAMPLE_RATE = 22050
HOP_LENGTH = 512

def detect_chords(audio_file):
    """
    Detect chords from an audio file and print them with timestamps.
    """
    try:
        # Load audio file
        print(f"Loading audio file: {audio_file}")
        y, sr = librosa.load(audio_file, sr=SAMPLE_RATE)

        # Compute chromagram (pitch class profile)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP_LENGTH)

        # Estimate tempo and beats (to segment audio into meaningful chunks)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=HOP_LENGTH)
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=HOP_LENGTH)

        # Simplified chord detection using chromagram
        chords = []
        for i in range(len(beats) - 1):
            # Extract chroma segment between beats
            start_frame = beats[i]
            end_frame = beats[i + 1]
            chroma_segment = chroma[:, start_frame:end_frame]

            # Average chroma values over the segment
            chroma_mean = np.mean(chroma_segment, axis=1)

            # Basic chord estimation (heuristic: strongest pitch classes)
            chord = estimate_chord(chroma_mean)
            time = beat_times[i]
            chords.append((time, chord))

        return chords

    except Exception as e:
        print(f"Error processing audio: {e}")
        return []

def estimate_chord(chroma):
    """
    Estimate a simple major/minor chord from chroma vector.
    This is a basic heuristic - could be improved with ML or templates.
    """
    # Major and minor chord templates (simplified)
    major_template = np.roll([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], 0)
    minor_template = np.roll([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], 0)

    # Pitch class names
    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Find best matching root note
    best_score_major = -1
    best_score_minor = -1
    best_root_major = 0
    best_root_minor = 0

    for root in range(12):
        rolled_major = np.roll(major_template, root)
        rolled_minor = np.roll(minor_template, root)
        
        score_major = np.sum(chroma * rolled_major)
        score_minor = np.sum(chroma * rolled_minor)

        if score_major > best_score_major:
            best_score_major = score_major
            best_root_major = root
        if score_minor > best_score_minor:
            best_score_minor = score_minor
            best_root_minor = root

    # Decide between major and minor
    if best_score_major > best_score_minor:
        return f"{pitch_classes[best_root_major]}"
    else:
        return f"{pitch_classes[best_root_minor]}m"

def main():
    # Check for command-line argument
    if len(sys.argv) != 2:
        print("Usage: python chordscribe.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    chords = detect_chords(audio_file)

    # Print results
    if chords:
        print("\nDetected Chords:")
        for time, chord in chords:
            print(f"Time: {time:.2f}s - Chord: {chord}")
    else:
        print("No chords detected.")

if __name__ == "__main__":
    main()