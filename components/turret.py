from math import pi, radians
from rev import CANSparkMax
from wpilib import DigitalInput
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.trajectory import TrapezoidProfileRadians
from ids import SparkMaxIds, DioChannels

from magicbot import tunable, feedback


GEAR_RATIO: float = (7 / 1) * (4 / 1) * (18 / 140)
ANGLE_ERROR_TOLERANCE: float = radians(1)
MAX_ANGULAR_VELOCITY: float = 1.0
MAX_ANGULAR_ACCELERATION: float = 0.5
NEGATIVE_LIMIT_ANGLE: float = radians(-120)
POSITIVE_LIMIT_ANGLE: float = radians(120)
INDEX_SEARCH_VOLTAGE: float = 2.0


class Turret:
    goal_angle = tunable(0.0)

    def __init__(self) -> None:
        # Create the hardware object handles
        self.motor = CANSparkMax(
            SparkMaxIds.turret_motor, CANSparkMax.MotorType.kBrushless
        )  # This will need to change to the proper motor controller type
        self.motor.setIdleMode(CANSparkMax.IdleMode.kBrake)
        self.motor.setInverted(False)
        self.positive_limit_switch = DigitalInput(DioChannels.positive_turret_switch)
        self.negative_limit_switch = DigitalInput(
            DioChannels.negative_turret_switch
        )  # These could also be attached directly to the motor controller breakout board for interrupts
        self.encoder = self.motor.getEncoder()
        self.encoder.setPositionConversionFactor(GEAR_RATIO)
        self.encoder.setVelocityConversionFactor(GEAR_RATIO)
        rotation_contraints = TrapezoidProfileRadians.Constraints(
            maxVelocity=MAX_ANGULAR_VELOCITY, maxAcceleration=MAX_ANGULAR_ACCELERATION
        )
        self.rotation_controller = ProfiledPIDControllerRadians(
            2, 0.0, 0.0, rotation_contraints
        )
        # set index found var to false
        self.index_found = False

    def set_angle(self, angle: float) -> None:
        # set the desired angle for the turret
        clamped_angle = min(angle, POSITIVE_LIMIT_ANGLE - radians(5))
        clamped_angle = max(clamped_angle, NEGATIVE_LIMIT_ANGLE + radians(5))
        self.goal_angle = clamped_angle

    @feedback
    def get_angle(self) -> float:
        return self.encoder.getPosition()

    @feedback
    def at_angle(self) -> bool:
        # return abs(current angle - reference) < Tolerance
        # This could also be done inside the motor controller depending on how it works
        return abs(self.get_angle() - self.goal_angle) < ANGLE_ERROR_TOLERANCE

    @feedback
    def at_positive_limit(self) -> bool:
        return not self.positive_limit_switch.get()

    @feedback
    def at_negative_limit(self) -> bool:
        return not self.negative_limit_switch.get()

    def find_index(self) -> None:
        self.index_found = False

    def execute(self) -> None:
        if self.at_negative_limit():
            self.encoder.setPosition(NEGATIVE_LIMIT_ANGLE)
            self.index_found = True

        if self.at_positive_limit():
            self.encoder.setPosition(POSITIVE_LIMIT_ANGLE)
            self.index_found = True

        if self.index_found:
            # calculate pid output based off angle delta
            pid_output = self.rotation_controller.calculate(
                self.get_angle(), self.goal_angle
            )
            # calcualte feed forward based off angle delta
            # clamp input

            self.motor.setVoltage(pid_output)
        else:
            # set desired output voltage or speed to find index
            self.motor.setVoltage(INDEX_SEARCH_VOLTAGE)
