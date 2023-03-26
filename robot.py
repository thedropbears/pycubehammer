#!/usr/bin/env python3

import magicbot
import wpilib


class Robot(magicbot.MagicRobot):
    def createObjects(self) -> None:
        pass


if __name__ == "__main__":
    wpilib.run(Robot)
