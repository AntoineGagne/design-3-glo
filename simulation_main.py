from design.decision_making.brain import Brain
from design.interfacing.interfacing_controller import InterfacingController
from design.interfacing.simulated_controllers import (SimulatedWheelsController,
                                                      SimulatedAntennaController,
                                                      SimulatedPenController,
                                                      SimulatedLightsController)
from design.interfacing.stm32_driver import Stm32Driver
from design.telemetry.telemetry_mock import TelemetryMock
from design.vision.onboard_vision_mock import OnboardVisionMock
from design.decision_making.movement_strategy import MovementStrategy
from design.decision_making.constants import TranslationStrategyType
from design.decision_making.constants import RotationStrategyType


if __name__ == '__main__':

    my_brain = Brain(TelemetryMock(), InterfacingController(SimulatedWheelsController(
    ), SimulatedAntennaController(), SimulatedPenController(), SimulatedLightsController()),
                     OnboardVisionMock(), MovementStrategy(
                         TranslationStrategyType.VERIFY_CONSTANTLY_THROUGH_CINEMATICS,
                         RotationStrategyType.VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS))
    my_brain.main()
