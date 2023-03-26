import math

class Turret:
  GEAR_RATION: float
  ANGLE_ERROR_TOLERANCE: float
  
  motor: Neo550 #This will need to change to the proper motor controller type
  positive_limit_switch: Digital I/O
  negative_limit_switch: Digital I/O # These could also be attached directly to the motor controller breakout board for interrupts

  goal_angle = 0.0

  def __init__(self) -> None:
    # Create the hardware object handles

    # set index found var to false
    pass

  def set_angle(self, angle: float) -> None:
    # set the desired angle for the turret

    # You will need to check the documentation if this can be on the output shaft 
    # or if you need to convert the angle back to a motor angle with the gear ratio
    pass

  def at_angle(self) -> bool:
    # return abs(current angle - reference) < Tolerance 
    # This could also be done inside the motor controller depending on how it works
    pass

  def find_index(self) -> None:
    # configure turret to rotate until it finds an index 
    # probaly speed or voltage for this
    pass

  def execute(self) -> None:
    
    #if index found:
      # calculate pid output based off angle delta
      #calcualte feed forward based off angle delta
      # clamp input
      # set motor setpoint
    #else:
      # set desired output voltage or speed to find index
    pass