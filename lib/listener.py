from os import chdir
from os.path import dirname, realpath
chdir(dirname(realpath(__file__))) if __name__.__eq__('__main__') else ...

from toolbox import slider, json, Enum, console
from dataclasses import dataclass, field
from pynput import keyboard
from threading import Thread
from movements import Movements
from time import sleep
import speech_recognition as sr

class const(Enum):
    microphone = sr.Microphone()
    recognizer = sr.Recognizer()

class Listener:

    @dataclass
    class variable:
        threshold: int | float = 1
        monitor: Thread | None = None
        transcript: slider = slider(size=2)
        keyREC: set = field(default_factory=set)

    var = variable()

    @classmethod
    def execute(cls, tello):

        Movements.tello = tello

        listenThread = Thread(name='Voice Listener', target=cls.listener, daemon=True)
        listenThread.start()

        with keyboard.Listener(on_press=cls.on_press, on_release=cls.on_release) as keyListener:
            keyListener.name = 'Keyboard Listener'
            keyListener.join()

    @classmethod
    def on_press(cls, key):
        cls.var.keyREC.add(key)
        if key == keyboard.Key.ctrl_r and cls.var.monitor is None:
            cls.var.monitor = Thread(name='Transcript Handler', target=cls.monitor, daemon=True)
            cls.var.monitor.start()

    @classmethod
    def on_release(cls, key):
        cls.var.keyREC.add(None)

    @classmethod
    def monitor(cls):
        sleep(cls.var.threshold)
        if (None not in cls.var.keyREC) and len(cls.var.keyREC):
            if cls.var.transcript:
                console.info('Start processing your voice-text.')
                cls.handler()
            else:
                console.info('There is nothing to process.')
        
        cls.var.keyREC.clear()
        cls.var.monitor = None

    @classmethod
    def listener(cls):
        with const.microphone as source:
            const.recognizer.adjust_for_ambient_noise(source)
            while True:
                console.info('Voice was detected, recording it currently.')
                audio = const.recognizer.listen(source)
                try: text = const.recognizer.recognize_google(audio, language='zh-tw', show_all=True)
                except Exception as E: console.info(E)
                else:
                    if text:
                        transcript = text['alternative'][0]['transcript']
                        console.debug(transcript)
                        cls.var.transcript.append(transcript)
                    else:
                        console.info('Failed to transcript your voice-text.')

    @classmethod
    def handler(cls):
        Movements.read(cls.var.transcript.join())
        cls.var.transcript = slider(size=2)