import typing

import robotpy_apriltag
import wpilib
from wpimath.geometry import Pose3d

apriltag_layout = robotpy_apriltag.loadAprilTagLayoutField(
    robotpy_apriltag.AprilTagField.k2023ChargedUp
)
get_fiducial_pose = typing.cast(
    typing.Callable[[typing.Literal[1, 2, 3, 4, 5, 6, 7, 8]], Pose3d],
    apriltag_layout.getTagPose,
)

FIELD_WIDTH = 8.0161
tag_8 = get_fiducial_pose(8)
tag_1 = get_fiducial_pose(1)
FIELD_LENGTH = tag_1.x + tag_8.x


def is_red() -> bool:
    return get_team() == wpilib.DriverStation.Alliance.kRed


def get_team() -> wpilib.DriverStation.Alliance:
    return wpilib.DriverStation.getAlliance()
