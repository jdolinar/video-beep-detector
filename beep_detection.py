import logging
import datetime
import argparse
import os
from scipy.signal import find_peaks
from moviepy.editor import VideoFileClip
import librosa
import numpy as np

def setup_logging(verbosity, quiet):
    if quiet:
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(len(levels) - 1, verbosity)]  # Ensure the level is within bounds
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_audio(video_path, audio_output_path):
    logging.info(f"Extracting audio from {video_path} to {audio_output_path}")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(filename=audio_output_path, verbose=False, logger=None)
    logging.debug("Audio extraction completed")

def load_audio(audio_path):
    logging.info(f"Loading audio from {audio_path}")
    y, sr = librosa.load(audio_path, sr=None)
    logging.debug(f"Audio loaded with sample rate {sr}")
    return y, sr

def detect_beep_pairs(y, sr, beep_freq=2020, beep_duration=0.032, interval=0.165, pair_interval_low=1.6, pair_interval_high=2.0, sensitivity=1.0):
    logging.info("Starting beep detection")

    # Perform STFT to analyze frequency content
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr)

    # Find the index of the target frequency
    target_idx = np.argmin(np.abs(freqs - beep_freq))
    logging.debug(f"Target frequency index: {target_idx}")

    # Detect peaks in the target frequency bin
    freq_bin = S[target_idx]
    peaks, _ = find_peaks(freq_bin, height=np.mean(freq_bin) + sensitivity * np.std(freq_bin))

    logging.info(f"Detected {len(peaks)} potential beep locations")

    # Convert peak locations to times
    beep_times = peaks * 512 / sr
    logging.debug(f"Beep times: {beep_times}")

    # Detect pairs of beeps
    detected_pairs = []
    for i in range(len(beep_times) - 1):
        if np.abs(beep_times[i+1] - beep_times[i] - interval) < 0.11:
            detected_pairs.append(beep_times[i])

    logging.info(f"Detected {len(detected_pairs)} pairs of beeps")
    logging.debug(f"Detected pairs: {detected_pairs}")

    # Find pairs followed by another pair within the tolerance interval
    valid_pairs = []
    for i in range(len(detected_pairs) - 1):
        if pair_interval_low <= detected_pairs[i+1] - detected_pairs[i] <= pair_interval_high:
            valid_pairs.append(detected_pairs[i])

    logging.warning(f"Detected {len(valid_pairs)} valid beep pairs")

    # Convert times to HH:MM:SS.thousand format with zero-padded hours
    formatted_pairs = [format_timestamp(t) for t in valid_pairs]

    return formatted_pairs

def format_timestamp(seconds):
    timestamp = str(datetime.timedelta(seconds=seconds))
    if len(timestamp.split(":")[0]) == 1:
        timestamp = "0" + timestamp
    return timestamp

def process_videos_in_folder(folder_path, output_file, verbosity, quiet):
    setup_logging(verbosity, quiet)
    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    logging.info(f"Found {len(video_files)} video files in {folder_path}")

    with open(output_file, 'w') as out_file:
        for video_file in video_files:
            video_path = os.path.join(folder_path, video_file)
            audio_output_path = "extracted_audio.wav"

            # Extract audio from video
            extract_audio(video_path, audio_output_path)

            # Load extracted audio
            y, sr = load_audio(audio_output_path)

            # Detect beep pairs
            beep_pairs = detect_beep_pairs(y, sr, sensitivity=3)

            # Write results to the output file
            if beep_pairs:
                timestamps = ", ".join(beep_pairs)
                out_file.write(f"{video_file} - {timestamps}\n")

            # Cleanup the extracted audio file
            os.remove(audio_output_path)
            logging.debug("")

def main():
    print("Viofo Video Beep detector")
    print()
    parser = argparse.ArgumentParser(description="Detect beep pairs in all MP4 video files in a folder.")
    parser.add_argument("folder_path", help="Path to the folder containing MP4 video files")
    parser.add_argument("output_file", help="Path to the output file where results will be saved")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (only errors will be logged)")
    parser.add_argument("-v", "--verbosity", type=int, default=1, help="Verbosity level: 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG")
    args = parser.parse_args()
    print()

    process_videos_in_folder(args.folder_path, args.output_file, args.verbosity, args.quiet)

if __name__ == "__main__":
    main()
