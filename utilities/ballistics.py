import math
from dataclasses import dataclass
from enum import Enum

from wpimath.geometry import Pose2d, Translation3d

from utilities.functions import constrain_angle, interpolate


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
    robot_pose: Pose2d, target_position: Translation3d
) -> BallisticsSolution:
    dy = target_position.y - robot_pose.y
    dx = target_position.x - robot_pose.x
    distance = math.hypot(dy, dx)
    azimuth = math.atan2(dy, dx)
    turret_angle = constrain_angle(azimuth - robot_pose.rotation().radians())
    # We have to have different lookup tables for high, mid and low goals
    if target_position.z < 0.30:
        # Low goal
        bs = _get_low_solution(distance)
    elif target_position.z < 0.60:
        # Mid goal
        bs = _get_mid_solution(distance)
    else:
        # High goal
        bs = _get_high_solution(distance)
    bs.turret_angle = turret_angle
    return bs


def _get_high_solution(target_range: float) -> BallisticsSolution:
    ranges = [0.0, 1.0]
    angles = [math.radians(45), math.radians(30)]
    top_speeds = [100.0, 200.0]
    bottom_speeds = [200.0, 300.0]
    return _interp(target_range, ranges, angles, top_speeds, bottom_speeds)


def _get_mid_solution(target_range: float) -> BallisticsSolution:
    ranges = [0.0, 1.0]
    angles = [math.radians(45), math.radians(30)]
    top_speeds = [100.0, 200.0]
    bottom_speeds = [200.0, 300.0]
    return _interp(target_range, ranges, angles, top_speeds, bottom_speeds)


def _get_low_solution(target_range: float) -> BallisticsSolution:
    ranges = [0.0, 1.0]
    angles = [math.radians(45), math.radians(30)]
    top_speeds = [100.0, 200.0]
    bottom_speeds = [200.0, 300.0]
    return _interp(target_range, ranges, angles, top_speeds, bottom_speeds)


def _interp(
    target_range: float,
    ranges: list[float],
    angles: list[float],
    top_speeds: list[float],
    bottom_speeds: list[float],
) -> BallisticsSolution:
    angle = interpolate(target_range, ranges, angles)
    top_speed = interpolate(target_range, ranges, top_speeds)
    bottom_speed = interpolate(target_range, ranges, bottom_speeds)
    bs = BallisticsSolution(
        turret_angle=0,
        tilt_angle=angle,
        top_flywheel_speed=top_speed,
        bottom_flywheel_speed=bottom_speed,
    )
    return bs
