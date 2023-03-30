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
        # set default preference for goal height
        self.GoalHeight_Preference = GoalHeight.HIGH

    @state(first=True, must_finish=True)
    def preparing_intake(self) -> None:
        # send pitch and turret to angle
        self.turret_component.set_angle(0.0)
        # if at pitch and turret angle
        if self.turret_component.at_angle():
            self.next_state("intaking")
        # next state intaking
        #pass

    @state(must_finish=True)
    def intaking(self) -> None:
        # shooter intake 
        # intake deploy
        self.intake_component.deploy()

        if self.shooter_component.is_loaded():
            self.intake_component.retract()
            self.next_state("tracking")
        #pass

    @default_state
    def tracking(self) -> None:
        # if turret not indexed
        # return
        if self.turret_component.find_index() is None:
            return

        # update flywheel speed
        self.shooter_component.set_flywheel_speed(1.0)
        # update turret angle
        self.turret_component.set_angle(0.0)
        # update tilt angle
        self.tilt_component.set_angle(0.0)
        #pass

    @state(must_finish=True)
    def shooting(self) -> None:
        # update flywheel speed
        self.shooter_component.set_flywheel_speed(1.0)
        # update turret angle
        self.turret_component.set_angle()
        # update tilt angle
        self.tilt_component.set_angle()

        # if tilt ready and turret ready and flywheels at speed
        # shoot
        # next state tracking
        if self.tilt_component.at_angle() and self.turret_component.at_angle(): #and self.shooter_component.at_flywheel_speed():
            self.shooter_component.shoot()
            self.next_state("tracking")
        #pass

    def shoot(self) -> None:
        # set next state to shooting
        self.next_state("shooting")
        #pass

    def intake(self) -> None:
        # if shooter doesn't have a cube
        # set next state to preparing intake
        if self.shooter_component.is_loaded() is False:
            self.next_state("preparing_intake")
        #pass

    def prefer_high(self) -> None:
        # set preference
        return self.GoalHeight_Preference
        #pass

    def prefer_mid(self) -> None:
        if self.GoalHeight_Preference is not GoalHeight.MID:
            self.GoalHeight_Preference = GoalHeight.MID
            return
        #pass

    def prefer_low(self) -> None:
        if self.GoalHeight_Preference is not GoalHeight.LOW:
            self.GoalHeight_Preference = GoalHeight.LOW
            return
