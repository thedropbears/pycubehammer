import math

from magicbot import feedback
from rev import CANSparkMax
from wpilib import DutyCycleEncoder, SmartDashboard
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.trajectory import TrapezoidProfileRadians

from ids import DioChannels, SparkMaxIds
from utilities.functions import clamp

INTAKING_ANGLE: float = math.radians(90)
ANGLE_ERROR_TOLERANCE: float = math.radians(1)
MAX_ANGULAR_VELOCITY: float = 12.0
MAX_ANGULAR_ACCELERATION: float = 0.5
POSITIVE_SOFT_LIMIT_ANGLE: float = math.radians(67)
NEGATIVE_SOFT_LIMIT_ANGLE: float = math.radians(-67)
TILT_ENCODER_ANGLE_OFFSET: float = 0.9012


class Tilt:
    goal_angle = 0.0

    def __init__(self) -> None:
        self.motor = CANSparkMax(
            SparkMaxIds.tilt_motor, CANSparkMax.MotorType.kBrushless
        )
        self.absolute_encoder = DutyCycleEncoder(DioChannels.tilt_absolute_encoder)
        self.absolute_encoder.setDistancePerRotation(-math.pi)
        self.absolute_encoder.setPositionOffset(TILT_ENCODER_ANGLE_OFFSET)

        rotation_contraints = TrapezoidProfileRadians.Constraints(
            maxVelocity=MAX_ANGULAR_VELOCITY, maxAcceleration=MAX_ANGULAR_ACCELERATION
        )
        self.rotation_controller = ProfiledPIDControllerRadians(
            10.0, 0.0, 0.0, rotation_contraints
        )
        SmartDashboard.putData("tilt_pid", self.rotation_controller)

    def set_angle(self, angle: float) -> None:
        # set the desired angle for the turret
        self.goal_angle = clamp(
            angle, NEGATIVE_SOFT_LIMIT_ANGLE, POSITIVE_SOFT_LIMIT_ANGLE
        )

    @feedback
    def get_angle(self) -> float:
        """
        Get the tilt angle in radians.

        0 is the shooter pointing upwards along the vertical axis,
        positive downwards along the front of the shooter.
        """
        return self.absolute_encoder.getDistance()

    def goto_intaking(self) -> None:
        self.set_angle(INTAKING_ANGLE)

    @feedback
    def at_angle(self) -> bool:
        current_angle = self.get_angle()
        # This could also be done inside the motor controller depending on how it works
        return abs(current_angle - self.goal_angle) < ANGLE_ERROR_TOLERANCE

    def execute(self) -> None:
        current_angle = self.get_angle()
        pid_output = self.rotation_controller.calculate(current_angle, self.goal_angle)

        self.motor.setVoltage(pid_output)
