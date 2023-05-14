import math

from magicbot import (
    StateMachine,
    default_state,
    feedback,
    state,
    timed_state,
    will_reset_to,
)
from wpimath.geometry import Rotation3d, Transform3d, Translation3d

from components.chassis import Chassis
from components.intake import Intake
from components.shooter import Shooter
from components.tilt import Tilt
from components.turret import Turret
from utilities import game
from utilities.ballistics import GoalHeight, GridColumn, calculate_ballistics


class ShooterController(StateMachine):
    chassis_component: Chassis
    intake_component: Intake
    shooter_component: Shooter
    tilt_component: Tilt
    turret_component: Turret

    try_shoot = will_reset_to(False)

    def __init__(self) -> None:
        self.goal_height_preference = GoalHeight.HIGH  # default preference
        self.column_preference = GridColumn.CENTRE  # selected hybrid node
        self.goal_id = -1  # No valid selection until controller is run

    @state(first=True, must_finish=True)
    def preparing_intake(self) -> None:
        self.turret_component.set_angle(0.0)
        self.tilt_component.goto_intaking()

        if self.turret_component.at_angle() and self.tilt_component.at_angle():
            self.next_state("intaking")

    @state(must_finish=True)
    def intaking(self) -> None:
        self.intake_component.deploy()
        self.shooter_component.load()

        if self.shooter_component.is_loaded():
            self.intake_component.retract()
            self.next_state("tracking")

    @default_state
    def tracking(self) -> None:
        self.update_component_setpoints()

        if (
            self.try_shoot
            and self.shooter_component.is_ready()
            and self.turret_component.at_angle()
            and self.tilt_component.at_angle()
        ):
            self.next_state("shooting")

    @timed_state(must_finish=True, duration=1.0)
    def shooting(self) -> None:
        self.update_component_setpoints()
        self.shooter_component.shoot()

    def update_component_setpoints(self) -> None:
        position = self.get_target_position()
        bs = calculate_ballistics(self.chassis_component.get_pose(), position)
        # Check to see if we need to flip the shooter around
        # If we are beyond the turret endpoints we have to flip
        if bs.turret_angle < Turret.NEGATIVE_SOFT_LIMIT_ANGLE:
            bs.turret_angle += math.pi
            bs.tilt_angle = -bs.tilt_angle
        if bs.turret_angle > Turret.POSITIVE_SOFT_LIMIT_ANGLE:
            bs.turret_angle -= math.pi
            bs.tilt_angle = -bs.tilt_angle

        # We also have an overlap zone so that we don't keep flipping back and forth
        if bs.turret_angle > math.pi / 2.0 and self.turret_component.get_angle() < 0.0:
            # We are already flipped, so keep it flipped
            bs.turret_angle -= math.pi
            bs.tilt_angle = -bs.tilt_angle
        if bs.turret_angle < -math.pi / 2.0 and self.turret_component.get_angle() > 0.0:
            # We are already flipped, so keep it flipped
            bs.turret_angle += math.pi
            bs.tilt_angle = -bs.tilt_angle

        self.turret_component.set_angle(bs.turret_angle)
        self.tilt_component.set_angle(bs.tilt_angle)
        # We can be tracking the targets even if we don't have a cube
        # No need to run the flywheels if we can't shoot
        if self.shooter_component.is_loaded():
            self.shooter_component.set_flywheel_speed(
                bs.top_flywheel_speed, bs.bottom_flywheel_speed
            )
        else:
            self.shooter_component.stop()

    def get_target_position(self) -> Translation3d:
        robot_pose = self.chassis_component.get_pose()
        best_tag_position, self.goal_id = game.find_closest_tag(robot_pose)
        # Offset the tag position to be at the centre of the relevant goal
        # Each goal is 42cm deep
        if self.goal_height_preference == GoalHeight.HIGH:
            depth = -(0.42 + 0.42 / 2.0)
            height = 0.45
            breadth = 0.0
        elif self.goal_height_preference == GoalHeight.MID:
            depth = -0.42 / 2.0
            height = 0.05
            breadth = 0.0
        else:
            depth = 0.42 / 2.0
            height = -0.45
            # distance between centre of cone nodes in a grid row is 44"
            breadth = 44.0 / 2.0 * 0.0254 * self.column_preference.value

        translation = Translation3d(depth, breadth, height)
        transform = Transform3d(translation, Rotation3d())

        target = best_tag_position.transformBy(transform)
        return target.translation()

    def shoot(self) -> None:
        self.try_shoot = True

    def intake(self) -> None:
        if not self.shooter_component.is_loaded():
            self.engage()

    def select_up(self) -> None:
        self.goal_height_preference = self.goal_height_preference.up()

    def select_down(self) -> None:
        self.goal_height_preference = self.goal_height_preference.down()

    def select_left(self) -> None:
        self.goal_height_preference = GoalHeight.LOW
        self.column_preference = self.column_preference.left()

    def select_right(self) -> None:
        self.goal_height_preference = GoalHeight.LOW
        self.column_preference = self.column_preference.right()

    def prefer_high(self) -> None:
        self.goal_height_preference = GoalHeight.HIGH

    def prefer_mid(self) -> None:
        self.goal_height_preference = GoalHeight.MID

    def prefer_low(self) -> None:
        self.goal_height_preference = GoalHeight.LOW

    @feedback
    def get_column_preference(self) -> str:
        return self.column_preference.name

    @feedback
    def get_goal_height_preference(self) -> str:
        return self.goal_height_preference.name

    @feedback
    def get_goal_id(self) -> int:
        return self.goal_id

    @feedback
    def is_high_node_selected(self) -> bool:
        return self.goal_height_preference is GoalHeight.HIGH

    @feedback
    def is_mid_node_selected(self) -> bool:
        return self.goal_height_preference is GoalHeight.MID

    @feedback
    def is_left_hybrid_node_selected(self) -> bool:
        return (
            self.goal_height_preference is GoalHeight.LOW
            and self.column_preference is GridColumn.LEFT
        )

    @feedback
    def is_centre_hybrid_node_selected(self) -> bool:
        return (
            self.goal_height_preference is GoalHeight.LOW
            and self.column_preference is GridColumn.CENTRE
        )

    @feedback
    def is_right_hybrid_node_selected(self) -> bool:
        return (
            self.goal_height_preference is GoalHeight.LOW
            and self.column_preference is GridColumn.RIGHT
        )
