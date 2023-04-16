import robotpy_apriltag
import wpilib

apriltag_layout = robotpy_apriltag.loadAprilTagLayoutField(
    robotpy_apriltag.AprilTagField.k2023ChargedUp
)

FIELD_WIDTH = 8.0161
tag_8 = apriltag_layout.getTagPose(8)
tag_1 = apriltag_layout.getTagPose(1)
# for type checker
assert tag_8 is not None and tag_1 is not None
FIELD_LENGTH = tag_1.x + tag_8.x


def is_red() -> bool:
    return get_team() == wpilib.DriverStation.Alliance.kRed


def get_team() -> wpilib.DriverStation.Alliance:
    return wpilib.DriverStation.getAlliance()
