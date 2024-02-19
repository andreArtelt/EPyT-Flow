from typing import Any
from copy import deepcopy
import json

from ..uncertainty import GaussianUncertainty, UniformUncertainty, ModelUncertainty, SensorNoise,\
    Uncertainty
from .sensor_config import SensorConfig
from .scada import AdvancedControlModule
from .events import SystemEvent, SensorReadingEvent
from .events.sensor_faults import SensorFaultConstant, SensorFaultDrift, SensorFaultGaussian,\
    SensorFaultPercentage, SensorFaultStuckZero
from .events.leakages import AbruptLeakage, IncipientLeakage
from ..serialization import serializable, Serializable, SCENARIO_CONFIG_ID


@serializable(SCENARIO_CONFIG_ID)
class ScenarioConfig(Serializable):
    """
    Configuration of a scenario.

    Parameters
    ----------
    f_inp_in : `str`
        Path to the .inp file.
    f_msx_in : `str`, optional
        Path to the .msx file -- optional, only necessary if EPANET-MSX is used.

        The default is None
    general_params : `dict`, optional
        General parameters such as the demand model, hydraulic time steps, etc.

        The default is None
    sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`, optional
        Specification of all sensors.

        The default is None
    sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`, optional
        Speciation of sensor noise -- i.e. noise/uncertainty affecting the sensor readings.

        The default is None
    controls : `list[`:class:`~epyt_flow.simulation.scada.advanced_control.AdvancedControlModule` `]`, optional
        List of control modules that are active during the simulation.

        The default is an empty list.
    model_uncertainty : :class:`~epyt_flow.uncertainty.model_uncertainty.ModelUncertainty`, optional
        Specification of model uncertainty.
    system_events : `list[`:class:`~epyt_flow.simulation.events.system_event.SystemEvent` `]`, optional
        List of system events -- i.e. events that directly affect the simulation (e.g. leakages).

        The default is an empty list.
    sensor_reading_events : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent` `]`, optional
        List of sensor reading events -- i.e. events that affect the readings of sensors.

        The default is an empty list.

    Attributes
    ----------
    f_inp_in : `str`
        Path to the .inp file.
    f_msx_in : `str`
        Path to the .msx file -- only set if EPANET-MSX is used.
    general_params : `dict`
        General parameters such as the demand model, hydraulic time steps, etc.
    sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
        Specification of all sensors.
    sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`
        Speciation of sensor noise -- i.e. noise/uncertainty affecting the sensor readings.
    controls : `list[`:class:`~epyt_flow.simulation.scada.advanced_control.AdvancedControlModule` `]`
        List of control modules that are active during the simulation.
    model_uncertainty : :class:`~epyt_flow.uncertainty.model_uncertainty.ModelUncertainty`
        Specification of model uncertainty.
    system_events : `list[`:class:`~epyt_flow.simulation.events.system_event.SystemEvent` `]`
        List of system events -- i.e. events that directly affect the simulation (e.g. leakages).
    sensor_reading_events : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent` `]`
        List of sensor reading events -- i.e. events that affect the readings of sensors.
    """
    def __init__(self, f_inp_in:str, f_msx_in:str=None, general_params:str=None,
                 sensor_config:SensorConfig=None, controls:list[AdvancedControlModule]=[],
                 sensor_noise:SensorNoise=None, model_uncertainty=ModelUncertainty(),
                 system_events:list[SystemEvent]=[],
                 sensor_reading_events:list[SensorReadingEvent]=[], **kwds):
        if not isinstance(f_inp_in, str):
            raise TypeError("'f_inp_in' must be an instance of 'str' "+\
                            f"but no of '{type(f_inp_in)}'")
        if f_msx_in is not None:
            if not isinstance(f_msx_in, str):
                raise TypeError("'f_msx_in' must be an instance of 'str' "+\
                                f"but no of '{type(f_msx_in)}'")
        if general_params is not None:
            if not isinstance(general_params, dict):
                raise TypeError("'general_params' must be an instance of 'dict' "+\
                                f"but not of '{type(general_params)}'")
        if sensor_config is not None:
            if not isinstance(sensor_config, SensorConfig):
                raise TypeError("'sensor_config' must be an instance of "+\
                                "'epyt_flow.simulation.SensorConfig' but not of "+\
                                    f"'{type(sensor_config)}'")
        if not isinstance(controls, list):
            raise TypeError("'controls' must be an instance of "+\
                            "'list[epyt_flow.simualtion.scada.AdvancedControlModule]' but no of "+\
                                f"'{type(controls)}'")
        if len(controls) != 0:
            if any(not isinstance(c, AdvancedControlModule) for c in controls):
                raise TypeError("Each item in 'controls' must be an instance of "+\
                                "'epyt_flow.simualtion.scada.AdvancedControlModule'")
        if sensor_noise is not None:
            if not isinstance(sensor_noise, SensorNoise):
                raise TypeError("'sensor_noise' must be an instance of "+\
                                "'epyt_flow.uncertainty.SensorNoise' but not of "+\
                                    f"'{type(sensor_noise)}'")
        if not isinstance(model_uncertainty, ModelUncertainty):
            raise TypeError("'model_uncertainty' must be an instance of "+\
                            "'epyt_flow.uncertainty.ModelUncertainty' but not of "+\
                                f"'{type(model_uncertainty)}'")
        if not isinstance(system_events, list):
            raise TypeError("'system_events' must be an instance of "+\
                            "'list[epyt_flow.simualtion.events.SystemEvent]' but no of "+\
                                f"'{type(system_events)}'")
        if len(system_events) != 0:
            if any(not isinstance(c, SystemEvent) for c in system_events):
                raise TypeError("Each item in 'system_events' must be an instance of "+\
                                "'epyt_flow.simualtion.events.SystemEvent'")
        if not isinstance(sensor_reading_events, list):
            raise TypeError("'sensor_reading_events' must be an instance of "+\
                            "'list[epyt_flow.simualtion.events.SensorReadingEvent]' but not of "+\
                                f"'{type(sensor_reading_events)}'")
        if len(sensor_reading_events) != 0:
            if any(not isinstance(c, SensorReadingEvent) for c in sensor_reading_events):
                raise TypeError("Each item in 'sensor_reading_events' must be an instance of "+\
                                "'epyt_flow.simualtion.events.SensorReadingEvent'")

        self.__f_inp_in = f_inp_in
        self.__f_msx_in = f_msx_in
        self.__general_params = general_params
        self.__sensor_config = sensor_config
        self.__controls = controls
        self.__sensor_noise = sensor_noise
        self.__model_uncertainty = model_uncertainty
        self.__system_events = system_events
        self.__sensor_reading_events = sensor_reading_events

        super().__init__(**kwds)

    @property
    def f_inp_in(self) -> str:
        return self.__f_inp_in

    @property
    def f_msx_in(self) -> str:
        return self.__f_msx_in

    @property
    def general_params(self) -> dict:
        return deepcopy(self.__general_params)

    @property
    def sensor_config(self) -> SensorConfig:
        return deepcopy(self.__sensor_config)

    @property
    def controls(self) -> list[AdvancedControlModule]:
        return deepcopy(self.__controls)

    @property
    def sensor_noise(self) -> list[SensorNoise]:
        return deepcopy(self.__sensor_noise)

    @property
    def model_uncertainty(self) -> ModelUncertainty:
        return deepcopy(self.__model_uncertainty)

    @property
    def system_events(self) -> list[SystemEvent]:
        return deepcopy(self.__system_events)

    @property
    def sensor_reading_events(self) -> list[SensorReadingEvent]:
        return deepcopy(self.__sensor_reading_events)

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"f_inp_in": self.__f_inp_in, "f_msx_in": self.__f_msx_in,
                                           "general_params": self.__general_params,
                                           "sensor_config": self.__sensor_config,
                                           "controls": self.__controls,
                                           "sensor_noise": self.__sensor_noise,
                                           "model_uncertainty": self.__model_uncertainty,
                                           "system_events": self.__system_events,
                                           "sensor_reading_events": self.__sensor_reading_events}

    def __eq__(self, other) -> bool:
        return self.__f_inp_in == other.f_inp_in and self.__f_msx_in == other.f_msx_in \
            and self.__general_params == other.general_params \
            and self.__sensor_config == other.sensor_config and self.__controls == other.controls \
            and self.__model_uncertainty == other.model_uncertainty \
            and self.__system_events == other.system_events \
            and self.__sensor_reading_events == other.sensor_reading_events

    def __str__(self) -> str:
        return f"f_inp_in: {self.f_inp_in} f_msx_in: {self.f_msx_in} "+\
            f"general_params: {self.general_params} sensor_config: {self.sensor_config} "+\
            f"controls: {self.controls} sensor_noise: {self.sensor_noise} "+\
            f"model_uncertainty: {self.model_uncertainty} "+\
            f"system_events: {','.join(map(str, self.system_events))} "+\
            f"sensor_reading_events: {','.join(map(str, self.sensor_reading_events))}"

    @staticmethod
    def load_from_json(config_data:str) -> Any:
        """
        Loads a scenario configuration from a given JSON string.

        Parameters
        ----------
        config_data : `str`
            JSON data.
        
        Returns
        -------
        :class:`~epyt_flow.simulation.scenario_config.ScenarioConfig`
            Loaded scenario configuration.
        """
        data = json.loads(config_data)

        # General parameters and sensor configuration
        general_settings = data["general"]
        f_inp_in = general_settings["file_inp"]
        f_msx_in = general_settings["file_msx"] if "file_msx" in general_settings.keys() else None

        general_params = {}
        general_params["simulation_duration"] = general_settings["simulation_duration"]
        general_params["hydraulic_time_step"] = general_settings["hydraulic_time_step"]
        general_params["quality_time_step"] = general_settings["quality_time_step"]
        if "demand_model" in general_settings.keys():
            general_params["demand_model"] = general_settings["demand_model"]
        if "quality_model" in general_settings.keys():
            general_params["quality_model"] = general_settings["quality_model"]

        sensor_config = data["sensors"]
        if "pressure_sensors" in sensor_config.keys():
            pressure_sensors = sensor_config["pressure_sensors"]
        else:
            pressure_sensors = []
        if "flow_sensors" in sensor_config.keys():
            flow_sensors = sensor_config["flow_sensors"]
        else:
            flow_sensors = []
        if "demand_sensors" in sensor_config.keys():
            demand_sensors = sensor_config["demand_sensors"]
        else:
            demand_sensors = []
        if "node_quality_sensors" in sensor_config.keys():
            node_quality_sensors = sensor_config["node_quality_sensors"]
        else:
            node_quality_sensors = []
        if "link_quality_sensors" in sensor_config.keys():
            link_quality_sensors = sensor_config["link_quality_sensors"]
        else:
            link_quality_sensors = []
        if "tank_level_sensors" in sensor_config.keys():
            tank_level_sensors = sensor_config["tank_level_sensor"]
        else:
            tank_level_sensors = []
        if "valve_state_sensors" in sensor_config.keys():
            valve_state_sensors = sensor_config["valve_state_sensors"]
        else:
            valve_state_sensors = []
        if "pump_state_sensors" in sensor_config.keys():
            pump_state_sensors = sensor_config["pump_state_sensors"]
        else:
            pump_state_sensors = []

        # Uncertainties
        if "uncertainties" in data.keys():
            def parse_uncertantiy(uncertainty_desc:dict) -> Uncertainty:
                uncertainty_type = uncertainty_desc["type"]
                del uncertainty_desc["type"]

                if uncertainty_type== "gaussian":
                    return GaussianUncertainty(**uncertainty_desc)
                elif uncertainty_type == "uniform":
                    return UniformUncertainty(**uncertainty_desc)
                else:
                    raise ValueError(f"Unknown uncertainty '{uncertainty_type}'")

            uncertanties = data["uncertainties"]
            if "pipe_length_uncertainty" in uncertanties.keys():
                pipe_length_uncertainty = parse_uncertantiy(uncertanties["pipe_length_uncertainty"])
            else:
                pipe_length_uncertainty = None
            if "pipe_roughness_uncertainty" in uncertanties.keys():
                pipe_roughness_uncertainty = parse_uncertantiy(
                    uncertanties["pipe_roughness_uncertainty"])
            else:
                pipe_roughness_uncertainty = None
            if "pipe_diameter_uncertainty" in uncertanties.keys():
                pipe_diameter_uncertainty = parse_uncertantiy(
                    uncertanties["pipe_diameter_uncertainty"])
            else:
                pipe_diameter_uncertainty = None
            if "demand_base_uncertainty" in uncertanties.keys():
                demand_base_uncertainty = parse_uncertantiy(uncertanties["demand_base_uncertainty"])
            else:
                demand_base_uncertainty = None
            if "demand_pattern_uncertainty" in uncertanties.keys():
                demand_pattern_uncertainty = parse_uncertantiy(
                    uncertanties["demand_pattern_uncertainty"])
            else:
                demand_pattern_uncertainty = None
            if "elevation_uncertainty" in uncertanties.keys():
                elevation_uncertainty = parse_uncertantiy(uncertanties["elevation_uncertainty"])
            else:
                elevation_uncertainty = None
            if "constants_uncertainty" in uncertanties.keys():
                constants_uncertainty = parse_uncertantiy(uncertanties["constants_uncertainty"])
            else:
                constants_uncertainty = None
            if "parameters_uncertainty" in uncertanties.keys():
                parameters_uncertainty = parse_uncertantiy(uncertanties["parameters_uncertainty"])
            else:
                parameters_uncertainty = None

            model_uncertainty = ModelUncertainty(pipe_length_uncertainty,
                                                 pipe_roughness_uncertainty,
                                                 pipe_diameter_uncertainty, demand_base_uncertainty,
                                                 demand_pattern_uncertainty, elevation_uncertainty,
                                                 constants_uncertainty, parameters_uncertainty)

            if "sensor_noise" in uncertanties.keys():
                sensor_noise = SensorNoise(parse_uncertantiy(uncertanties["sensor_noise"]))
            else:
                sensor_noise = None

        # Events
        leakages = []
        if "leakages" in data.keys():
            def parse_leak(leak_desc):
                leak_type = leak_desc["type"]
                del leak_desc["type"]

                if leak_type == "abrupt":
                    return AbruptLeakage(**leak_desc)
                elif leak_type == "incipient":
                    return IncipientLeakage(**leak_desc)
                else:
                    raise ValueError(f"Unknown leakage type '{leak_type}'")

            leakages = [parse_leak(leak) for leak in data["leakages"]]

        sensor_faults = []
        if "sensor_faults" in data.keys():
            def parse_sensor_fault(sensor_fault_desc):
                fault_type = sensor_fault_desc["type"]
                del sensor_fault_desc["type"]

                if fault_type == "constant":
                    return SensorFaultConstant(**sensor_fault_desc)
                elif fault_type == "drift":
                    return SensorFaultDrift(**sensor_fault_desc)
                elif fault_type == "gaussian":
                    return SensorFaultGaussian(**sensor_fault_desc)
                elif fault_type == "percentage":
                    return SensorFaultPercentage(**sensor_fault_desc)
                elif fault_type == "stuckatzero":
                    return SensorFaultStuckZero(**sensor_fault_desc)
                else:
                    raise ValueError(f"Unknown sensor fault '{fault_type}'")

            sensor_faults = [parse_sensor_fault(sensor_fault) \
                             for sensor_fault in data["sensor_faults"]]

        #  Load .inp file to get a list of all nodes and links/pipes
        sensor_config = None
        from .scenario_simulator import WaterDistributionNetworkScenarioSimulator
        with WaterDistributionNetworkScenarioSimulator(f_inp_in) as scenario:
            sensor_config = SensorConfig(scenario.sensor_config.nodes,
                                         scenario.sensor_config.links,
                                         scenario.sensor_config.valves,
                                         scenario.sensor_config.pumps,
                                         scenario.sensor_config.tanks, pressure_sensors,
                                         flow_sensors, demand_sensors, node_quality_sensors,
                                         link_quality_sensors, valve_state_sensors,
                                         pump_state_sensors, tank_level_sensors)

        # Create final scenario configuration
        return ScenarioConfig(f_inp_in, f_msx_in, general_params, sensor_config, [], sensor_noise,
                              model_uncertainty, leakages, sensor_faults)
