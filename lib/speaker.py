import speech_recognition as SR
from threading import Thread
from pynput import keyboard
from time import sleep
from collections import namedtuple
from toolbox import console, json
import enum


class Event:

    press = False
    micThread = None
    
    @classmethod
    def on_press(cls, key):
        cls.press = True
        if (key == keyboard.Key.ctrl_r) and cls.micThread is None:
            countThread = Thread(target=cls.recvmic, daemon=True)
            countThread.start()
            
    @classmethod
    def on_release(cls, key):
        cls.press = False

    @classmethod
    def recvmic(cls) -> bool:
        sleep(1)
        if not cls.press: return

        console.info('Start receiving voice from your microphone.')

        obj = namedtuple('speech_recognition_object', ['recog', 'micro'])(
            recog = SR.Recognizer(),
            micro = SR.Microphone()
        )

        with obj.micro as source:
            obj.recog.adjust_for_ambient_noise(source)
            audio = obj.recog.listen(source)

    @classmethod
    def transcript(cls) -> json:
        ...