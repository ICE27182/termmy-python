
from sys import platform
from os import system

if platform == "win32":
    def clear_screen():
        system("cls")
else:
    def clear_screen():
        system("clear")
