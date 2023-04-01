from rev import CANSparkMax
from wpilib import DigitalInput

from ids import DioChannels, SparkMaxIds

GEAR_RATIO: float  # whatever this is


class Shooter:
    # loaded_switch Digital I/O <- in my head this has something to confirm when the shooter is correctly loaded

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

        self.loaded_switch = DigitalInput(DioChannels.loaded_shooter)
        # initialise motor speed
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

    def flywheel_error(self) -> float:
        # return actual velocity - reference velocity
        return 0.0

    def load(self) -> None:
        # set load variable
        # set shooting variable
        pass

    def is_loaded(self) -> bool:
        # return state of loaded switch
        return False

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
