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

import time
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
        self._commutate_pattern = [0b10000000,  # A
                                   0b00001000,  # B
                                   0b01000000,  # C
                                   0b00000100]  # D

        # the enable bit flag to signal a read
        self._enable = 0b00000001

        # the various joint mapping codes
        self._joint = [0b00010000,  # gripper
                       0b00000010,  # wrist roll
                       0b00010010,  # wrist pitch
                       0b00100000,  # upper arm
                       0b00110000,  # shoulder
                       0b00100010]  # base

        self._commutate_index = [0] * len(self._joint)

        self._PULSE_TRANSMIT = 3000

        # flag to indicate whether to allow motor commutation
        self._motors_off = False

        # list to track the position count steps
        self._position_cnt = [0.0] * len(self._joint)

        # last time we drove this joint
        self._last_pulse = time.time()

    def _update_commutate_pattern(self, motor_idx, dir):
        """
         Update the commutation pattern pointer up or down and return
         the pattern
         """
        if(dir):
            self._commutate_index[motor_idx] += 1
            if self._commutate_index[motor_idx] > 3:
                self._commutate_index[motor_idx] = 0
        else:
            self._commutate_index[motor_idx] -= 1
            if self._commutate_index[motor_idx] < 0:
                self._commutate_index[motor_idx] = 3
        return self._commutate_pattern[self._commutate_index[motor_idx]]

    def _pulse_motor(self, motor_idx, dir):
        """
        Pulse a motor a single step
        """
        if self._motors_off:
            print "ERROR: Cannot drive motor while motors are off!"
            return

        output = self._joint[motor_idx]
        output = output | self._update_commutate_pattern(motor_idx, dir)
        if(dir):
            self._position_cnt[motor_idx] += 1
        else:
            self._position_cnt[motor_idx] -= 1
        wiringpi.digitalWriteByte(output | self._enable)
        wiringpi.digitalWriteByte(output)

    def motors_off(self):
        # for each joint output an empty commutate pattern
        for output in self._joint:
            wiringpi.digitalWriteByte(output | self._enable)
            wiringpi.digitalWriteByte(output)
        self._motors_off = True

    def motors_on(self):
        # for each joint output it's last commutate pattern
        for idx, output in enumerate(self._joint):
            output = output | self._commutate_index[idx]
            wiringpi.digitalWriteByte(output | self._enable)
            wiringpi.digitalWriteByte(output)
        self._motors_off = False

    def drive_motor(self, motor_idx, steps, dir):
        """
        Function to drive a single motor axis a specified number of steps

        param: motor_idx - the index number of the motor to drive [0-5]
        type: integer

        param: steps - the number of steps to move
        type: positive integer

        param: dir - the direction (clockwise = 1, ccw = 0)
        type: bool
        """
        if (motor_idx < 0 or motor_idx > 5):
            print("Bad motor index value (%d) detected." % motor_idx)
            return
        if steps <= 0:
            print("Cannot move negative steps.")
            return
        if (dir < 0 or dir > 1):
            print("dir must be either 0 or 1")
            return

        for i in range(steps):
            delay_us = (self._PULSE_TRANSMIT -
                        (time.time() - self._last_pulse))
            if delay_us > 0:
                wiringpi.delayMicroseconds(int(round(delay_us)))

            self._pulse_motor(motor_idx, dir)
            self._last_pulse = time.time()

    def drive_multi(self, motor_idx, steps):
        """
        Function to drive multiple axes at once
        param: motor_idx -  a list of motor indices to drive
        type: list of integers

        param: steps - the number of steps to move each corresponding index
        type: list of integers (positive or negative). NOTE: must be same size
              as motor_idx list
        """
        if len(motor_idx) != len(steps):
            print("motor_idx and steps lists must be same size!")
            return
        for idx in motor_idx:
            if idx < 0 or idx > 5:
                print "motor_idx must be 0 to 5"
                return

        # parse off the direction
        dir = []
        for idx in range(len(steps)):
            if steps[idx] > 0:
                dir.append(1)
            else:
                dir.append(0)
                steps[idx] = steps[idx] * -1

        # loop the maximum number of steps of all motors
        for i in range(max(steps)):
            delay_us = (self._PULSE_TRANSMIT -
                        (time.time() - self._last_pulse))
            if delay_us > 0:
                wiringpi.delayMicroseconds(int(round(delay_us)))

            for idx in range(len(steps)):
                if steps[idx] > 0:
                    self._pulse_motor(motor_idx[idx], dir[idx])
                    steps[idx] -= 1
                    self._last_pulse = time.time()


def main():
    # create our interface
    a = ArmDroid()

    # test some single-joint moves
    steps = 400
    for motor_idx in range(6):
        a.drive_motor(motor_idx, steps, 0)
        a.drive_motor(motor_idx, steps, 1)

    # test motors off/on and multi-joint moves
    a.motors_off()
    a.drive_multi([5, 4, 3, 2, 1, 0],[400]*6)
    a.drive_multi([5, 4, 3, 2, 1, 0],[-400]*6)
    a.motors_on()

    # test the error case
    a.motors_off()
    a.drive_multi([5, 4, 3, 2, 1, 0], [400]*6)


if __name__ == "__main__":
    main()
