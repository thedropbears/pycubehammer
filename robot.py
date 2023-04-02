#!/usr/bin/env python3

from math import radians

import magicbot
import wpilib

from components.chassis import Chassis
from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import Turret
from controllers.shooter import ShooterController
from utilities.scalers import rescale_js


class Robot(magicbot.MagicRobot):
    # Controllers
    shooter_controller: ShooterController

    # Components
    chassis_component: Chassis
    intake_component: Intake
    shooter_component: Shooter
    tilt_component: Tilt
    turret_component: Turret

    SPIN_RATE = 4
    MAX_SPEED = magicbot.tunable(Chassis.max_wheel_speed * 0.95)

    def createObjects(self) -> None:
        self.gamepad = wpilib.XboxController(0)

        self.field = wpilib.Field2d()
        wpilib.SmartDashboard.putData(self.field)

    def disabledInit(self) -> None:
        pass

    def disabledPeriodic(self) -> None:
        pass

    def autonomousInit(self) -> None:
        pass

    def autonomousPeriodic(self) -> None:
        pass

    def teleopInit(self) -> None:
        pass

    def teleopPeriodic(self) -> None:
        drive_x = -rescale_js(self.gamepad.getLeftY(), 0.1) * self.MAX_SPEED
        drive_y = -rescale_js(self.gamepad.getLeftX(), 0.1) * self.MAX_SPEED
        drive_z = (
            -rescale_js(self.gamepad.getRightX(), 0.1, exponential=2) * self.SPIN_RATE
        )
        local_driving = self.gamepad.getBButton()

        if local_driving:
            self.chassis_component.drive_local(drive_x, drive_y, drive_z)
        else:
            self.chassis_component.drive_field(drive_x, drive_y, drive_z)

    def testInit(self) -> None:
        pass

    def testPeriodic(self) -> None:
        # Turret
        if self.gamepad.getYButton():
            dpad_angle = self.gamepad.getPOV()

            if dpad_angle != -1:
                turret_angle = -dpad_angle
                if turret_angle < -180:
                    turret_angle = turret_angle + 360
                self.turret_component.set_angle(radians(turret_angle))

        # shooter controller
        if self.gamepad.getXButton():
            if self.gamepad.getRightBumper():
                self.shooter_controller.shoot()

            if self.gamepad.getLeftBumperPressed():
                self.shooter_controller.intake()

        self.turret_component.execute()
        self.shooter_controller.execute()
        self.shooter_controller.try_shoot = False


if __name__ == "__main__":
    wpilib.run(Robot)
