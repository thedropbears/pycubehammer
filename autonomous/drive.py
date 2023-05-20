from magicbot import AutonomousStateMachine, timed_state, tunable

from components.chassis import Chassis
from utilities.game import is_red


class Drive(AutonomousStateMachine):
    MODE_NAME = "Drive Forward"

    chassis_component: Chassis

    vx = tunable(2.0)

    @timed_state(first=True, duration=1.0)
    def driving(self) -> None:
        vx = -self.vx if is_red() else self.vx
        self.chassis_component.drive_field(vx, 0, 0)
