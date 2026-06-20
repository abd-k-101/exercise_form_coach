import threading
import time
import queue

import pygame.mixer
import pyttsx3


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self._sounds: dict[str, pygame.mixer.Sound] = {}

        self.tts_queue: queue.Queue = queue.Queue()
        self._last_spoken_text: str = ""
        self._last_spoken_time: float = 0.0

        tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        tts_thread.start()

    def _tts_worker(self) -> None:
        engine = pyttsx3.init()
        while True:
            text = self.tts_queue.get()
            engine.say(text)
            engine.runAndWait()

    def speak(self, text: str, cooldown: float = 3.0) -> None:
        now = time.time()
        if text == self._last_spoken_text and (now - self._last_spoken_time) < cooldown:
            return
        self._last_spoken_text = text
        self._last_spoken_time = now
        self.tts_queue.put(text)

    def load(self, name: str, path: str) -> None:
        self._sounds[name] = pygame.mixer.Sound(path)

    def play(self, name: str) -> None:
        sound = self._sounds.get(name)
        if sound:
            threading.Thread(target=sound.play, daemon=True).start()
