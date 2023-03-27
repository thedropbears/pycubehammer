#!/usr/bin/env python3

import magicbot
import wpilib

from components.chassis import Chassis
from utilities.scalers import rescale_js


class Robot(magicbot.MagicRobot):
    chassis: Chassis

    SPIN_RATE = 4
    MAX_SPEED = magicbot.tunable(Chassis.max_wheel_speed * 0.95)

    def createObjects(self) -> None:
        self.gamepad = wpilib.XboxController(0)

        self.field = wpilib.Field2d()
        wpilib.SmartDashboard.putData(self.field)

    def teleopPeriodic(self) -> None:
        drive_x = -rescale_js(self.gamepad.getLeftY(), 0.1) * self.MAX_SPEED
        drive_y = -rescale_js(self.gamepad.getLeftX(), 0.1) * self.MAX_SPEED
        drive_z = (
            -rescale_js(self.gamepad.getRightX(), 0.1, exponential=2) * self.SPIN_RATE
        )
        local_driving = self.gamepad.getBButton()

        if local_driving:
            self.chassis.drive_local(drive_x, drive_y, drive_z)
        else:
            self.chassis.drive_field(drive_x, drive_y, drive_z)


if __name__ == "__main__":
    wpilib.run(Robot)
