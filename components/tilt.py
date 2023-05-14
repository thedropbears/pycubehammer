import math

GEAR_RATIO: float
ANGLE_ERROR_TOLERANCE: float
INTAKING_ANGLE: float = math.radians(90)
MAX_ANGLE: float = math.radians(60)


class Tilt:
    # motor: Neo550 #This will need to change to the proper motor controller type
    # encoder: This will likely be an absolute encoder like the one we used on the arm.
    # ^^ note for this we want to use the absolute api from the start so we dont have a disaster at comp
    # brake: solenoid #This will probably be a double solenoid

    # goal_angle = 0.0

    def __init__(self) -> None:
        # Create the hardware object handles

        pass

    def set_angle(self, angle: float) -> None:
        # set the desired angle for the turret

        # You will need to check the documentation if this can be on the output shaft
        # or if you need to convert the angle back to a motor angle with the gear ratio
        pass

    def goto_intaking(self) -> None:
        self.set_angle(INTAKING_ANGLE)

    def goto_pre_intake(self) -> None:
        self.set_angle(MAX_ANGLE)

    def at_angle(self) -> bool:
        # return abs(current angle - reference) < Tolerance
        # This could also be done inside the motor controller depending on how it works
        return True

    def execute(self) -> None:
        # add logic for engaging and disengaging brake if it exists
        # similar to the real build we will want to add a dead zone where it cant disengage after engaging so we dont drain the tanks too much
        # calculate pid output based off angle delta
        # calcualte feed forward based off angle delta
        # clamp input
        # set motor setpoint
        pass
