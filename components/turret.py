from math import radians, tau

from magicbot import feedback, tunable
from rev import CANSparkMax
from wpilib import DigitalInput
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.geometry import Translation3d
from wpimath.trajectory import TrapezoidProfileRadians

from ids import DioChannels, SparkMaxIds

GEAR_RATIO: float = (10 / 1) * (4 / 1) * (140 / 18)
ANGLE_ERROR_TOLERANCE: float = radians(1)
MAX_ANGULAR_VELOCITY: float = 12.0
MAX_ANGULAR_ACCELERATION: float = 2.0
NEGATIVE_LIMIT_ANGLE: float = radians(-112)
POSITIVE_LIMIT_ANGLE: float = radians(112)
INDEX_SEARCH_VOLTAGE: float = 2.0
POSITIVE_SOFT_LIMIT_ANGLE: float = POSITIVE_LIMIT_ANGLE - radians(5)
NEGATIVE_SOFT_LIMIT_ANGLE: float = NEGATIVE_LIMIT_ANGLE + radians(5)


class Turret:
    goal_angle = tunable(0.0)
    index_search_positive = tunable(True)

    TRANSLATION3D: Translation3d = Translation3d(-0.2, 0, 0.3)

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
            8.0, 0.0, 0.0, rotation_contraints
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

    @feedback
    def has_found_index(self) -> bool:
        return self.index_found

    @feedback
    def position_error(self) -> bool:
        return self.rotation_controller.getPositionError()

    @feedback
    def velocity_error(self) -> bool:
        return self.rotation_controller.getVelocityError()

    def find_index(self) -> None:
        self.index_found = False

    def execute(self) -> None:
        self.maybe_rezero_off_limits_switches()

        if self.at_positive_limit() and self.at_negative_limit():
            self.motor.setVoltage(0)
            return
        if self.at_positive_limit():
            self.motor.setVoltage(-INDEX_SEARCH_VOLTAGE)
            return
        if self.at_negative_limit():
            self.motor.setVoltage(INDEX_SEARCH_VOLTAGE)
            return

        if self.index_found:
            # calculate pid output based off angle delta
            pid_output = self.rotation_controller.calculate(
                self.get_angle(), self.goal_angle
            )
            # calcualte feed forward based off angle delta
            self.motor.setVoltage(pid_output)
        else:
            if self.index_search_positive:
                self.motor.setVoltage(INDEX_SEARCH_VOLTAGE)
            else:
                self.motor.setVoltage(-INDEX_SEARCH_VOLTAGE)

    def on_enable(self) -> None:
        self.motor.setIdleMode(CANSparkMax.IdleMode.kBrake)
        self.rotation_controller.reset(self.get_angle())
        self.set_angle(self.get_angle())

    def on_disable(self) -> None:
        self.motor.setIdleMode(CANSparkMax.IdleMode.kCoast)

    def disabled_periodic(self) -> None:
        if self.has_found_index():
            self.set_angle(self.get_angle())
            self.rotation_controller.reset(self.get_angle())

    def maybe_rezero_off_limits_switches(self) -> None:
        if self.at_negative_limit():
            self.set_to_angle(NEGATIVE_LIMIT_ANGLE)
            self.rotation_controller.reset(NEGATIVE_LIMIT_ANGLE)
        if self.at_positive_limit():
            self.set_to_angle(POSITIVE_LIMIT_ANGLE)
            self.rotation_controller.reset(POSITIVE_LIMIT_ANGLE)

    # override the current angle to be angle
    def set_to_angle(self, angle):
        self.encoder.setPosition(angle)
        self.index_found = True
