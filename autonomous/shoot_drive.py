from magicbot import AutonomousStateMachine, state, timed_state

from components.chassis import Chassis
from components.shooter import Shooter
from controllers.shooter import ShooterController
from utilities.game import is_red


class ShootDrive(AutonomousStateMachine):
    MODE_NAME = "Eats Shoots and Leaves"

    chassis_component: Chassis
    shooter_component: Shooter
    shooter_controller: ShooterController

    @state(first=True)
    def shooting(self) -> None:
        self.shooter_controller.shoot()

        if not (
            self.shooter_component.is_loaded() or self.shooter_component.is_shooting()
        ):
            self.next_state(self.driving)

    @timed_state(duration=1.0)
    def driving(self) -> None:
        vx = -1 if is_red() else 1
        self.chassis_component.drive_field(vx, 0, 0)
