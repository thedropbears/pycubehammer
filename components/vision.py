import math
import typing
from typing import Optional

import wpilib
import wpiutil.log
from magicbot import tunable
from photonvision import PhotonCamera, PhotonTrackedTarget
from wpimath.geometry import Pose2d, Rotation3d, Transform3d, Translation3d

from components.chassis import Chassis
from components.turret import ITurret, Turret
from utilities.game import apriltag_layout


class VisualLocaliser:
    """
    This localises the robot from AprilTags on the field,
    using information from a single PhotonVision camera.
    """

    add_to_estimator = tunable(True)
    should_log = tunable(False)

    rejected_in_row = tunable(0.0)
    last_pose_z = tunable(0.0, writeDefault=False)
    range = tunable(0.0)

    def __init__(
        self,
        # The name of the camera in PhotonVision.
        name: str,
        # Position of the camera relative to the center of the robot
        pos: Translation3d,
        # The camera rotation.
        rot: Rotation3d,
        field: wpilib.Field2d,
        data_log: wpiutil.log.DataLog,
        chassis_component: Chassis,
        turret_component: ITurret,
    ) -> None:
        self.camera = PhotonCamera(name)
        self.camera_rotation = rot
        self.camera_position = pos
        self.last_timestamp = -1

        self.field_pos_obj = field.getObject("vision_pose_" + name)
        self.pose_log_entry = wpiutil.log.DoubleArrayLogEntry(
            data_log, "vision_pose_" + name
        )

        self.chassis_component = chassis_component
        self.turret_component = turret_component

    def execute(self) -> None:
        # if results didn't see any targets
        if not (results := self.camera.getLatestResult()).hasTargets():
            return

        # if we have already processed these results
        timestamp = results.getTimestamp()
        if timestamp == self.last_timestamp and wpilib.RobotBase.isReal():
            return
        self.last_timestamp = timestamp

        # old results cause pose estimator to crash and aren't very useful anyway
        if abs(wpilib.Timer.getFPGATimestamp() - timestamp) > 0.5:
            return

        turret_rotation = Rotation3d.fromDegrees(
            0, 0, math.degrees(self.turret_component.get_angle())
        )

        camera_rotation = self.camera_rotation.rotateBy(turret_rotation)
        camera_position = (
            self.camera_position.rotateBy(turret_rotation) + Turret.TRANSLATION3D
        )
        camera_to_robot = Transform3d(camera_position, camera_rotation).inverse()
        for target in results.getTargets():
            poses = estimate_poses_from_apriltag(camera_to_robot, target)
            if poses is None:
                # tag doesn't exist
                continue
            self.range = target.getBestCameraToTarget().inverse().translation().norm()

            best_pose, alt_pose, self.last_pose_z = poses
            pose = choose_pose(
                best_pose,
                alt_pose,
                self.chassis_component.get_pose(),
                target.getPoseAmbiguity(),
            )

            # filter out likely bad targets
            if target.getPoseAmbiguity() > 0.25 or abs(target.getYaw()) > 20:
                continue

            self.field_pos_obj.setPose(pose)
            change = (
                self.chassis_component.get_pose()
                .translation()
                .distance(pose.translation())
            )
            if change > 1.0:
                self.rejected_in_row += 1
                if self.rejected_in_row < 20:
                    continue
            else:
                self.rejected_in_row //= 2

            if self.add_to_estimator:
                self.chassis_component.estimator.addVisionMeasurement(
                    pose,
                    timestamp,
                    (3.0, 3.0, 1.0),
                )

            if self.should_log:
                ground_truth_pose = self.chassis_component.get_pose()
                trans_error1: float = ground_truth_pose.translation().distance(
                    best_pose.translation()
                )
                trans_error2: float = ground_truth_pose.translation().distance(
                    alt_pose.translation()
                )
                rot_error1: float = (
                    ground_truth_pose.rotation() - best_pose.rotation()
                ).radians()
                rot_error2: float = (
                    ground_truth_pose.rotation() - alt_pose.rotation()
                ).radians()
                skew = get_target_skew(target)

                self.pose_log_entry.append(
                    [
                        best_pose.x,
                        best_pose.y,
                        typing.cast(float, best_pose.rotation().radians()),
                        trans_error1,  # error of main pose
                        rot_error1,
                        alt_pose.x,
                        alt_pose.y,
                        typing.cast(float, alt_pose.rotation().radians()),
                        trans_error2,
                        rot_error2,
                        ground_truth_pose.x,
                        ground_truth_pose.y,
                        target.getYaw(),
                        skew,
                        target.getPoseAmbiguity(),
                        target.getArea(),
                        target.getFiducialId(),
                    ]
                )


def estimate_poses_from_apriltag(
    cam_to_robot: Transform3d, target: PhotonTrackedTarget
) -> Optional[tuple[Pose2d, Pose2d, float]]:
    tag_id = target.getFiducialId()
    tag_pose = apriltag_layout.getTagPose(tag_id)
    if tag_pose is None:
        return None

    best_pose = tag_pose.transformBy(
        target.getBestCameraToTarget().inverse()
    ).transformBy(cam_to_robot)
    alternate_pose = (
        tag_pose.transformBy(target.getAlternateCameraToTarget().inverse())
        .transformBy(cam_to_robot)
        .toPose2d()
    )
    return best_pose.toPose2d(), alternate_pose, best_pose.z


def get_target_skew(target: PhotonTrackedTarget):
    tag_to_cam = target.getBestCameraToTarget().inverse()
    return math.atan2(tag_to_cam.y, tag_to_cam.x)


def choose_pose(
    best_pose: Pose2d, alternate_pose: Pose2d, cur_robot: Pose2d, ambiguity: float
):
    """Picks either the best or alternate pose estimate"""
    return best_pose
