from enum import Enum

from magicbot import StateMachine, default_state, state

from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import Turret


class GoalHeight(Enum):
    HIGH = 2
    MID = 1
    LOW = 0


# Setpoints for intaking state
INTAKE_AZIMUTH: float
INTAKE_TILT: float


class ShooterController(StateMachine):
    intake_component: Intake
    shooter_component: Shooter
    tilt_component: Tilt
    turret_component: Turret

    def __init__(self) -> None:
        self.goal_height_preference = GoalHeight.HIGH #default preference

    @state(first=True, must_finish=True)
    def preparing_intake(self) -> None:
        self.turret_component.set_angle(0.0)

        if self.turret_component.at_angle():
            self.next_state("intaking")

    @state(must_finish=True)
    def intaking(self) -> None:
        self.intake_component.deploy()

        if self.shooter_component.is_loaded():
            self.intake_component.retract()
            self.next_state("tracking")

    @default_state
    def tracking(self) -> None:
        if self.turret_component.find_index(): ###
            return
        self.shooter_component.set_flywheel_speed(1.0)
        self.turret_component.set_angle(0.0)
        self.tilt_component.set_angle(0.0)

    @state(must_finish=True)
    def shooting(self) -> None:
        self.shooter_component.set_flywheel_speed(1.0)
        self.turret_component.set_angle()
        self.tilt_component.set_angle()

        if self.tilt_component.at_angle() and self.turret_component.at_angle(): #and self.shooter_component.at_flywheel_speed():
            self.shooter_component.shoot()
            self.next_state("tracking")

    def shoot(self) -> None:
        self.next_state("shooting")

    def intake(self) -> None:
        if self.shooter_component.is_loaded() is False:
            self.next_state("preparing_intake")

    def prefer_high(self) -> None:
        return self.GoalHeight_Preference

    def prefer_mid(self) -> None:
        if self.GoalHeight_Preference is not GoalHeight.MID:
            self.GoalHeight_Preference = GoalHeight.MID
            return

    def prefer_low(self) -> None:
        if self.GoalHeight_Preference is not GoalHeight.LOW:
            self.GoalHeight_Preference = GoalHeight.LOW
            return
