#!/usr/bin/env python
""" ArmDroid.py - Basic Class to communicate with an ArmDroid robot.
    Specifically developed against an ArmDroid 1000 by D&M Computing

    __author__      = "Joe Romano"
    __license__     = "BSD"
    __version__     = "0.1"
"""
""" Wiring Description"""
""" Usage Description"""
""" Testing: sudo python ArmDroid.py """


import wiringpi


class ArmDroid:
    """ A simple class to speak to the armdroid over the raspberry pi """

    def __init__(self):
        """ Initialize the wiringpi interface and set the appropriate
            pi pins to be outputs
        """
        # set pins 0-7 as output
        # NOTE: these are WiringPi pin numbers
        #    https://pinout.xyz/pinout/wiringpi
        wiringpi.wiringPiSetup()
        for i in range(8):
            wiringpi.pinMode(i, wiringpi.OUTPUT)

        # define the phase commutation pattern
        self._commutate_pattern_pos = [0b10000000,  # A
                                       0b00001000,  # B
                                       0b01000000,  # C
                                       0b00000100]  # D
        # create the reversed pattern for negative commutation
        self._commutate_pattern_neg = list(
            reversed(self._commutate_pattern_pos))

        # the enable bit flag to signal a read
        self._enable = 0b00000001

        # the various joint mapping codes
        self._joint = [0b00010000,  # gripper
                       0b00000010,  # wrist roll
                       0b00010010,  # wrist pitch
                       0b00100000,  # upper arm
                       0b00110000,  # shoulder
                       0b00100010]  # base

        self._PULSE_TRANSMIT = 2000
        self._DELAY_RESET = 1000

    def drive_motor(self, motor_idx, steps, dir):
        if (motor_idx < 0 or motor_idx > 5):
            return
        if steps <= 0:
            return
        if (dir < 0 or dir > 1):
            return

        motor = self._joint[motor_idx]

        for i in range(steps):
            for j in range(len(self._commutate_pattern_pos)):
                wiringpi.delayMicroseconds(self._DELAY_RESET)
                output = motor
                if(dir):
                    output = output | self._commutate_pattern_pos[j]
                else:
                    output = output | self._commutate_pattern_neg[j]
                wiringpi.digitalWriteByte(output | self._enable)
                wiringpi.delayMicroseconds(self._PULSE_TRANSMIT)
                wiringpi.digitalWriteByte(output)


def main():
    a = ArmDroid()
    steps = 100
    for motor_idx in range(6):
        a.drive_motor(motor_idx, steps, 0)
        a.drive_motor(motor_idx, steps, 1)

if __name__ == "__main__":
    main()
