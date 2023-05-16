from math import radians

from ctre import WPI_TalonFX, WPI_TalonSRX
from magicbot import feedback, tunable
from wpimath.controller import PIDController
from wpimath.controller import (
    # TODO(davo): Change to radians after fixing RobotPy
    SimpleMotorFeedforwardMeters as SimpleMotorFeedforward,
)

from ids import TalonIds

FLYWHEEL_SPEED_ERROR_TOLERANCE: float = radians(1)

BACK_MOTOR_SHOOTING_SPEED: float = 1
BACK_MOTOR_INTAKE_SPEED: float = -0.15

FLYWHEEL_INTAKE_SPEED: float = -80


class Shooter:
    # initialise motor speed
    top_flywheel_speed = tunable(0.0)
    bottom_flywheel_speed = tunable(0.0)
    back_motor_speed = tunable(0.0)

    def __init__(self) -> None:
        # create instances of hardware handles
        self.top_flywheel = WPI_TalonFX(TalonIds.shooter_bottom)
        self.bottom_flywheel = WPI_TalonFX(TalonIds.shooter_bottom)
        self.back_motor = WPI_TalonSRX(TalonIds.shooter_back)

        self.top_flywheel_feedforward = SimpleMotorFeedforward(
            kS=0.015633, kV=0.12331, kA=0.0046012
        )
        self.bottom_flywheel_feedforward = SimpleMotorFeedforward(
            kS=0.015633, kV=0.12331, kA=0.0046012
        )

        self.top_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)
        self.bottom_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)

    def set_flywheel_speed(
        self, top_flywheel_speed: float, bottom_flywheel_speed: float
    ) -> None:
        # update internal motor speed setpoint
        self.top_flywheel_speed = top_flywheel_speed
        self.bottom_flywheel_speed = bottom_flywheel_speed

    def shoot(self) -> None:
        # rotate back motors so the cube is picked up by the flywheels
        self.back_motor_speed = BACK_MOTOR_SHOOTING_SPEED

    @feedback
    def top_flywheel_error(self) -> float:
        return self.top_flywheel_speed - self.top_flywheel.getSelectedSensorVelocity()

    @feedback
    def bottom_flywheel_error(self) -> float:
        return (
            self.bottom_flywheel_speed
            - self.bottom_flywheel.getSelectedSensorVelocity()
        )

    def top_flywheel_at_speed(self) -> bool:
        # return abs(self.top_flywheel_error()) < FLYWHEEL_SPEED_ERROR_TOLERANCE
        return True

    def bottom_flywheel_at_speed(self) -> bool:
        # return abs(self.bottom_flywheel_error()) < FLYWHEEL_SPEED_ERROR_TOLERANCE
        return True

    def is_ready(self) -> bool:
        return (
            self.top_flywheel_at_speed()
            and self.bottom_flywheel_at_speed()
            and self.is_loaded()
        )

    def load(self) -> None:
        self.top_flywheel_speed = FLYWHEEL_INTAKE_SPEED
        self.bottom_flywheel_speed = FLYWHEEL_INTAKE_SPEED
        self.back_motor_speed = BACK_MOTOR_INTAKE_SPEED

    @feedback
    def is_loaded(self) -> bool:
        """Get whether the shooter is loaded."""
        return bool(self.back_motor.isRevLimitSwitchClosed())

    def stop(self) -> None:
        self.top_flywheel_speed = 0.0
        self.bottom_flywheel_speed = 0.0
        self.back_motor_speed = 0.0

    def is_loading(self) -> bool:
        return self.top_flywheel_speed < 0 and self.bottom_flywheel_speed < 0

    def execute(self) -> None:
        if self.is_loaded() and self.is_loading():
            self.stop()

        # top_voltage = self.top_flywheel_speed_controller.calculate(
        #     self.top_flywheel_encoder.getVelocity(), self.top_flywheel_speed
        # )
        # bottom_voltage = self.bottom_flywheel_speed_controller.calculate(
        #     self.bottom_flywheel_encoder.getVelocity(), self.bottom_flywheel_speed
        # )
        top_voltage = self.top_flywheel_feedforward.calculate(
            currentVelocity=self.top_flywheel.getSelectedSensorVelocity(),
            nextVelocity=self.top_flywheel_speed,
            dt=0.02,
        )
        bottom_voltage = self.bottom_flywheel_feedforward.calculate(
            currentVelocity=self.bottom_flywheel.getSelectedSensorVelocity(),
            nextVelocity=self.bottom_flywheel_speed,
            dt=0.02,
        )

        back_voltage = self.back_motor_speed * 12

        self.top_flywheel.setVoltage(top_voltage)
        self.bottom_flywheel.setVoltage(bottom_voltage)
        self.back_motor.setVoltage(back_voltage)
