import enum


@enum.unique
class TalonIds(enum.IntEnum):
    drive_1 = 1
    steer_1 = 5

    drive_2 = 2
    steer_2 = 6

    drive_3 = 3
    steer_3 = 7

    drive_4 = 4
    steer_4 = 8

    shooter_back = 12


@enum.unique
class CancoderIds(enum.IntEnum):
    swerve_1 = 1
    swerve_2 = 2
    swerve_3 = 3
    swerve_4 = 4


@enum.unique
class SparkMaxIds(enum.IntEnum):
    intake_front = 3

    turret_motor = 1
    top_flywheel = 10
    bottom_flywheel = 11


@enum.unique
class PhChannels(enum.IntEnum):
    intake_piston_forward = 4
    intake_piston_reverse = 5


@enum.unique
class PwmChannels(enum.IntEnum):
    pass


@enum.unique
class DioChannels(enum.IntEnum):
    positive_turret_switch = 1
    negative_turret_switch = 2
    loaded_shooter = 0
