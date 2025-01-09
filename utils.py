import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygame
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks

# Ensure pydub can find ffmpeg - adjust the path if necessary
AudioSegment.converter = "ffmpeg"  # Ensure ffmpeg is installed and in PATH

# Initialize Pygame Mixer
pygame.mixer.init()


class AudioApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Audio Recorder and Player")
        self.master.geometry("500x400")
        self.recognizer = sr.Recognizer()
        self.audio_file = None
        self.transcription = tk.StringVar()
        self.is_playing = False
        self.is_paused = False

        self.create_widgets()

    def create_widgets(self):
        # Record Button
        self.record_button = ttk.Button(
            self.master, text="Record Audio", command=self.start_recording_thread
        )
        self.record_button.pack(pady=10)

        # Stop Recording Button
        self.stop_record_button = ttk.Button(
            self.master, text="Stop Recording", command=self.stop_recording, state="disabled"
        )
        self.stop_record_button.pack(pady=5)

        # Playback Controls Frame
        controls_frame = ttk.Frame(self.master)
        controls_frame.pack(pady=10)

        self.play_button = ttk.Button(
            controls_frame, text="Play", command=self.play_audio, state="disabled"
        )
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(
            controls_frame, text="Pause", command=self.pause_audio, state="disabled"
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(
            controls_frame, text="Stop", command=self.stop_audio, state="disabled"
        )
        self.stop_button.grid(row=0, column=2, padx=5)

        # Save Button
        self.save_button = ttk.Button(
            self.master, text="Save Recording", command=self.save_audio, state="disabled"
        )
        self.save_button.pack(pady=10)

        # Transcription Label and Text
        transcription_label = ttk.Label(self.master, text="Transcription:")
        transcription_label.pack(pady=5)

        self.transcription_text = tk.Text(self.master, height=5, wrap=tk.WORD)
        self.transcription_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Idle")
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Audio Level Indicator
        self.audio_level = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.audio_level.pack(pady=10)

    def start_recording_thread(self):
        threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        self.record_button.config(state="disabled")
        self.stop_record_button.config(state="normal")
        self.status_var.set("Recording...")
        self.audio_level["value"] = 0

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                self.audio_file = audio
                self.status_var.set("Recording stopped.")
                self.save_button.config(state="normal")
                self.play_button.config(state="normal")
                # Start transcription in a separate thread
                threading.Thread(target=self.transcribe_audio, args=(audio,)).start()
        except sr.WaitTimeoutError:
            messagebox.showwarning("Timeout", "No speech detected within the timeout period.")
            self.status_var.set("Idle")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Idle")
        finally:
            self.record_button.config(state="normal")
            self.stop_record_button.config(state="disabled")

    def stop_recording(self):
        # speech_recognition does not support stopping listen, so this is a placeholder
        # Implementing real-time stop would require a different approach with pyaudio
        messagebox.showinfo("Info", "Stop functionality is not implemented in this version.")
        self.stop_record_button.config(state="disabled")
        self.status_var.set("Idle")

    def save_audio(self):
        if not self.audio_file:
            messagebox.showwarning("No Audio", "No audio to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            try:
                # Save as WAV
                with open(file_path, "wb") as f:
                    f.write(self.audio_file.get_wav_data())

                # If MP3 is selected, convert using pydub
                if file_path.lower().endswith(".mp3"):
                    sound = AudioSegment.from_wav(io.BytesIO(self.audio_file.get_wav_data()))
                    sound.export(file_path, format="mp3")

                messagebox.showinfo("Success", f"Audio saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {e}")

    def play_audio(self):
        if not self.audio_file:
            messagebox.showwarning("No Audio", "No audio to play.")
            return

        if self.is_playing:
            messagebox.showinfo("Info", "Audio is already playing.")
            return

        try:
            # Save to a temporary file
            temp_path = "temp_audio.wav"
            with open(temp_path, "wb") as f:
                f.write(self.audio_file.get_wav_data())

            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.status_var.set("Playing audio...")
            self.play_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.stop_button.config(state="normal")

            # Monitor playback in a separate thread
            threading.Thread(target=self.monitor_playback, args=(temp_path,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {e}")
            self.status_var.set("Idle")

    def monitor_playback(self, temp_path):
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        self.is_playing = False
        self.status_var.set("Playback finished.")
        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        # Remove temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def pause_audio(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_var.set("Playback paused.")
            self.pause_button.config(text="Resume")
        elif self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_var.set("Playing audio...")
            self.pause_button.config(text="Pause")

    def stop_audio(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.status_var.set("Playback stopped.")
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")

    def transcribe_audio(self, audio):
        self.status_var.set("Transcribing audio...")
        try:
            text = self.recognizer.recognize_google(audio)
            self.transcription_text.delete(1.0, tk.END)
            self.transcription_text.insert(tk.END, text)
            self.transcription.set(text)
            self.status_var.set("Transcription complete.")
        except sr.UnknownValueError:
            self.transcription_text.insert(tk.END, "Could not understand the audio.")
            self.status_var.set("Transcription failed.")
        except sr.RequestError as e:
            self.transcription_text.insert(tk.END, f"Could not request results; {e}")
            self.status_var.set("Transcription error.")


def main():
    # Check for ffmpeg
    if not shutil.which("ffmpeg"):
        messagebox.showerror("FFmpeg Not Found", "FFmpeg is required for audio format conversions. Please install it and ensure it's in the system PATH.")
        sys.exit(1)

    root = tk.Tk()
    app = AudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    import shutil
    import io

    main()
