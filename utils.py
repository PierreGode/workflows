import speech_recognition as sr
import pygame
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='utils.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def record_audio(file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Please say something...")
            audio_data = recognizer.listen(source)
            print("Recording complete.")
            with open(file_path, "wb") as audio_file:
                audio_file.write(audio_data.get_wav_data())
    except sr.RequestError as e:
        logging.error(f"Could not request results from the speech recognition service; {e}")
        print("Could not request results from the speech recognition service.")
    except sr.UnknownValueError:
        logging.error("Speech recognition could not understand the audio")
        print("Speech recognition could not understand the audio")
    except Exception as e:
        logging.error(f"An error occurred during audio recording: {e}")
        print(f"An error occurred during audio recording: {e}")

def play_audio(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist")
        print(f"File {file_path} does not exist")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Wait until the audio is finished playing
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except pygame.error as e:
        logging.error(f"An error occurred during audio playback: {e}")
        print(f"An error occurred during audio playback: {e}")
    finally:
        pygame.mixer.quit()
