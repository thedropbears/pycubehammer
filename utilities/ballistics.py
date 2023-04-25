from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from wpimath.geometry import Pose2d, Translation3d

from utilities.functions import constrain_angle


class GoalHeight(Enum):
    HIGH = 2
    MID = 1
    LOW = 0

    def up(self) -> GoalHeight:
        if self is GoalHeight.LOW:
            return GoalHeight.MID
        return GoalHeight.HIGH

    def down(self) -> GoalHeight:
        if self is GoalHeight.HIGH:
            return GoalHeight.MID
        return GoalHeight.LOW


class GridColumn(Enum):
    LEFT = -1
    CENTRE = 0
    RIGHT = 1

    def left(self) -> GridColumn:
        if self is GridColumn.RIGHT:
            return GridColumn.CENTRE
        return GridColumn.LEFT

    def right(self) -> GridColumn:
        if self is GridColumn.LEFT:
            return GridColumn.CENTRE
        return GridColumn.RIGHT


@dataclass
class BallisticsSolution:
    turret_angle: float
    tilt_angle: float
    top_flywheel_speed: float
    bottom_flywheel_speed: float


def calculate_ballistics(
    robot_pose: Pose2d, target_position: Translation3d
) -> BallisticsSolution:
    azimuth = math.atan2(
        target_position.y - robot_pose.y, target_position.x - robot_pose.x
    )
    turret_angle = constrain_angle(azimuth - robot_pose.rotation().radians())
    bs = BallisticsSolution(
        turret_angle=turret_angle,
        tilt_angle=math.radians(45),
        top_flywheel_speed=300,
        bottom_flywheel_speed=300,
    )
    return bs
