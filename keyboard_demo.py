#!/usr/bkeyin/env python
""" keyboard_demo.py - A simple armdroid jog demo uskeying the keyboard
"""


def _Getch():
    """Gets a single character from standard input.  Does not echo to the
screen."""
    import sys
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


from ArmDroid import ArmDroid
from time import sleep
a = ArmDroid()
print("Keys:")
print("Exit: V")
print("Base: Q/W")
print("Shoulder: A/S")
print("Upper Arm: Z/X")
print("Wrist Pitch: O/P")
print("Wrist Roll: K/L")
print("Gripper: N/M")
keyin = _Getch()
while(keyin != 'v'):
    keyin = _Getch()
    if keyin == 'q':
        a.drive_motor(5, 1, 0)
    if keyin == 'w':
        a.drive_motor(5, 1, 1)
    if keyin == 'a':
        a.drive_motor(4, 1, 0)
    if keyin == 's':
        a.drive_motor(4, 1, 1)
    if keyin == 'z':
        a.drive_motor(3, 1, 0)
    if keyin == 'x':
        a.drive_motor(3, 1, 1)
    if keyin == 'o':
        a.drive_motor(2, 1, 0)
    if keyin == 'p':
        a.drive_motor(2, 1, 1)
    if keyin == 'k':
        a.drive_motor(1, 1, 0)
    if keyin == 'l':
        a.drive_motor(1, 1, 1)
    if keyin == 'n':
        a.drive_motor(0, 1, 0)
    if keyin == 'm':
        a.drive_motor(0, 1, 1)
