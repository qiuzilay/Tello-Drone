from toolbox import slider, json, Enum, console
from pynput import keyboard
from threading import Thread
from time import perf_counter
from collections import namedtuple
import speech_recognition as sr
import asyncio

class const(Enum):
    microphone = sr.Microphone()
    recognizer = sr.Recognizer()

class Listener:

    transcript = slider(size=3)
    var = json({
        'trigger': False,
        'process': False,
        'threshold': 1.5
    })

    @classmethod
    def execute(cls):
        asyncio.run(cls.monitor())

    @classmethod
    def on_press(cls, key):
        if (key == keyboard.Key.ctrl_r):
            cls.var.trigger = True

    @classmethod
    def on_release(cls, key):
        if (key == keyboard.Key.ctrl_r):
            cls.var.trigger = False

    @classmethod
    async def monitor(cls):

        async def inspect():
            while True:
                await asyncio.sleep(cls.var.threshold)
                if cls.var.trigger and not cls.var.process:
                    console.info("Start processing your voice.")
                    cls.var.process = True
                    cls.handler()
                    cls.var.process = False

        with keyboard.Listener(on_press=cls.on_press, on_release=cls.on_release) as listener:
            await asyncio.gather(
                asyncio.to_thread(listener.join),
                inspect()
            )

    @classmethod
    def listener(cls):
        with const.microphone as source:
            while True:
                console.info('Trigger!')
                const.recognizer.adjust_for_ambient_noise(source)
                audio = const.recognizer.listen(source)
                try:
                    text = const.recognizer.recognize_google(audio, language='zh-tw', show_all=True)
                except Exception as E:
                    console.info(E)
                else:
                    console.info('text:', text)
                    cls.transcript.append(text['alternative'][0]['transcript']) if text else ...
        
    @classmethod
    def handler(cls):
        console.info(cls.transcript)
        cls.transcript = slider(size=3)


listenThread = Thread(target=Listener.listener, daemon=True)
listenThread.start()

Listener.execute() if __name__.__eq__('__main__') else ...