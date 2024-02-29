"""
Module provides a class for storing and processing SCADA data.
"""
import warnings
from copy import deepcopy
import numpy as np

from ..sensor_config import SensorConfig, SENSOR_TYPE_LINK_FLOW, SENSOR_TYPE_LINK_QUALITY, \
    SENSOR_TYPE_NODE_DEMAND, SENSOR_TYPE_NODE_PRESSURE, SENSOR_TYPE_NODE_QUALITY, \
    SENSOR_TYPE_PUMP_STATE, SENSOR_TYPE_TANK_LEVEL, SENSOR_TYPE_VALVE_STATE
from ..events import SensorFault, SensorReadingAttack, SensorReadingEvent
from ...uncertainty import SensorNoise
from ...serialization import serializable, Serializable, SCADA_DATA_ID


@serializable(SCADA_DATA_ID, ".epytflow_scada_data")
class ScadaData(Serializable):
    """
    Class for storing and processing SCADA data.

    Parameters
    ----------
    sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
        Specifications of all sensors.
    pressure_data_raw : `numpy.ndarray`
        Raw pressure values of all nodes.
    flow_data_raw : `numpy.ndarray`
        Raw flow values of all links/pipes.
    demand_data_raw : `numpy.ndarray`
        Raw demand values of all nodes.
    node_quality_data_raw : `numpy.ndarray`
        Raw quality values of all nodes.
    link_quality_data_raw : `numpy.ndarray`
        Raw quality values of all links/pipes.
    pumps_state_data_raw : `numpy.ndarray`
        States of all pumps.
    valves_state_data_raw : `numpy.ndarray`
        States of all valves.
    tanks_level_data_raw : `numpy.ndarray`
        Water levels in all tanks.
    sensor_readings_time : `numpy.ndarray`
        Time (seconds since simulation start) for each sensor reading row
        in `sensor_readings_data_raw`.

        This parameter is expected to be a 1d array with the same size as
        the number of rows in `sensor_readings_data_raw`.
    sensor_faults : `list[`:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault` `]`, optional
        List of sensor faults to be applied to the sensor readings.

        The default is an empty list.
    sensor_reading_attacks : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack` `]`, optional
        List of sensor reading attacks to be applied to the sensor readings.

        The default is an empty list.
    sensor_reading_events : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent` `]`, optional
        List of additional sensor reading events that are to be applied to the sensor readings.

        The default is an empty list.
    sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`, optional
        Specification of the sensor noise/uncertainty to be added to the sensor readings.

        The default is None.
    """
    def __init__(self, sensor_config: SensorConfig, pressure_data_raw: np.ndarray,
                 flow_data_raw: np.ndarray, demand_data_raw: np.ndarray,
                 node_quality_data_raw: np.ndarray, link_quality_data_raw: np.ndarray,
                 pumps_state_data_raw: np.ndarray, valves_state_data_raw: np.ndarray,
                 tanks_level_data_raw: np.ndarray, sensor_readings_time: np.ndarray,
                 sensor_faults: list[SensorFault] = [],
                 sensor_reading_attacks: list[SensorReadingAttack] = [],
                 sensor_reading_events: list[SensorReadingEvent] = [],
                 sensor_noise: SensorNoise = None, **kwds):
        if not isinstance(sensor_config, SensorConfig):
            raise TypeError("'sensor_config' must be an instance of " +
                            "'epyt_flow.simulation.SensorConfig' but not of " +
                            f"'{type(sensor_config)}'")
        if not isinstance(pressure_data_raw, np.ndarray):
            raise TypeError("'pressure_data_raw' must be an instance of 'numpy.ndarray'" +
                            f" but not of '{type(pressure_data_raw)}'")
        if not isinstance(flow_data_raw, np.ndarray):
            raise TypeError("'flow_data_raw' must be an instance of 'numpy.ndarray' but not of " +
                            f"'{type(flow_data_raw)}'")
        if not isinstance(demand_data_raw, np.ndarray):
            raise TypeError("'demand_data_raw' must be an instance of 'numpy.ndarray' " +
                            f"but not of '{type(demand_data_raw)}'")
        if not isinstance(node_quality_data_raw, np.ndarray):
            raise TypeError("'node_quality_data_raw' must be an instance of 'numpy.ndarray'" +
                            f" but not of '{type(node_quality_data_raw)}'")
        if not isinstance(link_quality_data_raw, np.ndarray):
            raise TypeError("'link_quality_data_raw' must be an instance of 'numpy.ndarray'" +
                            f" but not of '{type(link_quality_data_raw)}'")
        if not isinstance(pumps_state_data_raw, np.ndarray):
            raise TypeError("'pumps_state_data_raw' must be an instance of 'numpy.ndarray' " +
                            f"but no of '{type(pumps_state_data_raw)}'")
        if not isinstance(valves_state_data_raw, np.ndarray):
            raise TypeError("'valves_state_data_raw' must be an instance of 'numpy.ndarray' " +
                            f"but no of '{type(valves_state_data_raw)}'")
        if not isinstance(tanks_level_data_raw, np.ndarray):
            raise TypeError("'tanks_level_data_raw' must be an instance of 'numpy.ndarray'" +
                            f" but not of '{type(tanks_level_data_raw)}'")
        if not isinstance(sensor_readings_time, np.ndarray):
            raise TypeError("'sensor_readings_time' must be an instance of 'numpy.ndarray' " +
                            f"but not of '{type(sensor_readings_time)}'")
        if sensor_faults is None or not isinstance(sensor_faults, list):
            raise TypeError("'sensor_faults' must be a list of " +
                            "'epyt_flow.simulation.events.SensorFault' instances but " +
                            f"'{type(sensor_faults)}'")
        if len(sensor_faults) != 0:
            if any(not isinstance(f, SensorFault) for f in sensor_faults):
                raise TypeError("'sensor_faults' must be a list of " +
                                "'epyt_flow.simulation.event.SensorFault' instances")
        if len(sensor_reading_attacks) != 0:
            if any(not isinstance(f, SensorReadingAttack) for f in sensor_reading_attacks):
                raise TypeError("'sensor_reading_attacks' must be a list of " +
                                "'epyt_flow.simulation.event.SensorReadingAttack' instances")
        if len(sensor_reading_events) != 0:
            if any(not isinstance(f, SensorReadingEvent) for f in sensor_reading_events):
                raise TypeError("'sensor_reading_events' must be a list of " +
                                "'epyt_flow.simulation.event.SensorReadingEvent' instances")
        if sensor_noise is not None and not isinstance(sensor_noise, SensorNoise):
            raise TypeError("'sensor_noise' must be an instance of " +
                            "'epyt_flow.uncertainty.SensorNoise' but not of " +
                            f"'{type(sensor_noise)}'")
        n_time_steps = sensor_readings_time.shape[0]
        if not all([pressure_data_raw.shape[0] == n_time_steps,
                    flow_data_raw.shape[0] == n_time_steps,
                    demand_data_raw.shape[0] == n_time_steps,
                    node_quality_data_raw.shape[0] == n_time_steps,
                    link_quality_data_raw.shape[0] == n_time_steps,
                    valves_state_data_raw.shape[0] == n_time_steps,
                    pumps_state_data_raw.shape[0] == n_time_steps,
                    tanks_level_data_raw.shape[0] == n_time_steps]):
            raise ValueError("Shape mismatch detected")
        if len(valves_state_data_raw) != 0:
            if not valves_state_data_raw.shape[0] == n_time_steps:
                raise ValueError("Shape mismatch detected")
        if len(pumps_state_data_raw) != 0:
            if not pumps_state_data_raw.shape[0] == n_time_steps:
                raise ValueError("Shape mismatch detected")
        if len(tanks_level_data_raw) != 0:
            if not tanks_level_data_raw.shape[0] == n_time_steps:
                raise ValueError("Shape mismatch detected")

        self.__sensor_config = sensor_config
        self.__sensor_noise = sensor_noise
        self.__sensor_reading_events = sensor_faults + sensor_reading_attacks +\
            sensor_reading_events
        self.__pressure_data_raw = pressure_data_raw
        self.__flow_data_raw = flow_data_raw
        self.__demand_data_raw = demand_data_raw
        self.__node_quality_data_raw = node_quality_data_raw
        self.__link_quality_data_raw = link_quality_data_raw
        self.__sensor_readings_time = sensor_readings_time
        self.__pumps_state_data_raw = pumps_state_data_raw
        self.__valves_state_data_raw = valves_state_data_raw
        self.__tanks_level_data_raw = tanks_level_data_raw
        self.__sensor_readings = None

        self.__init()

        super().__init__(**kwds)

    @property
    def sensor_config(self) -> SensorConfig:
        """
        Gets the sensor configuration.

        Returns
        -------
        :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
            Sensor configuration.
        """
        return deepcopy(self.__sensor_config)

    @sensor_config.setter
    def sensor_config(self, sensor_config: SensorConfig) -> None:
        self.change_sensor_config(sensor_config)

    @property
    def sensor_noise(self) -> SensorNoise:
        """
        Gets the sensor noise.

        Returns
        -------
        :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`
            Sensor noise.
        """
        return deepcopy(self.__sensor_noise)

    @sensor_noise.setter
    def sensor_noise(self, sensor_noise: SensorNoise) -> None:
        self.change_sensor_noise(sensor_noise)

    @property
    def sensor_faults(self) -> list[SensorFault]:
        """
        Gets all sensor faults.

        Returns
        -------
        `list[` :class:`~epyt_flow.simulation.events.sensor_faults.SensorFault` `]`
            All sensor faults.
        """
        return deepcopy(filter(lambda e: isinstance(e, SensorFault), self.__sensor_reading_events))

    @sensor_faults.setter
    def sensor_faults(self, sensor_faults: list[SensorFault]) -> None:
        self.change_sensor_faults(sensor_faults)

    @property
    def sensor_reading_attacks(self) -> list[SensorReadingAttack]:
        """
        Gets all sensor reading attacks.

        Returns
        -------
        `list[` :class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack` `]`
            All sensor reading attacks.
        """
        return deepcopy(filter(lambda e: isinstance(e, SensorReadingAttack),
                               self.__sensor_reading_events))

    @sensor_reading_attacks.setter
    def sensor_reading_attacks(self, sensor_reading_attacks: list[SensorReadingAttack]) -> None:
        self.change_sensor_reading_attacks(sensor_reading_attacks)

    @property
    def sensor_reading_events(self) -> list[SensorReadingEvent]:
        """
        Gets all sensor reading events.

        Returns
        -------
        `list[` :class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent` `]`
            All sensor faults.
        """
        return deepcopy(self.__sensor_reading_events)

    @sensor_reading_events.setter
    def sensor_reading_events(self, sensor_reading_events: list[SensorReadingEvent]) -> None:
        self.change_sensor_reading_events(sensor_reading_events)

    @property
    def pressure_data_raw(self) -> np.ndarray:
        """
        Gets the raw pressure readings.

        Returns
        -------
        `numpy.ndarray`
            Raw pressure readings.
        """
        return deepcopy(self.__pressure_data_raw)

    @property
    def flow_data_raw(self) -> np.ndarray:
        """
        Gets the raw flow readings.

        Returns
        -------
        `numpy.ndarray`
            Raw flow readings.
        """
        return deepcopy(self.__flow_data_raw)

    @property
    def demand_data_raw(self) -> np.ndarray:
        """
        Gets the raw demand readings.

        Returns
        -------
        `numpy.ndarray`
            Raw demand readings.
        """
        return deepcopy(self.__demand_data_raw)

    @property
    def node_quality_data_raw(self) -> np.ndarray:
        """
        Gets the raw node quality readings.

        Returns
        -------
        `numpy.ndarray`
            Raw node quality readings.
        """
        return deepcopy(self.__node_quality_data_raw)

    @property
    def link_quality_data_raw(self) -> np.ndarray:
        """
        Gets the raw link quality readings.

        Returns
        -------
        `numpy.ndarray`
            Raw link quality readings.
        """
        return deepcopy(self.__link_quality_data_raw)

    @property
    def sensor_readings_time(self) -> np.ndarray:
        """
        Gets the sensor readings time stamps.

        Returns
        -------
        `numpy.ndarray`
            Sensor readings time stamps.
        """
        return deepcopy(self.__sensor_readings_time)

    @property
    def pumps_state_data_raw(self) -> np.ndarray:
        """
        Gets the raw pump state readings.

        Returns
        -------
        `numpy.ndarray`
            Raw pump state readings.
        """
        return deepcopy(self.__pumps_state_data_raw)

    @property
    def valves_state_data_raw(self) -> np.ndarray:
        """
        Gets the raw valve state readings.

        Returns
        -------
        `numpy.ndarray`
            Raw valve state readings.
        """
        return deepcopy(self.__valves_state_data_raw)

    @property
    def tanks_level_data_raw(self) -> np.ndarray:
        """
        Gets the raw tank level readings.

        Returns
        -------
        `numpy.ndarray`
            Raw tank level readings.
        """
        return deepcopy(self.__tanks_level_data_raw)

    def __init(self):
        self.__apply_sensor_noise = lambda x: x
        if self.__sensor_noise is not None:
            self.__apply_sensor_noise = self.__sensor_noise.apply

        self.__apply_sensor_reading_events = []
        for sensor_event in self.__sensor_reading_events:
            idx = None
            if sensor_event.sensor_type == SENSOR_TYPE_NODE_PRESSURE:
                idx = self.__sensor_config.get_index_of_reading(
                    pressure_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_NODE_QUALITY:
                idx = self.__sensor_config.get_index_of_reading(
                    node_quality_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_NODE_DEMAND:
                idx = self.__sensor_config.get_index_of_reading(
                    demand_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_LINK_FLOW:
                idx = self.__sensor_config.get_index_of_reading(
                    flow_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_LINK_QUALITY:
                idx = self.__sensor_config.get_index_of_reading(
                    link_quality_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_VALVE_STATE:
                idx = self.__sensor_config.get_index_of_reading(
                    valve_state_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_PUMP_STATE:
                idx = self.__sensor_config.get_index_of_reading(
                    pump_state_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_TANK_LEVEL:
                idx = self.__sensor_config.get_index_of_reading(
                    tank_level_sensor=sensor_event.sensor_id)

            self.__apply_sensor_reading_events.append((idx, sensor_event.apply))

        self.__sensor_readings = None

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"sensor_config": self.__sensor_config,
                                           "sensor_noise": self.__sensor_noise,
                                           "sensor_reading_events": self.__sensor_reading_events,
                                           "pressure_data_raw": self.__pressure_data_raw,
                                           "flow_data_raw": self.__flow_data_raw,
                                           "demand_data_raw": self.__demand_data_raw,
                                           "node_quality_data_raw": self.__node_quality_data_raw,
                                           "link_quality_data_raw": self.__link_quality_data_raw,
                                           "sensor_readings_time": self.__sensor_readings_time,
                                           "pumps_state_data_raw": self.__pumps_state_data_raw,
                                           "valves_state_data_raw": self.__valves_state_data_raw,
                                           "tanks_level_data_raw": self.__tanks_level_data_raw}

    def __eq__(self, other) -> bool:
        try:
            return self.__sensor_config == other.sensor_config \
                and self.__sensor_noise == other.sensor_noise \
                and all(a == b for a, b in
                        zip(self.__sensor_reading_events, other.sensor_reading_events)) \
                and np.all(self.__pressure_data_raw == other.pressure_data_raw) \
                and np.all(self.__flow_data_raw == other.flow_data_raw) \
                and np.all(self.__demand_data_raw == self.demand_data_raw) \
                and np.all(self.__node_quality_data_raw == other.node_quality_data_raw) \
                and np.all(self.__link_quality_data_raw == other.link_quality_data_raw) \
                and np.all(self.__sensor_readings_time == other.sensor_readings_time) \
                and np.all(self.__pumps_state_data_raw == other.pumps_state_data_raw) \
                and np.all(self.__valves_state_data_raw == other.valves_state_data_raw) \
                and np.all(self.__tanks_level_data_raw == other.tanks_level_data_raw)
        except Exception as ex:
            warnings.warn(ex.__str__())
            return False

    def __str__(self) -> str:
        return f"sensor_config: {self.__sensor_config} sensor_noise: {self.__sensor_noise} " +\
            f"sensor_reading_events: {self.__sensor_reading_events} " +\
            f"pressure_data_raw: {self.__pressure_data_raw} " +\
            f"flow_data_raw: {self.__flow_data_raw} demand_data_raw: {self.__demand_data_raw} " +\
            f"node_quality_data_raw: {self.__node_quality_data_raw} " +\
            f"link_quality_data_raw: {self.__link_quality_data_raw} " +\
            f"sensor_readings_time: {self.__sensor_readings_time} " +\
            f"pumps_state_data_raw: {self.__pumps_state_data_raw} " +\
            f"valves_state_data_raw: {self.__valves_state_data_raw}" +\
            f"tanks_level_data_raw: {self.__tanks_level_data_raw}"

    def change_sensor_config(self, sensor_config: SensorConfig) -> None:
        """
        Changes the sensor configuration.

        Parameters
        ----------
        sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
            New sensor configuration.
        """
        if not isinstance(sensor_config, SensorConfig):
            raise TypeError("'sensor_config' must be an instance of " +
                            "'epyt_flow.simulation.SensorConfig' but not of " +
                            f"'{type(sensor_config)}'")

        self.__sensor_config = sensor_config
        self.__init()

    def change_sensor_noise(self, sensor_noise: SensorNoise) -> None:
        """
        Changes the sensor noise/uncertainty.

        Parameters
        ----------
        sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`
            New sensor noise/uncertainty specification.
        """
        if not isinstance(sensor_noise, SensorNoise):
            raise TypeError("'sensor_noise' must be an instance of " +
                            "'epyt_flow.uncertainty.SensorNoise' but not of " +
                            f"'{type(sensor_noise)}'")

        self.__sensor_noise = sensor_noise
        self.__init()

    def change_sensor_faults(self, sensor_faults: list[SensorFault]) -> None:
        """
        Changes the sensor faults -- overrides all previous sensor faults!

        sensor_faults : `list[`:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault` `]`
            List of new sensor faults.
        """
        if len(sensor_faults) != 0:
            if any(not isinstance(e, SensorFault) for e in sensor_faults):
                raise TypeError("'sensor_faults' must be a list of " +
                                "'epyt_flow.simulation.events.SensorFault' instances")

        self.__sensor_reading_events = list(filter(lambda e: not isinstance(e, SensorFault),
                                                   self.__sensor_reading_events))
        self.__sensor_reading_events += sensor_faults
        self.__init()

    def change_sensor_reading_attacks(self,
                                      sensor_reading_attacks: list[SensorReadingAttack]) -> None:
        """
        Changes the sensor reading attacks -- overrides all previous sensor reading attacks!

        sensor_reading_attacks : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack` `]`
            List of new sensor reading attacks.
        """
        if len(sensor_reading_attacks) != 0:
            if any(not isinstance(e, SensorReadingAttack) for e in sensor_reading_attacks):
                raise TypeError("'sensor_reading_attacks' must be a list of " +
                                "'epyt_flow.simulation.events.SensorReadingAttack' instances")

        self.__sensor_reading_events = list(filter(lambda e: not isinstance(e, SensorReadingAttack),
                                                   self.__sensor_reading_events))
        self.__sensor_reading_events += sensor_reading_attacks
        self.__init()

    def change_sensor_reading_events(self, sensor_reading_events: list[SensorReadingEvent]) -> None:
        """
        Changes the sensor reading events -- overrides all previous sensor reading events
        (incl. sensor faults)!

        sensor_reading_events : `list[`:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent` `]`
            List of new sensor reading events.
        """
        if len(sensor_reading_events) != 0:
            if any(not isinstance(e, SensorReadingEvent) for e in sensor_reading_events):
                raise TypeError("'sensor_reading_events' must be a list of " +
                                "'epyt_flow.simulation.events.SensorReadingEvent' instances")

        self.__sensor_reading_events = sensor_reading_events
        self.__init()

    def join(self, other) -> None:
        """
        Joins two :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instances -- i.e.
         add scada data from another given
         :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instance to this one.

        Note that the two :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instances
         must be the same in all other attributs (e.g. sensor configuration, etc.).

        Parameters
        ----------
        other : :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData`
            Other scada data to be added to this data.
        """
        if not isinstance(other, ScadaData):
            raise TypeError(f"'other' must be an instance of 'ScadaData' but not of {type(other)}")
        if self.__sensor_config != other.sensor_config:
            raise ValueError("Sensor configurations must be the same!")
        # TODO: Check for different sensor reading events!

        self.__pressure_data_raw = np.concatenate(
            (self.__pressure_data_raw, other.pressure_data_raw), axis=0)
        self.__flow_data_raw = np.concatenate(
            (self.__flow_data_raw, other.flow_data_raw), axis=0)
        self.__demand_data_raw = np.concatenate(
            (self.__demand_data_raw, other.demand_data_raw), axis=0)
        self.__node_quality_data_raw = np.concatenate(
            (self.__node_quality_data_raw, other.node_quality_data_raw), axis=0)
        self.__link_quality_data_raw = np.concatenate(
            (self.__link_quality_data_raw, other.link_quality_data_raw), axis=0)
        self.__sensor_readings_time = np.concatenate(
            (self.__sensor_readings_time, other.sensor_readings_time), axis=0)
        self.__pumps_state_data_raw = np.concatenate(
            (self.__pumps_state_data_raw, other.pumps_state_data_raw), axis=0)
        self.__valves_state_data_raw = np.concatenate(
            (self.__valves_state_data_raw, other.valves_state_data_raw), axis=0)
        self.__tanks_level_data_raw = np.concatenate(
            (self.__tanks_level_data_raw, other.tanks_level_data_raw), axis=0)

    def get_data(self) -> np.ndarray:
        """
        Computes the final sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Returns
        -------
        `numpy.ndarray`
            Final sensor readings.
        """
        # Comute clean sensor readings
        sensor_readings = self.__sensor_config.compute_readings(self.__pressure_data_raw,
                                                                self.__flow_data_raw,
                                                                self.__demand_data_raw,
                                                                self.__node_quality_data_raw,
                                                                self.__link_quality_data_raw,
                                                                self.__pumps_state_data_raw,
                                                                self.__valves_state_data_raw,
                                                                self.__tanks_level_data_raw)

        # Apply sensor uncertainties
        sensor_readings = self.__apply_sensor_noise(sensor_readings)

        # Apply sensor faults
        for idx, f in self.__apply_sensor_reading_events:
            sensor_readings[:, idx] = f(sensor_readings[:, idx], self.__sensor_readings_time)

        self.__sensor_readings = deepcopy(sensor_readings)

        return sensor_readings

    def get_data_pressures(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final pressure sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing pressure sensor locations for which the sensor readings are requested.
             If None, the readings from all pressure sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Pressure sensor readings.
        """
        if self.sensor_config.pressure_sensors == []:
            raise ValueError("No pressure sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.pressure_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "pressure sensor configuration")
        else:
            sensor_locations = self.sensor_config.pressure_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(pressure_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_flows(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final flow sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing flow sensor locations for which the sensor readings are requested.
             If None, the readings from all flow sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Flow sensor readings.
        """
        if self.sensor_config.flow_sensors == []:
            raise ValueError("No flow sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.flow_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "flow sensor configuration")
        else:
            sensor_locations = self.sensor_config.flow_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(flow_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_demands(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final demand sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing demand sensor locations for which the sensor readings are requested.
             If None, the readings from all demand sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Demand sensor readings.
        """
        if self.sensor_config.demand_sensors == []:
            raise ValueError("No demand sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.demand_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "demand sensor configuration")
        else:
            sensor_locations = self.sensor_config.demand_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(demand_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_nodes_quality(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final node quality sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing node quality sensor locations for which the sensor readings are requested.
             If None, the readings from all node quality sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Node quality sensor readings.
        """
        if self.sensor_config.quality_node_sensors == []:
            raise ValueError("No node quality sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.quality_node_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "node quality sensor configuration")
        else:
            sensor_locations = self.sensor_config.quality_node_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(node_quality_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_links_quality(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final link quality sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing link quality sensor locations for which the sensor readings are requested.
             If None, the readings from all link quality sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Link quality sensor readings.
        """
        if self.sensor_config.quality_link_sensors == []:
            raise ValueError("No link quality sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.quality_link_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "link quality sensor configuration")
        else:
            sensor_locations = self.sensor_config.quality_link_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(link_quality_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_pumps_state(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final pump state sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing pump state sensor locations for which the sensor readings are requested.
             If None, the readings from all pump state sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Pump state sensor readings.
        """
        if self.sensor_config.pump_state_sensors == []:
            raise ValueError("No pump state sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.pump_state_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "pump state sensor configuration")
        else:
            sensor_locations = self.sensor_config.pump_state_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(pump_state_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_valves_state(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final valve state sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing valve state sensor locations for which the sensor readings are requested.
             If None, the readings from all valve state sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Valve state sensor readings.
        """
        if self.sensor_config.valve_state_sensors == []:
            raise ValueError("No valve state sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.valve_state_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "valve state sensor configuration")
        else:
            sensor_locations = self.sensor_config.valve_state_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(valve_state_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_tanks_water_level(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final water tanks level sensor readings -- note that those might be subject to
         given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing flow sensor locations for which the sensor readings are requested.
             If None, the readings from all water tanks level sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Water tanks level sensor readings.
        """
        if self.sensor_config.tank_level_sensors == []:
            raise ValueError("No tank level sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.sensor_config.flow_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "water tanks level sensor configuration")
        else:
            sensor_locations = self.sensor_config.tank_level_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.sensor_config.get_index_of_reading(tank_level_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]
