from Tello3 import send, sock
from time import sleep
from typing import overload
# import tellopy as Tellopy

class drone:

    @staticmethod
    def takeoff(dist):
        send(f'takeoff {dist}')


    @staticmethod
    def land(dist):
        send(f'land {dist}')



drone.takeoff(30)
sleep(3)
drone.land(30)

sock.close()

"""
drone:Tellopy.Tello = Tellopy.Tello()

drone.connect()
drone.wait_for_connection()

drone.takeoff()
sleep(3)
drone.forward(30)
drone.backward(30)
drone.land()
"""