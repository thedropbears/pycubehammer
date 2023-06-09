from ctre import WPI_TalonSRX
from magicbot import feedback, tunable
from rev import CANSparkMax
from wpimath.controller import PIDController
from wpimath.controller import (
    # TODO(davo): Change to radians after fixing RobotPy
    SimpleMotorFeedforwardMeters as SimpleMotorFeedforward,
)

from ids import SparkMaxIds, TalonIds

FLYWHEEL_SPEED_ERROR_TOLERANCE: float = 10

BACK_MOTOR_SHOOTING_SPEED: float = 1
BACK_MOTOR_INTAKE_SPEED: float = -0.5


class Shooter:
    # initialise motor speed
    top_flywheel_speed = tunable(0.0)
    bottom_flywheel_speed = tunable(0.0)
    back_motor_speed = tunable(0.0)

    flywheel_intake_speed = tunable(-25)

    def __init__(self) -> None:
        # create instances of hardware handles
        self.top_flywheel = CANSparkMax(
            SparkMaxIds.top_flywheel, CANSparkMax.MotorType.kBrushless
        )
        self.bottom_flywheel = CANSparkMax(
            SparkMaxIds.bottom_flywheel, CANSparkMax.MotorType.kBrushless
        )
        self.top_flywheel.setInverted(False)
        self.bottom_flywheel.setInverted(True)
        self.top_flywheel.setSmartCurrentLimit(40)
        self.bottom_flywheel.setSmartCurrentLimit(40)

        self.back_motor = WPI_TalonSRX(TalonIds.shooter_back)
        self.back_motor.setInverted(True)
        self.back_motor.configContinuousCurrentLimit(20)

        self.top_flywheel_encoder = self.top_flywheel.getEncoder()
        self.top_flywheel_encoder.setVelocityConversionFactor(1 / 60)
        self.bottom_flywheel_encoder = self.bottom_flywheel.getEncoder()
        self.bottom_flywheel_encoder.setVelocityConversionFactor(1 / 60)

        self.flywheel_feedforward = SimpleMotorFeedforward(
            kS=0.015633, kV=0.12331, kA=0.0046012
        )

        self.top_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)
        self.bottom_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)

        self._has_cube = False
        self._reset_last_flywheel_speeds()

    def _reset_last_flywheel_speeds(self) -> None:
        self._last_top_flywheel_speed = 0.0
        self._last_bottom_flywheel_speed = 0.0

    def on_disable(self) -> None:
        self._reset_last_flywheel_speeds()

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
        return self.top_flywheel_speed - self.top_flywheel_encoder.getVelocity()

    @feedback
    def bottom_flywheel_error(self) -> float:
        return self.bottom_flywheel_speed - self.bottom_flywheel_encoder.getVelocity()

    def top_flywheel_at_speed(self) -> bool:
        return abs(self.top_flywheel_error()) < FLYWHEEL_SPEED_ERROR_TOLERANCE

    def bottom_flywheel_at_speed(self) -> bool:
        return abs(self.bottom_flywheel_error()) < FLYWHEEL_SPEED_ERROR_TOLERANCE

    def is_ready(self) -> bool:
        return (
            self.top_flywheel_at_speed()
            and self.bottom_flywheel_at_speed()
            and self.is_loaded()
            and self.bottom_flywheel_speed > 0  # don't fire beyond max range
            and self.top_flywheel_speed > 0
        )

    def load(self) -> None:
        self.top_flywheel_speed = self.flywheel_intake_speed
        self.bottom_flywheel_speed = self.flywheel_intake_speed
        self.back_motor_speed = BACK_MOTOR_INTAKE_SPEED

    @feedback
    def is_loaded(self) -> bool:
        """Get whether the shooter is loaded."""
        return bool(self.back_motor.isRevLimitSwitchClosed() or self._has_cube)

    def set_has_cube(self) -> None:
        self._has_cube = True

    def clear_has_cube(self) -> None:
        self._has_cube = False

    def stop(self) -> None:
        self.top_flywheel_speed = 0.0
        self.bottom_flywheel_speed = 0.0
        self.back_motor_speed = 0.0

    def is_loading(self) -> bool:
        return self.top_flywheel_speed < 0 and self.bottom_flywheel_speed < 0

    def is_shooting(self) -> bool:
        return self.back_motor_speed > 0

    def execute(self) -> None:
        if self.is_loaded() and self.is_loading():
            self.stop()

        # top_voltage = self.top_flywheel_speed_controller.calculate(
        #     self.top_flywheel_encoder.getVelocity(), self.top_flywheel_speed
        # )
        # bottom_voltage = self.bottom_flywheel_speed_controller.calculate(
        #     self.bottom_flywheel_encoder.getVelocity(), self.bottom_flywheel_speed
        # )
        top_voltage = self.flywheel_feedforward.calculate(
            currentVelocity=self._last_top_flywheel_speed,
            nextVelocity=self.top_flywheel_speed,
            dt=0.02,
        )
        bottom_voltage = self.flywheel_feedforward.calculate(
            currentVelocity=self._last_bottom_flywheel_speed,
            nextVelocity=self.bottom_flywheel_speed,
            dt=0.02,
        )

        back_voltage = self.back_motor_speed * 12

        self.top_flywheel.setVoltage(top_voltage)
        self.bottom_flywheel.setVoltage(bottom_voltage)
        self.back_motor.setVoltage(back_voltage)

        self._last_top_flywheel_speed = self.top_flywheel_speed
        self._last_bottom_flywheel_speed = self.bottom_flywheel_speed
