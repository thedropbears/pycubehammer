import math
from dataclasses import dataclass
from enum import Enum

from wpimath.geometry import Pose2d


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
    bs = BallisticsSolution(math.radians(90), math.radians(45), 300, 300)
    return bs
