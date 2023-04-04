from math import radians, tau

from magicbot import feedback, tunable
from rev import CANSparkMax
from wpilib import DigitalInput
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.trajectory import TrapezoidProfileRadians

from ids import DioChannels, SparkMaxIds

GEAR_RATIO: float = (10 / 1) * (4 / 1) * (140 / 18)
ANGLE_ERROR_TOLERANCE: float = radians(1)
MAX_ANGULAR_VELOCITY: float = 12.0
MAX_ANGULAR_ACCELERATION: float = 0.5
NEGATIVE_LIMIT_ANGLE: float = radians(-112)
POSITIVE_LIMIT_ANGLE: float = radians(112)
INDEX_SEARCH_VOLTAGE: float = 2.0
POSITIVE_SOFT_LIMIT_ANGLE: float = POSITIVE_LIMIT_ANGLE - radians(5)
NEGATIVE_SOFT_LIMIT_ANGLE: float = NEGATIVE_LIMIT_ANGLE + radians(5)


class Turret:
    goal_angle = tunable(0.0)
    index_search_positive = tunable(True)

    def __init__(self) -> None:
        # Create the hardware object handles
        self.motor = CANSparkMax(
            SparkMaxIds.turret_motor, CANSparkMax.MotorType.kBrushless
        )
        self.motor.setIdleMode(CANSparkMax.IdleMode.kBrake)
        self.motor.setInverted(False)
        self.positive_limit_switch = DigitalInput(DioChannels.positive_turret_switch)
        self.negative_limit_switch = DigitalInput(
            DioChannels.negative_turret_switch
        )  # These could also be attached directly to the motor controller breakout board for interrupts
        self.encoder = self.motor.getEncoder()
        self.encoder.setPositionConversionFactor(tau / GEAR_RATIO)
        self.encoder.setVelocityConversionFactor((tau / 60) / GEAR_RATIO)
        rotation_contraints = TrapezoidProfileRadians.Constraints(
            maxVelocity=MAX_ANGULAR_VELOCITY, maxAcceleration=MAX_ANGULAR_ACCELERATION
        )
        self.rotation_controller = ProfiledPIDControllerRadians(
            32.0, 0.0, 0.0, rotation_contraints
        )
        # set index found var to false
        self.index_found = False

    def set_angle(self, angle: float) -> None:
        # set the desired angle for the turret
        clamped_angle = min(angle, POSITIVE_SOFT_LIMIT_ANGLE)
        clamped_angle = max(clamped_angle, NEGATIVE_SOFT_LIMIT_ANGLE)
        self.goal_angle = clamped_angle

    @feedback
    def get_angle(self) -> float:
        return self.encoder.getPosition()

    @feedback
    def at_angle(self) -> bool:
        # return abs(current angle - reference) < Tolerance
        # This could also be done inside the motor controller depending on how it works
        return (
            abs(self.get_angle() - self.goal_angle) < ANGLE_ERROR_TOLERANCE
        ) and self.index_found

    @feedback
    def at_positive_limit(self) -> bool:
        return not self.positive_limit_switch.get()

    @feedback
    def at_negative_limit(self) -> bool:
        return not self.negative_limit_switch.get()

    def find_index(self) -> None:
        self.index_found = False

    def execute(self) -> None:
        current_angle = self.get_angle()
        if self.at_negative_limit() and self.at_positive_limit():
            self.motor.setVoltage(0)
            return

        if self.at_negative_limit():
            self.encoder.setPosition(NEGATIVE_LIMIT_ANGLE)
            current_angle = NEGATIVE_LIMIT_ANGLE
            self.rotation_controller.reset(current_angle)
            self.index_found = True
            self.motor.setVoltage(INDEX_SEARCH_VOLTAGE)
            return

        if self.at_positive_limit():
            self.encoder.setPosition(POSITIVE_LIMIT_ANGLE)
            current_angle = POSITIVE_LIMIT_ANGLE
            self.rotation_controller.reset(current_angle)
            self.index_found = True
            self.motor.setVoltage(-INDEX_SEARCH_VOLTAGE)
            return

        if self.index_found:
            # calculate pid output based off angle delta
            pid_output = self.rotation_controller.calculate(
                current_angle, self.goal_angle
            )
            # calcualte feed forward based off angle delta
            # clamp input

            self.motor.setVoltage(pid_output)
        else:
            if self.index_search_positive:
                self.motor.setVoltage(INDEX_SEARCH_VOLTAGE)
            else:
                self.motor.setVoltage(-INDEX_SEARCH_VOLTAGE)
