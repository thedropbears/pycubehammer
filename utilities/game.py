import typing

import robotpy_apriltag
import wpilib
from wpimath.geometry import Pose2d, Pose3d

apriltag_layout = robotpy_apriltag.loadAprilTagLayoutField(
    robotpy_apriltag.AprilTagField.k2023ChargedUp
)

TagId = typing.Literal[1, 2, 3, 4, 5, 6, 7, 8]
get_fiducial_pose = typing.cast(
    typing.Callable[[TagId], Pose3d],
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


def get_grid_tag_ids() -> tuple[TagId, TagId, TagId]:
    """Get our alliance's grids' tag IDs."""
    return (1, 2, 3) if is_red() else (6, 7, 8)


def find_closest_tag(robot_pose: Pose2d) -> tuple[Pose3d, int]:
    tag_ids = get_grid_tag_ids()

    # Use the first tag to set a baseline for distance
    best_id = tag_ids[0]
    best_tag = get_fiducial_pose(best_id)

    closest_distance = robot_pose.translation().distance(
        best_tag.toPose2d().translation()
    )

    for tag_id in tag_ids[1:]:
        tag = get_fiducial_pose(tag_id)
        d = robot_pose.translation().distance(tag.toPose2d().translation())
        if d < closest_distance:
            closest_distance = d
            best_tag = tag
            best_id = tag_id
    return best_tag, best_id
