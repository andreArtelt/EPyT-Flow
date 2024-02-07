from copy import deepcopy
import numpy
import numpy as np

from ..sensor_config import *
from ..events import SensorFault
from ...uncertainty import SensorNoise
from ...serialization import serializable, Serializable, SCADA_DATA_ID


@serializable(SCADA_DATA_ID)
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
    sensor_readings_time : `numpy.ndarray`
        Time (seconds since simulation start) for each sensor reading row 
        in `sensor_readings_data_raw`.

        This parameter is expected to be a 1d array with the same size as 
        the number of rows in `sensor_readings_data_raw`.
    sensor_faults : `list[`:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault` `]`, optional
        List of sensor faults to be applied to the sensor readings.

        The default is an empty list.
    sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`, optional
        Specification of the sensor noise/uncertainty to be added to the sensor readings.

        The default is None.
    """
    def __init__(self, sensor_config:SensorConfig, pressure_data_raw:numpy.ndarray,
                 flow_data_raw:numpy.ndarray, demand_data_raw:numpy.ndarray,
                 node_quality_data_raw:numpy.ndarray, link_quality_data_raw:numpy.ndarray,
                 pumps_state_data_raw:numpy.ndarray, valves_state_data_raw,
                 sensor_readings_time:numpy.ndarray, sensor_faults:list[SensorFault]=[],
                 sensor_noise:SensorNoise=None, **kwds):
        if not isinstance(sensor_config, SensorConfig):
            raise ValueError("'sensor_config' must be an instance of "+\
                             "'epyt_flow.simulation.SensorConfig' but not of "+\
                                f"'{type(sensor_config)}'")
        if not isinstance(pressure_data_raw, np.ndarray):
            raise ValueError("'pressure_data_raw' must be an instance of 'numpy.ndarray'"+\
                             f" but not of '{type(pressure_data_raw)}'")
        if not isinstance(flow_data_raw, np.ndarray):
            raise ValueError("'flow_data_raw' must be an instance of 'numpy.ndarray' but not of "+\
                             f"'{type(flow_data_raw)}'")
        if not isinstance(demand_data_raw, np.ndarray):
            raise ValueError("'demand_data_raw' must be an instance of 'numpy.ndarray' "+\
                             f"but not of '{type(demand_data_raw)}'")
        if not isinstance(node_quality_data_raw, np.ndarray):
            raise ValueError("'node_quality_data_raw' must be an instance of 'numpy.ndarray'"+\
                             f" but not of '{type(node_quality_data_raw)}'")
        if not isinstance(link_quality_data_raw, np.ndarray):
            raise ValueError("'link_quality_data_raw' must be an instance of 'numpy.ndarray'"+\
                             f" but not of '{type(link_quality_data_raw)}'")
        if not isinstance(pumps_state_data_raw, np.ndarray):
            raise ValueError("'pumps_state_data_raw' must be an instance of 'numpy.ndarray' "+\
                             f"but no of '{type(pumps_state_data_raw)}'")
        if not isinstance(valves_state_data_raw, np.ndarray):
            raise ValueError("'valves_state_data_raw' must be an instance of 'numpy.ndarray' "+\
                             f"but no of '{type(valves_state_data_raw)}'")
        if not isinstance(sensor_readings_time, np.ndarray):
            raise ValueError("'sensor_readings_time' must be an instance of 'numpy.ndarray' "+\
                             f"but not of '{type(sensor_readings_time)}'")
        if sensor_faults is None or not isinstance(sensor_faults, list):
            raise ValueError("'sensor_faults' must be a list of "+\
                             "'epyt_flow.simulation.events.SensorFault' instances but "+\
                                f"'{type(sensor_faults)}'")
        if len(sensor_faults) != 0:
            if any([not isinstance(f, SensorFault) for f in sensor_faults]):
                raise ValueError("'sensor_faults' must be a list of "+\
                                 "'epyt_flow.simulation.event.SensorFault' instances")
        if sensor_noise is not None and not isinstance(sensor_noise, SensorNoise):
            raise ValueError("'sensor_noise' must be an instance of "+\
                             "'epyt_flow.uncertainty.SensorNoise' but not of "+\
                                f"'{type(sensor_noise)}'")
        n_time_steps = sensor_readings_time.shape[0]
        if not all([pressure_data_raw.shape[0] == n_time_steps,
                    flow_data_raw.shape[0] == n_time_steps,
                    demand_data_raw.shape[0] == n_time_steps,
                    node_quality_data_raw.shape[0] == n_time_steps,
                    link_quality_data_raw.shape[0] == n_time_steps]):
            raise ValueError("Shape mismatch detected")
        if len(valves_state_data_raw) != 0:
            if not valves_state_data_raw.shape[0] == n_time_steps:
                raise ValueError("Shape mismatch detected")
        if len(pumps_state_data_raw) != 0:
            if not pumps_state_data_raw.shape[0] == n_time_steps:
                raise ValueError("Shape mismatch detected")


        self.__sensor_config = sensor_config
        self.__sensor_noise = sensor_noise
        self.__sensor_faults = sensor_faults
        self.__pressure_data_raw = pressure_data_raw
        self.__flow_data_raw = flow_data_raw
        self.__demand_data_raw = demand_data_raw
        self.__node_quality_data_raw = node_quality_data_raw
        self.__link_quality_data_raw = link_quality_data_raw
        self.__sensor_readings_time = sensor_readings_time
        self.__pumps_state_data_raw = pumps_state_data_raw
        self.__valves_state_data_raw = valves_state_data_raw

        self.__init()

        super().__init__(**kwds)

    @property
    def sensor_config(self) -> SensorConfig:
        return deepcopy(self.__sensor_config)

    @sensor_config.setter
    def sensor_config(self, sensor_config:SensorConfig) -> None:
        self.change_sensor_config(sensor_config)

    @property
    def sensor_noise(self) -> SensorNoise:
        return deepcopy(self.__sensor_noise)

    @sensor_noise.setter
    def sensor_noise(self, sensor_noise:SensorNoise) -> None:
        self.change_sensor_noise(sensor_noise)

    @property
    def sensor_faults(self) -> list[SensorFault]:
        return deepcopy(self.__sensor_faults)

    @sensor_faults.setter
    def sensor_faults(self, sensor_faults:list[SensorFault]) -> None:
        self.change_sensor_faults(sensor_faults)

    @property
    def pressure_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__pressure_data_raw)

    @property
    def flow_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__flow_data_raw)

    @property
    def demand_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__demand_data_raw)

    @property
    def node_quality_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__node_quality_data_raw)

    @property
    def link_quality_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__link_quality_data_raw)

    @property
    def sensor_readings_time(self) -> numpy.ndarray:
        return deepcopy(self.__sensor_readings_time)

    @property
    def pumps_state_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__pumps_state_data_raw)

    @property
    def valves_state_data_raw(self) -> numpy.ndarray:
        return deepcopy(self.__valves_state_data_raw)

    def __init(self):
        self.__apply_sensor_noise = lambda x: x
        if self.__sensor_noise is not None:
            self.__apply_sensor_noise = self.__sensor_noise.apply

        self.__apply_sensor_faults = []
        for sensor_fault in self.__sensor_faults:
            idx = None
            if sensor_fault.sensor_type == SENSOR_TYPE_NODE_PRESSURE:
                idx = self.__sensor_config.get_index_of_reading(
                    pressure_sensor=sensor_fault.sensor_id)
            elif sensor_fault.sensor_type == SENSOR_TYPE_NODE_QUALITY:
                idx = self.__sensor_config.get_index_of_reading(
                    node_quality_sensor=sensor_fault.sensor_id)
            elif sensor_fault.sensor_type == SENSOR_TYPE_NODE_DEMAND:
                idx = self.__sensor_config.get_index_of_reading(
                    demand_sensor=sensor_fault.sensor_id)
            elif sensor_fault.sensor_type == SENSOR_TYPE_LINK_FLOW:
                idx = self.__sensor_config.get_index_of_reading(
                    flow_sensor=sensor_fault.sensor_id)
            elif sensor_fault.sensor_type == SENSOR_TYPE_LINK_QUALITY:
                idx = self.__sensor_config.get_index_of_reading(
                    link_quality_sensor=sensor_fault.sensor_id)

            self.__apply_sensor_faults.append((idx, sensor_fault.apply))

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"sensor_config": self.__sensor_config,
                                           "sensor_noise": self.__sensor_noise,
                                           "sensor_faults": self.__sensor_faults,
                                           "pressure_data_raw": self.__pressure_data_raw,
                                           "flow_data_raw": self.__flow_data_raw,
                                           "demand_data_raw": self.__demand_data_raw,
                                           "node_quality_data_raw": self.__node_quality_data_raw,
                                           "link_quality_data_raw": self.__link_quality_data_raw,
                                           "sensor_readings_time": self.__sensor_readings_time,
                                           "pumps_state_data_raw": self.__pumps_state_data_raw,
                                           "valves_state_data_raw": self.__valves_state_data_raw}

    def __eq__(self, other) -> bool:
        return self.__sensor_config == other.sensor_config \
            and self.__sensor_noise == other.sensor_noise \
            and self.__sensor_faults == other.sensor_faults \
            and np.all(self.__pressure_data_raw == other.pressure_data_raw) \
            and np.all(self.__flow_data_raw == other.flow_data_raw) \
            and np.all(self.__demand_data_raw == self.demand_data_raw) \
            and np.all(self.__node_quality_data_raw == other.node_quality_data_raw) \
            and np.all(self.__link_quality_data_raw == other.link_quality_data_raw) \
            and np.all(self.__sensor_readings_time == other.sensor_readings_time) \
            and np.all(self.__pumps_state_data_raw == other.pumps_state_data_raw) \
            and np.all(self.__valves_state_data_raw == other.valves_state_data_raw)

    def __str__(self) -> str:
        return f"sensor_config: {self.__sensor_config} sensor_noise: {self.__sensor_noise} "+\
            f"sensor_faults: {self.__sensor_faults} "+\
            f"pressure_data_raw: {self.__pressure_data_raw} "+\
            f"flow_data_raw: {self.__flow_data_raw} demand_data_raw: {self.__demand_data_raw} "+\
            f"node_quality_data_raw: {self.__node_quality_data_raw} "+\
            f"link_quality_data_raw: {self.__link_quality_data_raw} "+\
            f"sensor_readings_time: {self.__sensor_readings_time} "+\
            f"pumps_state_data_raw: {self.__pumps_state_data_raw} "+\
            f"valves_state_data_raw: {self.__valves_state_data_raw}"

    def change_sensor_config(self, sensor_config:SensorConfig) -> None:
        """
        Changes the sensor configuration.

        Parameters
        ----------
        sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
            New sensor configuration.
        """
        if not isinstance(sensor_config, SensorConfig):
            raise ValueError("'sensor_config' must be an instance of "+\
                             "'epyt_flow.simulation.SensorConfig' but not of "+\
                                f"'{type(sensor_config)}'")

        self.__sensor_config = sensor_config
        self.__init()

    def change_sensor_noise(self, sensor_noise:SensorNoise) -> None:
        """
        Changes the sensor noise/uncertainty.

        Parameters
        ----------
        sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`
            New sensor noise/uncertainty specification.
        """
        if not isinstance(sensor_noise, SensorNoise):
            raise ValueError("'sensor_noise' must be an instance of "+\
                             "'epyt_flow.uncertainty.SensorNoise' but not of "+\
                                f"'{type(sensor_noise)}'")

        self.__sensor_noise = sensor_noise
        self.__init()

    def change_sensor_faults(self, sensor_faults:list[SensorFault]) -> None:
        """
        Changes the sensor faults -- overrides all previous sensor faults!

        sensor_faults : `list[`:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault` `]`
            List of new sensor faults.
        """
        if len(sensor_faults) != 0:
            if any([not isinstance(f, SensorFault) for f in sensor_faults]):
                raise ValueError("'sensor_faults' must be a list of "+\
                                 "'epyt_flow.simulation.events.SensorFault' instances")

        self.__sensor_faults = sensor_faults
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
            raise ValueError(f"'other' must be an instance of 'ScadaData' but not of {type(other)}")
        if self.__sensor_config != other.sensor_config:
            raise ValueError("Sensor configurations must be the same!")

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

    def get_data(self) -> numpy.ndarray:
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
                                                                self.__link_quality_data_raw)

        # Apply sensor uncertainties
        sensor_readings = self.__apply_sensor_noise(sensor_readings)

        # Append actuator states
        sensor_readings = np.concatenate(
            (sensor_readings, self.__pumps_state_data_raw, self.__valves_state_data_raw), axis=1)

        # Apply sensor faults
        for idx, f in self.__apply_sensor_faults:
            sensor_readings[:,idx] = f(sensor_readings[:,idx], self.__sensor_readings_time)

        return sensor_readings
