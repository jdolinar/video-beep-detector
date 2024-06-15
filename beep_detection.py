import logging
import datetime
import argparse
import os
from scipy.signal import find_peaks
from moviepy.editor import VideoFileClip
import librosa
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_audio(video_path, audio_output_path):
    logging.info(f"Extracting audio from {video_path} to {audio_output_path}")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path)
    logging.info("Audio extraction completed")

def load_audio(audio_path):
    logging.info(f"Loading audio from {audio_path}")
    y, sr = librosa.load(audio_path, sr=None)
    logging.info(f"Audio loaded with sample rate {sr}")
    return y, sr

def detect_beep_pairs(y, sr, beep_freq=2020, beep_duration=0.032, interval=0.165, pair_interval=2.0, tolerance=0.1, sensitivity=1.0):
    logging.info("Starting beep detection")

    # Convert times to samples
    beep_duration_samples = int(sr * beep_duration)
    interval_samples = int(sr * interval)
    pair_interval_samples = int(sr * pair_interval)

    # Perform STFT to analyze frequency content
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr)

    # Find the index of the target frequency
    target_idx = np.argmin(np.abs(freqs - beep_freq))
    logging.info(f"Target frequency index: {target_idx}")

    # Detect peaks in the target frequency bin
    freq_bin = S[target_idx]
    peaks, _ = find_peaks(freq_bin, height=np.mean(freq_bin) + sensitivity * np.std(freq_bin))

    logging.info(f"Detected {len(peaks)} potential beep locations")

    # Convert peak locations to times
    beep_times = peaks * 512 / sr

    # Detect pairs of beeps
    detected_pairs = []
    for i in range(len(beep_times) - 1):
        if np.abs(beep_times[i+1] - beep_times[i] - interval) < 0.02:
            detected_pairs.append(beep_times[i])

    logging.info(f"Detected {len(detected_pairs)} pairs of beeps")

    # Find pairs followed by another pair within the tolerance interval
    valid_pairs = []
    for i in range(len(detected_pairs) - 1):
        if pair_interval - tolerance <= detected_pairs[i+1] - detected_pairs[i] <= pair_interval + tolerance:
            valid_pairs.append(detected_pairs[i])

    logging.info(f"Detected {len(valid_pairs)} valid beep pairs")

    # Convert times to HH:MM:SS.thousand format with zero-padded hours
    formatted_pairs = [format_timestamp(t) for t in valid_pairs]

    return formatted_pairs

def format_timestamp(seconds):
    timestamp = str(datetime.timedelta(seconds=seconds))
    if len(timestamp.split(":")[0]) == 1:
        timestamp = "0" + timestamp
    return timestamp

def process_videos_in_folder(folder_path, output_file):
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
            beep_pairs = detect_beep_pairs(y, sr, sensitivity=1.5)

            # Write results to the output file
            if beep_pairs:
                timestamps = ", ".join(beep_pairs)
                out_file.write(f"{video_file} - {timestamps}\n")

            # Cleanup the extracted audio file
            os.remove(audio_output_path)

def main():
    parser = argparse.ArgumentParser(description="Detect beep pairs in all MP4 video files in a folder.")
    parser.add_argument("folder_path", help="Path to the folder containing MP4 video files")
    parser.add_argument("output_file", help="Path to the output file where results will be saved")
    args = parser.parse_args()

    process_videos_in_folder(args.folder_path, args.output_file)

if __name__ == "__main__":
    main()
