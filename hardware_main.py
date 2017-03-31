from design.decision_making.brain import Brain
from design.interfacing.hardware_controllers import WheelsController, AntennaController, LightsController, PenController
from design.interfacing.interfacing_controller import InterfacingController
from design.interfacing.stm32_driver import Stm32Driver
from design.telemetry.telemetry_mock import TelemetryMock
from design.vision.onboard_vision_mock import OnboardVisionMock
from design.decision_making.movement_strategy import MovementStrategy
from design.decision_making.constants import TranslationStrategyType
from design.decision_making.constants import RotationStrategyType


if __name__ == '__main__':

    microcontroller_driver = Stm32Driver()
    prehensor_driver = None

    my_brain = Brain(TelemetryMock(), InterfacingController(WheelsController(microcontroller_driver
    ), AntennaController(microcontroller_driver), PenController(prehensor_driver), LightsController(microcontroller_driver)),
                     OnboardVisionMock(), MovementStrategy(
                         TranslationStrategyType.VERIFY_CONSTANTLY_THROUGH_CINEMATICS,
                         RotationStrategyType.VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS))
    my_brain.main()
