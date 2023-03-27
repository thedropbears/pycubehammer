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
        pass

    @state(must_finish=True)
    def preparing_intake(self) -> None:
        # send pitch and turret to angle

        # if at pitch and turret angle
        # next state intaking
        pass

    @state(must_finish=True)
    def intaking(self) -> None:
        # shooter intake
        # intake deploy

        # if shooter is loaded
        # retract intake
        # next state tracking
        pass

    @default_state
    def tracking(self) -> None:
        # if turret not indexed
        # return

        # update flywheel speed
        # update turret angle
        # update tilt angle

        pass

    @state(must_finish=True)
    def shooting(self) -> None:
        # update flywheel speed
        # update turret angle
        # update tilt angle

        # if tilt ready and turret ready and flywheels at speed
        # shoot
        # next state tracking
        pass

    def shoot(self) -> None:
        # set next state to shooting
        pass

    def intake(self) -> None:
        # if shooter doesn't have a cube
        # set next state to preparing intake
        pass

    def prefer_high(self) -> None:
        # set preference
        pass

    def prefer_mid(self) -> None:
        # set preference
        pass

    def prefer_low(self) -> None:
        # set preference
        pass
