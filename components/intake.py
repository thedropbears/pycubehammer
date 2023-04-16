from ctre import WPI_TalonSRX
from magicbot import tunable
from rev import CANSparkMax
from wpilib import DoubleSolenoid, PneumaticsModuleType

import ids


class Intake:
    front_speed = tunable(0.8)
    tunnel_speed = tunable(0.8)
    deployed = tunable(False)

    def __init__(self) -> None:
        self.front_motor = CANSparkMax(
            ids.SparkMaxIds.intake_front, CANSparkMax.MotorType.kBrushless
        )
        self.front_motor.restoreFactoryDefaults()
        self.front_motor.setSmartCurrentLimit(30)
        self.front_motor.setInverted(True)

        self.tunnel_motor = WPI_TalonSRX(ids.TalonIds.intake_tunnel)

        self.piston = DoubleSolenoid(
            PneumaticsModuleType.REVPH,
            ids.PhChannels.intake_piston_forward,
            ids.PhChannels.intake_piston_reverse,
        )

    def deploy(self) -> None:
        self.deployed = True

    def retract(self) -> None:
        self.deployed = False

    def execute(self) -> None:
        if self.deployed:
            self.piston.set(DoubleSolenoid.Value.kForward)
            self.front_motor.set(self.front_speed)
            self.tunnel_motor.set(self.tunnel_speed)
        else:
            self.piston.set(DoubleSolenoid.Value.kReverse)
            self.front_motor.stopMotor()
            self.tunnel_motor.stopMotor()
