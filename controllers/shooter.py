from magicbot import StateMachine, default_state, state, timed_state, will_reset_to
from wpimath.geometry import Pose2d

from components.chassis import Chassis
from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import Turret
from utilities.ballistics import GoalHeight, calculate_ballistics


class ShooterController(StateMachine):
    chassis_component: Chassis
    intake_component: Intake
    shooter_component: Shooter
    tilt_component: Tilt
    turret_component: Turret

    try_shoot = will_reset_to(False)

    def __init__(self) -> None:
        self.goal_height_preference = GoalHeight.HIGH  # default preference

    @state(first=True, must_finish=True)
    def preparing_intake(self) -> None:
        self.turret_component.set_angle(0.0)
        self.tilt_component.goto_intaking()

        if self.turret_component.at_angle() and self.tilt_component.at_angle():
            self.next_state("intaking")

    @state(must_finish=True)
    def intaking(self) -> None:
        self.intake_component.deploy()
        self.shooter_component.load()

        if self.shooter_component.is_loaded():
            self.intake_component.retract()
            self.next_state("tracking")

    @default_state
    def tracking(self) -> None:
        self.update_component_setpoints()

        if (
            self.try_shoot
            and self.shooter_component.is_ready()
            and self.turret_component.at_angle()
            and self.tilt_component.at_angle()
        ):
            self.next_state("shooting")

    @timed_state(must_finish=True, duration=1.0)
    def shooting(self) -> None:
        self.update_component_setpoints()
        self.shooter_component.shoot()

    def update_component_setpoints(self) -> None:
        bs = calculate_ballistics(
            self.chassis_component.get_pose(), self.get_target_pose(), self.goal_height_preference
        )
        self.turret_component.set_angle(bs.turret_angle)
        self.tilt_component.set_angle(bs.tilt_angle)
        # We can be tracking the targets even if we don't have a cube
        # No need to run the flywheels if we can't shoot
        if self.shooter_component.is_loaded():
            self.shooter_component.set_flywheel_speed(
                bs.top_flywheel_speed, bs.bottom_flywheel_speed
            )
        else:
            self.shooter_component.stop()

    def get_target_pose(self) -> Pose2d:
        return Pose2d()

    def shoot(self) -> None:
        self.try_shoot = True

    def intake(self) -> None:
        if not self.shooter_component.is_loaded():
            self.engage()

    def prefer_high(self) -> None:
        self.goal_height_preference = GoalHeight.HIGH

    def prefer_mid(self) -> None:
        self.goal_height_preference = GoalHeight.MID

    def prefer_low(self) -> None:
        self.goal_height_preference = GoalHeight.LOW
