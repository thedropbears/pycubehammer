#!/usr/bin/env python3

from math import radians
from typing import Optional

import magicbot
import wpilib
import wpilib.event
from wpimath.geometry import (
    Pose2d,
    Rotation2d,
    Rotation3d,
    Transform2d,
    Translation2d,
    Translation3d,
)

from components.chassis import Chassis
from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import ITurret
from components.vision import VisualLocaliser
from controllers.shooter import ShooterController
from utilities.game import TagId, get_fiducial_pose, get_grid_tag_ids, is_red
from utilities.scalers import rescale_js, scale_value


class Robot(magicbot.MagicRobot):
    # Controllers
    shooter_controller: ShooterController

    # Components
    chassis_component: Chassis
    intake_component: Intake
    shooter_component: Shooter
    tilt_component: Tilt
    turret_component: ITurret
    front_localiser: VisualLocaliser
    rear_localiser: VisualLocaliser

    SPIN_RATE = 4.0
    MAX_SPEED = magicbot.tunable(Chassis.max_wheel_speed * 0.95)

    def createObjects(self) -> None:
        self.data_log = wpilib.DataLogManager.getLog()

        self.event_loop = wpilib.event.EventLoop()
        self.gamepad = wpilib.XboxController(0)
        self.pov_up = self.gamepad.POVUp(self.event_loop)
        self.pov_left = self.gamepad.POVLeft(self.event_loop)
        self.pov_down = self.gamepad.POVDown(self.event_loop)
        self.pov_right = self.gamepad.POVRight(self.event_loop)

        self.field = wpilib.Field2d()
        wpilib.SmartDashboard.putData(self.field)

        self.front_localiser_name = "cam_front"
        # Relative to turret centre
        self.front_localiser_pos = Translation3d(0.05, 0.0, 0.83)
        self.front_localiser_rot = Rotation3d.fromDegrees(0.0, 0.0, 0.0)

        self.rear_localiser_name = "cam_rear"
        # Relative to turret centre
        self.rear_localiser_pos = Translation3d(-0.05, 0.0, 0.83)
        self.rear_localiser_rot = Rotation3d.fromDegrees(0.0, 0.0, 180.0)

    def robotInit(self) -> None:
        super().robotInit()
        # Bind events to component methods after components are created.
        self.pov_up.rising().ifHigh(self.shooter_controller.select_up)
        self.pov_down.rising().ifHigh(self.shooter_controller.select_down)
        self.pov_left.rising().ifHigh(self.shooter_controller.select_left)
        self.pov_right.rising().ifHigh(self.shooter_controller.select_right)

    def robotPeriodic(self) -> None:
        super().robotPeriodic()
        position = self.shooter_controller.get_target_position()
        self.field.getObject("target").setPose(
            Pose2d(Translation2d(position.x, position.y), Rotation2d())
        )
        abs_turret_rotation = Rotation2d(
            self.chassis_component.get_pose().rotation().radians()
            + self.turret_component.get_angle()
        )
        turret_pose = Pose2d(
            self.chassis_component.get_pose().translation(), abs_turret_rotation
        )
        self.field.getObject("turret").setPose(turret_pose)

    def disabledInit(self) -> None:
        pass

    def disabledPeriodic(self) -> None:
        tag_id: Optional[TagId] = None
        if self.gamepad.getXButtonPressed():
            tag_id = get_grid_tag_ids()[0]
        if self.gamepad.getYButtonPressed():
            tag_id = get_grid_tag_ids()[1]
        if self.gamepad.getBButtonPressed():
            tag_id = get_grid_tag_ids()[2]

        if tag_id is not None and self.gamepad.getLeftTriggerAxis() > 0.5:
            bumper_up_trans = Transform2d(0.42 + Chassis.LENGTH / 2, 0, 0)
            pose = get_fiducial_pose(tag_id).toPose2d() + bumper_up_trans
            self.chassis_component.set_pose(pose)

        self.turret_component.maybe_rezero_off_limits_switches()
        self.turret_component.disabled_periodic()

        self.tilt_component.disabled_periodic()

        self.chassis_component.update_odometry()
        self.front_localiser.execute()
        self.rear_localiser.execute()

    def autonomousInit(self) -> None:
        pass

    def teleopInit(self) -> None:
        pass

    def teleopPeriodic(self) -> None:
        # Scale speeds so fully depressing a trigger is half speed.
        speed_multiplier = scale_value(self.gamepad.getRightTriggerAxis(), 0, 1, 1, 0.5)
        max_speed = self.MAX_SPEED * speed_multiplier
        spin_rate = self.SPIN_RATE * speed_multiplier

        drive_x = -rescale_js(self.gamepad.getLeftY(), 0.1) * max_speed
        drive_y = -rescale_js(self.gamepad.getLeftX(), 0.1) * max_speed
        drive_z = -rescale_js(self.gamepad.getRightX(), 0.1, exponential=2) * spin_rate
        local_driving = self.gamepad.getStartButton()

        if is_red():
            drive_x = -drive_x
            drive_y = -drive_y

        if local_driving:
            self.chassis_component.drive_local(drive_x, drive_y, drive_z)
        else:
            self.chassis_component.drive_field(drive_x, drive_y, drive_z)

        if self.gamepad.getLeftBumperPressed():
            self.shooter_controller.intake()
        elif self.gamepad.getRightBumper():
            self.shooter_controller.shoot()
        elif (
            self.gamepad.getBackButtonPressed()
            and not self.shooter_component.is_shooting()
        ):
            self.shooter_controller.next_state("recovery")

        self.event_loop.poll()

    def testInit(self) -> None:
        self.tilt_component.set_angle(self.tilt_component.get_angle())

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
