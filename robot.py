#!/usr/bin/env python3

from math import radians

import magicbot
import wpilib
from wpimath.geometry import (
    Pose2d,
    Rotation2d,
    Rotation3d,
    Translation2d,
    Translation3d,
)

from components.chassis import Chassis
from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import Turret
from components.vision import VisualLocaliser
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
    front_localiser: VisualLocaliser
    rear_localiser: VisualLocaliser

    SPIN_RATE = 4
    MAX_SPEED = magicbot.tunable(Chassis.max_wheel_speed * 0.95)

    def createObjects(self) -> None:
        self.data_log = wpilib.DataLogManager.getLog()

        self.gamepad = wpilib.XboxController(0)

        self.field = wpilib.Field2d()
        wpilib.SmartDashboard.putData(self.field)

        self.front_localiser_name = "cam_front"
        # Relative to turret centre
        self.front_localiser_pos = Translation3d(0.05, 0.0, 0.25)
        self.front_localiser_rot = Rotation3d.fromDegrees(0.0, 0.0, 0.0)

        self.rear_localiser_name = "cam_rear"
        # Relative to turret centre
        self.rear_localiser_pos = Translation3d(-0.05, 0.0, 0.25)
        self.rear_localiser_rot = Rotation3d.fromDegrees(0.0, 0.0, 180.0)

    def robotPeriodic(self) -> None:
        super().robotPeriodic()
        position = self.shooter_controller.get_target_position()
        self.field.getObject("target").setPose(
            Pose2d(Translation2d(position.x, position.y), Rotation2d())
        )
        abs_turret_rotation = Rotation2d(
            self.chassis_component.get_pose().rotation().radians()
            + self.turret_component.goal_angle
        )
        turret_pose = Pose2d(
            self.chassis_component.get_pose().translation(), abs_turret_rotation
        )
        self.field.getObject("turret").setPose(turret_pose)

    def disabledInit(self) -> None:
        pass

    def disabledPeriodic(self) -> None:
        self.turret_component.maybe_rezero_off_limits_switches()
        self.turret_component.disabled_periodic()

        self.chassis_component.update_odometry()
        self.front_localiser.execute()
        self.rear_localiser.execute()

    def autonomousInit(self) -> None:
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

        # Tilt component
        if self.gamepad.getBButton():
            dpad_angle = self.gamepad.getPOV()
            if dpad_angle != -1:
                if dpad_angle <= 90:
                    self.tilt_component.set_angle(radians(dpad_angle))
                elif dpad_angle >= 270:
                    self.tilt_component.set_angle(radians(dpad_angle - 360))

        # shooter controller
        if self.gamepad.getXButton():
            if self.gamepad.getRightBumper():
                self.shooter_controller.shoot()

            if self.gamepad.getLeftBumperPressed():
                self.shooter_controller.intake()

            self.shooter_controller.execute()

        # shooter component
        if self.gamepad.getAButton():
            dpad_angle = self.gamepad.getPOV()

            if self.gamepad.getRightBumperPressed():
                top_flywheel_speed = self.shooter_component.top_flywheel_speed + 100
                bottom_flywheel_speed = (
                    self.shooter_component.bottom_flywheel_speed + 100
                )

                top_flywheel_speed = min(top_flywheel_speed, 600)
                bottom_flywheel_speed = min(bottom_flywheel_speed, 600)

                self.shooter_component.set_flywheel_speed(
                    top_flywheel_speed, bottom_flywheel_speed
                )

            if self.gamepad.getLeftBumperPressed():
                top_flywheel_speed = self.shooter_component.top_flywheel_speed - 100
                bottom_flywheel_speed = (
                    self.shooter_component.bottom_flywheel_speed - 100
                )

                top_flywheel_speed = max(top_flywheel_speed, -600)
                bottom_flywheel_speed = max(bottom_flywheel_speed, -600)

                self.shooter_component.set_flywheel_speed(
                    top_flywheel_speed, bottom_flywheel_speed
                )

            if dpad_angle == 0:
                self.shooter_component.shoot()

            if dpad_angle == 180:
                self.shooter_component.load()

            if dpad_angle == 270:
                self.shooter_component.stop()

        self.intake_component.execute()
        self.turret_component.execute()
        self.tilt_component.execute()
        self.shooter_component.execute()
        self.shooter_controller.try_shoot = False

        # Vision and odometry
        self.chassis_component.update_odometry()
        self.front_localiser.execute()
        self.rear_localiser.execute()


if __name__ == "__main__":
    wpilib.run(Robot)
