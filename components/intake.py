class Intake:
    # front_motor: whatever motor type it is
    # tunnel_motor: whatever motor type this is # this also assumes that the two stages are not slaved together
    # deployment_piston: solenoid

    # deployed

    def __init__(self) -> None:
        # create hardware handles here

        # initialise deployed var

        pass

    def deploy(self) -> None:
        # set deployed var

        pass

    def retract(self) -> None:
        # set deployed var
        pass

    def execute(self) -> None:
        # If deployed var
        # actuate piston and spin up motors
        # else:
        # actuate piston and stop motors
        pass
