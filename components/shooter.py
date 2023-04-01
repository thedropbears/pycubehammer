from math import radians, tau

from magicbot import tunable
from rev import CANSparkMax
from wpilib import DigitalInput

from ids import DioChannels, SparkMaxIds

GEAR_RATIO: float = 1 / 1
FLYWHEEL_SPEED_ERROR_TOLERANCE: float = radians(1)


class Shooter:
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
        self.top_flywheel_encoder.setVelocityConversionFactor(GEAR_RATIO * tau / 60)
        self.bottom_flywheel_encoder.setVelocityConversionFactor(GEAR_RATIO * tau / 60)

        self.loaded_switch = DigitalInput(DioChannels.loaded_shooter)

        # initialise motor speed
        self.top_flywheel_speed = tunable(0.0)
        self.bottom_flywheel_speed = tunable(0.0)

        # initialise shooting
        # initialise last shooting
        # initialise loading

    def set_flywheel_speed(self) -> None:
        # update internal motor speed setpoint
        pass

    def shoot(self) -> None:
        # rotate back motors so the cube is picked up by the flywheels
        # set loading variable
        pass

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
        # if loading
        # update has shootd to false
        # set reverse speed to suck up
        # return

        # if shooting and shooting != last shooting
        # update change time

        # if shooting
        # set forward speed on neck motor

        # update flywheels to setpoint

        pass
