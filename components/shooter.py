from math import radians, tau

from magicbot import tunable
from rev import CANSparkMax
from wpilib import DigitalInput
from wpimath.controller import PIDController

from ids import DioChannels, SparkMaxIds

GEAR_RATIO: float = 1 / 1
FLYWHEEL_SPEED_ERROR_TOLERANCE: float = radians(1)

BACK_MOTOR_GEAR_RATIO: float = 1 / 1
BACK_MOTOR_SHOOTING_SPEED: float = 12


class Shooter:
    # initialise motor speed
    top_flywheel_speed = tunable(0.0)
    bottom_flywheel_speed = tunable(0.0)
    back_motor_speed = tunable(0.0)

    def __init__(self) -> None:
        # create instances of hardware handles
        self.top_flywheel = CANSparkMax(
            SparkMaxIds.top_flywheel, CANSparkMax.MotorType.kBrushless
        )
        self.bottom_flywheel = CANSparkMax(
            SparkMaxIds.bottom_flywheel, CANSparkMax.MotorType.kBrushless
        )
        self.back_motor = CANSparkMax(
            SparkMaxIds.back_motor, CANSparkMax.MotorType.kBrushless
        )

        self.top_flywheel_encoder = self.top_flywheel.getEncoder()
        self.bottom_flywheel_encoder = self.bottom_flywheel.getEncoder()
        self.back_motor_encoder = self.back_motor.getEncoder()
        self.top_flywheel_encoder.setVelocityConversionFactor(GEAR_RATIO * tau / 60)
        self.bottom_flywheel_encoder.setVelocityConversionFactor(GEAR_RATIO * tau / 60)
        self.back_motor_encoder.setVelocityConversionFactor(
            BACK_MOTOR_GEAR_RATIO * tau / 60
        )

        self.top_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)
        self.bottom_flywheel_speed_controller = PIDController(1.0, 0.0, 0.0)
        self.back_motor_speed_controller = PIDController(1.0, 0.0, 0.0)

        self.loaded_switch = DigitalInput(DioChannels.loaded_shooter)

        # initialise shooting
        # initialise last shooting
        # initialise loading

    def set_flywheel_speed(
        self, top_flywheel_speed: float, bottom_flywheel_speed: float
    ) -> None:
        # update internal motor speed setpoint
        self.top_flywheel_speed = top_flywheel_speed
        self.bottom_flywheel_speed = bottom_flywheel_speed

    def shoot(self) -> None:
        # rotate back motors so the cube is picked up by the flywheels
        self.back_motor_speed = BACK_MOTOR_SHOOTING_SPEED

    def top_flywheel_error(self) -> float:
        return self.top_flywheel_speed - self.top_flywheel_encoder.getVelocity()

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
        )

    def load(self) -> None:
        # set load variable
        # set shooting variable
        pass

    def is_loaded(self) -> bool:
        # return state of loaded switch
        return not self.loaded_switch.get()

    def has_shot(self) -> bool:
        # true if shooting and change time greater than threshold
        return False

    def execute(self) -> None:
        top_voltage = self.top_flywheel_speed_controller.calculate(
            self.top_flywheel_encoder.getVelocity(), self.top_flywheel_speed
        )
        bottom_voltage = self.bottom_flywheel_speed_controller.calculate(
            self.bottom_flywheel_encoder.getVelocity(), self.bottom_flywheel_speed
        )
        back_voltage = self.back_motor_speed_controller.calculate(
            self.back_motor_encoder.getVelocity(), self.back_motor_speed
        )

        self.top_flywheel.setVoltage(top_voltage)
        self.bottom_flywheel.setVoltage(bottom_voltage)
        self.back_motor.setVoltage(back_voltage)
