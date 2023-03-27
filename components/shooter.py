class Shooter:
    GEAR_RATIO: float  # whatever this is

    # top_flywheel: whatever motor type this is
    # bottom flywheel: whatever motor type this is
    # neck_motor: whatever motor this is <- this refers to the back motor that pulls the cube away from the motors

    # loaded_switch Digital I/O <- in my head this has something to confirm when the shooter is correctly loaded

    def __init__(self) -> None:
        # create instances of hardware handles

        # initialise motor speed
        # initialise shooting
        # initialise last shooting
        # initialise loading
        pass

    def set_flywheel_speed(self) -> None:
        # update internal motor speed setpoint
        pass

    def shoot(self) -> None:
        # rotate back motors so the cube is picked up by the flywheels
        # set loading variable
        pass

    def flywheel_error(self) -> float:
        # return actual velocity - reference velocity
        return 0.0

    def load(self) -> None:
        # set load variable
        # set shooting variable
        pass

    def is_loaded(self) -> bool:
        # return state of loaded switch
        return False

    def has_shot(self) -> bool:
        # true if shooting and change time greater than threshold
        return False

    def execute(self) -> None:
        # if loading
        # update has shootd to false
        # set reverse speed to suck up
        # return

        # if shooting and shooting != last shooting
        # update change time

        # if shooting
        # set forward speed on neck motor

        # update flywheels to setpoint

        pass
