from magicbot import AutonomousStateMachine, timed_state

from components.chassis import Chassis
from utilities.game import is_red


class Drive(AutonomousStateMachine):
    MODE_NAME = "Drive Forward"

    chassis_component: Chassis

    @timed_state(first=True, duration=1.0)
    def driving(self) -> None:
        vx = -1 if is_red() else 1
        self.chassis_component.drive_field(vx, 0, 0)
