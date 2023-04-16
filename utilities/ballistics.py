import math
from dataclasses import dataclass
from enum import Enum

from wpimath.geometry import Pose2d

from utilities.functions import constrain_angle


class GoalHeight(Enum):
    HIGH = 2
    MID = 1
    LOW = 0


@dataclass
class BallisticsSolution:
    turret_angle: float
    tilt_angle: float
    top_flywheel_speed: float
    bottom_flywheel_speed: float


def calculate_ballistics(
    robot_pose: Pose2d, target_pose: Pose2d, target_height: GoalHeight
) -> BallisticsSolution:
    azimuth = math.atan2(target_pose.y - robot_pose.y, target_pose.x - robot_pose.x)
    turret_angle = constrain_angle(azimuth - robot_pose.rotation().radians())
    bs = BallisticsSolution(
        turret_angle=turret_angle,
        tilt_angle=math.radians(45),
        top_flywheel_speed=300,
        bottom_flywheel_speed=300,
    )
    return bs
