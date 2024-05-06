"""
Module provides a class for storing and processing SCADA data.
"""
import warnings
from typing import Callable
from copy import deepcopy
import numpy as np

from ..sensor_config import SensorConfig, SENSOR_TYPE_LINK_FLOW, SENSOR_TYPE_LINK_QUALITY, \
    SENSOR_TYPE_NODE_DEMAND, SENSOR_TYPE_NODE_PRESSURE, SENSOR_TYPE_NODE_QUALITY, \
    SENSOR_TYPE_PUMP_STATE, SENSOR_TYPE_TANK_VOLUME, SENSOR_TYPE_VALVE_STATE, \
    SENSOR_TYPE_NODE_BULK_SPECIES, SENSOR_TYPE_LINK_BULK_SPECIES, SENSOR_TYPE_SURFACE_SPECIES
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
    sensor_readings_time : `numpy.ndarray`
        Time (seconds since simulation start) for each sensor reading row
        in `sensor_readings_data_raw`.

        This parameter is expected to be a 1d array with the same size as
        the number of rows in `sensor_readings_data_raw`.
    pressure_data_raw : `numpy.ndarray`, optional
        Raw pressure values of all nodes as a two-dimensional array --
        first dimension encodes time, second dimension pressure at nodes.

        The default is None,
    flow_data_raw : `numpy.ndarray`, optional
        Raw flow values of all links/pipes --
        first dimension encodes time, second dimension pressure at links/pipes.

        The default is None.
    demand_data_raw : `numpy.ndarray`, optional
        Raw demand values of all nodes --
        first dimension encodes time, second dimension demand at nodes.

        The default is None.
    node_quality_data_raw : `numpy.ndarray`, optional
        Raw quality values of all nodes --
        first dimension encodes time, second dimension quality at nodes.

        The default is None.
    link_quality_data_raw : `numpy.ndarray`, optional
        Raw quality values of all links/pipes --
        first dimension encodes time, second dimension quality at links/pipes.

        The default is None.
    pumps_state_data_raw : `numpy.ndarray`, optional
        States of all pumps --
        first dimension encodes time, second dimension states of pumps.

        The default is None.
    valves_state_data_raw : `numpy.ndarray`, optional
        States of all valves --
        first dimension encodes time, second dimension states of valves.

        The default is None.
    tanks_volume_data_raw : `numpy.ndarray`, optional
        Water volumes in all tanks --
        first dimension encodes time, second dimension water volume in tanks.

        The default is None.
    surface_species_concentration_raw : `numpy.ndarray`, optional
        Raw concentrations of surface species as a tree dimensional array --
        first dimension encodes time, second dimension denotes the different surface species,
        third dimension denotes species concentrations at links/pipes.

        The default is None.
    bulk_species_node_concentration_raw : `numpy.ndarray`, optional
        Raw concentrations of bulk species at nodes as a tree dimensional array --
        first dimension encodes time, second dimension denotes the different bulk species,
        third dimension denotes species concentrations at nodes.

        The default is None.
    bulk_species_link_concentration_raw : `numpy.ndarray`, optional
        Raw concentrations of bulk species at links as a tree dimensional array --
        first dimension encodes time, second dimension denotes the different bulk species,
        third dimension denotes species concentrations at nodes.

        The default is None.
    pump_energy_usage_data : `numpy.ndarray`, optional
        Energy usage data of each pump.

        The default is None.
    pump_efficiency_data : `numpy.ndarray`, optional
        Pump efficiency data of each pump.

        The default is None.
    sensor_faults : list[:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault`], optional
        List of sensor faults to be applied to the sensor readings.

        The default is an empty list.
    sensor_reading_attacks : list[:class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack`], optional
        List of sensor reading attacks to be applied to the sensor readings.

        The default is an empty list.
    sensor_reading_events : list[`:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent`], optional
        List of additional sensor reading events that are to be applied to the sensor readings.

        The default is an empty list.
    sensor_noise : :class:`~epyt_flow.uncertainty.sensor_noise.SensorNoise`, optional
        Specification of the sensor noise/uncertainty to be added to the sensor readings.

        The default is None.
    frozen_sensor_config : `bool`, optional
        If True, the sensor config can not be changed and only the required sensor nodes/links
        will be stored -- this usually leads to a significant reduction in memory consumption.

        The default is False.
    """

    def __init__(self, sensor_config: SensorConfig, sensor_readings_time: np.ndarray,
                 pressure_data_raw: np.ndarray = None, flow_data_raw: np.ndarray = None,
                 demand_data_raw: np.ndarray = None, node_quality_data_raw: np.ndarray = None,
                 link_quality_data_raw: np.ndarray = None, pumps_state_data_raw: np.ndarray = None,
                 valves_state_data_raw: np.ndarray = None, tanks_volume_data_raw: np.ndarray = None,
                 surface_species_concentration_raw: np.ndarray = None,
                 bulk_species_node_concentration_raw: np.ndarray = None,
                 bulk_species_link_concentration_raw: np.ndarray = None,
                 pump_energy_usage_data: np.ndarray = None,
                 pump_efficiency_data: np.ndarray = None,
                 sensor_faults: list[SensorFault] = [],
                 sensor_reading_attacks: list[SensorReadingAttack] = [],
                 sensor_reading_events: list[SensorReadingEvent] = [],
                 sensor_noise: SensorNoise = None, frozen_sensor_config: bool = False, **kwds):
        if not isinstance(sensor_config, SensorConfig):
            raise TypeError("'sensor_config' must be an instance of " +
                            "'epyt_flow.simulation.SensorConfig' but not of " +
                            f"'{type(sensor_config)}'")
        if not isinstance(sensor_readings_time, np.ndarray):
            raise TypeError("'sensor_readings_time' must be an instance of 'numpy.ndarray' " +
                            f"but not of '{type(sensor_readings_time)}'")
        if pressure_data_raw is not None:
            if not isinstance(pressure_data_raw, np.ndarray):
                raise TypeError("'pressure_data_raw' must be an instance of 'numpy.ndarray'" +
                                f" but not of '{type(pressure_data_raw)}'")
        if flow_data_raw is not None:
            if not isinstance(flow_data_raw, np.ndarray):
                raise TypeError("'flow_data_raw' must be an instance of 'numpy.ndarray' " +
                                f"but not of '{type(flow_data_raw)}'")
        if demand_data_raw is not None:
            if not isinstance(demand_data_raw, np.ndarray):
                raise TypeError("'demand_data_raw' must be an instance of 'numpy.ndarray' " +
                                f"but not of '{type(demand_data_raw)}'")
        if node_quality_data_raw is not None:
            if not isinstance(node_quality_data_raw, np.ndarray):
                raise TypeError("'node_quality_data_raw' must be an instance of 'numpy.ndarray'" +
                                f" but not of '{type(node_quality_data_raw)}'")
        if link_quality_data_raw is not None:
            if not isinstance(link_quality_data_raw, np.ndarray):
                raise TypeError("'link_quality_data_raw' must be an instance of 'numpy.ndarray'" +
                                f" but not of '{type(link_quality_data_raw)}'")
        if pumps_state_data_raw is not None:
            if not isinstance(pumps_state_data_raw, np.ndarray):
                raise TypeError("'pumps_state_data_raw' must be an instance of 'numpy.ndarray' " +
                                f"but no of '{type(pumps_state_data_raw)}'")
        if valves_state_data_raw is not None:
            if not isinstance(valves_state_data_raw, np.ndarray):
                raise TypeError("'valves_state_data_raw' must be an instance of 'numpy.ndarray' " +
                                f"but no of '{type(valves_state_data_raw)}'")
        if tanks_volume_data_raw is not None:
            if not isinstance(tanks_volume_data_raw, np.ndarray):
                raise TypeError("'tanks_volume_data_raw' must be an instance of 'numpy.ndarray'" +
                                f" but not of '{type(tanks_volume_data_raw)}'")
        if sensor_faults is None or not isinstance(sensor_faults, list):
            raise TypeError("'sensor_faults' must be a list of " +
                            "'epyt_flow.simulation.events.SensorFault' instances but " +
                            f"'{type(sensor_faults)}'")
        if surface_species_concentration_raw is not None:
            if not isinstance(surface_species_concentration_raw, np.ndarray):
                raise TypeError("'surface_species_concentration_raw' must be an instance of " +
                                "'numpy.ndarray' but not of " +
                                f"'{type(surface_species_concentration_raw)}'")
        if bulk_species_node_concentration_raw is not None:
            if not isinstance(bulk_species_node_concentration_raw, np.ndarray):
                raise TypeError("'bulk_species_node_concentration_raw' must be an instance of " +
                                "'numpy.ndarray' but not of " +
                                f"'{type(bulk_species_node_concentration_raw)}'")
        if bulk_species_link_concentration_raw is not None:
            if not isinstance(bulk_species_link_concentration_raw, np.ndarray):
                raise TypeError("'bulk_species_link_concentration_raw' must be an instance of " +
                                "'numpy.ndarray' but not of " +
                                f"'{type(bulk_species_link_concentration_raw)}'")
        if pump_energy_usage_data is not None:
            if not isinstance(pump_energy_usage_data, np.ndarray):
                raise TypeError("'pump_energy_usage_data' must be an instance of 'numpy.ndarray' " +
                                f"but not of '{type(pump_energy_usage_data)}'")
        if pump_efficiency_data is not None:
            if not isinstance(pump_efficiency_data, np.ndarray):
                raise TypeError("'pump_efficiency_data' must be an instance of 'numpy.ndarray' " +
                                f"but not of '{type(pump_efficiency_data)}'")
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
        if not isinstance(frozen_sensor_config, bool):
            raise TypeError("'frozen_sensor_config' must be an instance of 'bool' " +
                            f"but not of '{type(frozen_sensor_config)}'")

        def __raise_shape_mismatch(var_name: str) -> None:
            raise ValueError(f"Shape mismatch in '{var_name}' -- " +
                             "i.e number of time steps in 'sensor_readings_time' " +
                             "must match number of raw measurements.")

        n_time_steps = sensor_readings_time.shape[0]
        if pressure_data_raw is not None:
            if pressure_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("pressure_data_raw")
        if flow_data_raw is not None:
            if flow_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("flow_data_raw")
        if demand_data_raw is not None:
            if demand_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("demand_data_raw")
        if node_quality_data_raw is not None:
            if node_quality_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("node_quality_data_raw")
        if link_quality_data_raw is not None:
            if link_quality_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("link_quality_data_raw")
        if valves_state_data_raw is not None:
            if valves_state_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("valves_state_data_raw")
        if pumps_state_data_raw is not None:
            if pumps_state_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("pumps_state_data_raw")
        if tanks_volume_data_raw is not None:
            if tanks_volume_data_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("tanks_volume_data_raw")
        if valves_state_data_raw is not None:
            if not valves_state_data_raw.shape[0] == n_time_steps:
                __raise_shape_mismatch("valves_state_data_raw")
        if pumps_state_data_raw is not None:
            if not pumps_state_data_raw.shape[0] == n_time_steps:
                __raise_shape_mismatch("pumps_state_data_raw")
        if tanks_volume_data_raw is not None:
            if not tanks_volume_data_raw.shape[0] == n_time_steps:
                __raise_shape_mismatch("tanks_volume_data_raw")
        if bulk_species_node_concentration_raw is not None:
            if bulk_species_node_concentration_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("bulk_species_node_concentration_raw")
        if bulk_species_link_concentration_raw is not None:
            if bulk_species_link_concentration_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("bulk_species_link_concentration_raw")
        if surface_species_concentration_raw is not None:
            if surface_species_concentration_raw.shape[0] != n_time_steps:
                __raise_shape_mismatch("surface_species_concentration_raw")
        if pump_energy_usage_data is not None:
            if pump_energy_usage_data.shape[0] != n_time_steps:
                __raise_shape_mismatch("pump_energy_usage_data")
        if pump_efficiency_data is not None:
            if pump_efficiency_data.shape[0] != n_time_steps:
                __raise_shape_mismatch("pump_efficiency_data")

        self.__sensor_config = sensor_config
        self.__sensor_noise = sensor_noise
        self.__sensor_reading_events = sensor_faults + sensor_reading_attacks + \
            sensor_reading_events

        self.__sensor_readings = None
        self.__frozen_sensor_config = frozen_sensor_config
        self.__sensor_readings_time = sensor_readings_time
        self.__pump_energy_usage_data = pump_energy_usage_data
        self.__pump_efficiency_data = pump_efficiency_data

        if self.__frozen_sensor_config is False:
            self.__pressure_data_raw = pressure_data_raw
            self.__flow_data_raw = flow_data_raw
            self.__demand_data_raw = demand_data_raw
            self.__node_quality_data_raw = node_quality_data_raw
            self.__link_quality_data_raw = link_quality_data_raw
            self.__pumps_state_data_raw = pumps_state_data_raw
            self.__valves_state_data_raw = valves_state_data_raw
            self.__tanks_volume_data_raw = tanks_volume_data_raw
            self.__surface_species_concentration_raw = surface_species_concentration_raw
            self.__bulk_species_node_concentration_raw = bulk_species_node_concentration_raw
            self.__bulk_species_link_concentration_raw = bulk_species_link_concentration_raw
        else:
            sensor_config = self.__sensor_config

            node_to_idx = sensor_config.node_id_to_idx
            link_to_idx = sensor_config.link_id_to_idx
            pump_to_idx = sensor_config.pump_id_to_idx
            valve_to_idx = sensor_config.valve_id_to_idx
            tank_to_idx = sensor_config.tank_id_to_idx

            # EPANET quantities
            def __reduce_data(data: np.ndarray, sensors: list[str],
                              item_to_idx: Callable[[str], int]) -> np.ndarray:
                idx = [item_to_idx(item_id) for item_id in sensors]

                if data is None or len(idx) == 0:
                    return None
                else:
                    return data[:, idx]

            self.__pressure_data_raw = __reduce_data(data=pressure_data_raw,
                                                     item_to_idx=node_to_idx,
                                                     sensors=sensor_config.pressure_sensors)
            self.__flow_data_raw = __reduce_data(data=flow_data_raw,
                                                 item_to_idx=link_to_idx,
                                                 sensors=sensor_config.flow_sensors)
            self.__demand_data_raw = __reduce_data(data=demand_data_raw,
                                                   item_to_idx=node_to_idx,
                                                   sensors=sensor_config.demand_sensors)
            self.__node_quality_data_raw = __reduce_data(data=node_quality_data_raw,
                                                         item_to_idx=node_to_idx,
                                                         sensors=sensor_config.quality_node_sensors)
            self.__link_quality_data_raw = __reduce_data(data=link_quality_data_raw,
                                                         item_to_idx=link_to_idx,
                                                         sensors=sensor_config.quality_link_sensors)
            self.__pumps_state_data_raw = __reduce_data(data=pumps_state_data_raw,
                                                        item_to_idx=pump_to_idx,
                                                        sensors=sensor_config.pump_state_sensors)
            self.__valves_state_data_raw = __reduce_data(data=valves_state_data_raw,
                                                         item_to_idx=valve_to_idx,
                                                         sensors=sensor_config.valve_state_sensors)
            self.__tanks_volume_data_raw = __reduce_data(data=tanks_volume_data_raw,
                                                         item_to_idx=tank_to_idx,
                                                         sensors=sensor_config.tank_volume_sensors)

            # EPANET-MSX quantities
            def __reduce_msx_data(data: np.ndarray, sensors: list[tuple[list[int], list[int]]]
                                  ) -> np.ndarray:
                if data is None or len(sensors) == 0:
                    return None
                else:
                    r = []
                    for species_idx, item_idx in sensors:
                        r.append(data[:, species_idx, item_idx].reshape(-1, len(item_idx)))

                    return np.concatenate(r, axis=1)

            node_bulk_species_idx = [(sensor_config.bulkspecies_id_to_idx(s),
                                      [sensor_config.node_id_to_idx(node_id)
                                       for node_id in sensor_config.bulk_species_node_sensors[s]
                                       ]) for s in sensor_config.bulk_species_node_sensors.keys()]
            self.__bulk_species_node_concentration_raw = \
                __reduce_msx_data(data=bulk_species_node_concentration_raw,
                                  sensors=node_bulk_species_idx)

            bulk_species_link_idx = [(sensor_config.bulkspecies_id_to_idx(s),
                                      [sensor_config.link_id_to_idx(link_id)
                                       for link_id in sensor_config.bulk_species_link_sensors[s]
                                       ]) for s in sensor_config.bulk_species_link_sensors.keys()]
            self.__bulk_species_link_concentration_raw = \
                __reduce_msx_data(data=bulk_species_link_concentration_raw,
                                  sensors=bulk_species_link_idx)

            surface_species_idx = [(sensor_config.surfacespecies_id_to_idx(s),
                                    [sensor_config.link_id_to_idx(link_id)
                                     for link_id in sensor_config.surface_species_sensors[s]
                                     ]) for s in sensor_config.surface_species_sensors.keys()]
            self.__surface_species_concentration_raw = \
                __reduce_msx_data(data=surface_species_concentration_raw,
                                  sensors=surface_species_idx)

        self.__init()

        super().__init__(**kwds)

    @property
    def frozen_sensor_config(self) -> bool:
        """
        Checks if the sensor configuration is frozen or not.

        Returns
        -------
        `bool`
            True if the sensor configuration is frozen, False otherwise.
        """
        return self.__frozen_sensor_config

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
        if self.__frozen_sensor_config is True:
            raise RuntimeError("Sensor config can not be changed because it is frozen")

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
        list[:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault`]
            All sensor faults.
        """
        return deepcopy(list(filter(lambda e: isinstance(e, SensorFault),
                                    self.__sensor_reading_events)))

    @sensor_faults.setter
    def sensor_faults(self, sensor_faults: list[SensorFault]) -> None:
        self.change_sensor_faults(sensor_faults)

    @property
    def sensor_reading_attacks(self) -> list[SensorReadingAttack]:
        """
        Gets all sensor reading attacks.

        Returns
        -------
        list[:class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack`]
            All sensor reading attacks.
        """
        return deepcopy(list(filter(lambda e: isinstance(e, SensorReadingAttack),
                                    self.__sensor_reading_events)))

    @sensor_reading_attacks.setter
    def sensor_reading_attacks(self, sensor_reading_attacks: list[SensorReadingAttack]) -> None:
        self.change_sensor_reading_attacks(sensor_reading_attacks)

    @property
    def sensor_reading_events(self) -> list[SensorReadingEvent]:
        """
        Gets all sensor reading events.

        Returns
        -------
        list[:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent`]
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
    def tanks_volume_data_raw(self) -> np.ndarray:
        """
        Gets the raw tank volume readings.

        Returns
        -------
        `numpy.ndarray`
            Raw tank volume readings.
        """
        return deepcopy(self.__tanks_volume_data_raw)

    @property
    def surface_species_concentration_raw(self) -> np.ndarray:
        """
        Gets the raw surface species concentrations at links/pipes.

        Returns
        -------
        `numpy.ndarray`
            Raw species concentrations.
        """
        return deepcopy(self.__surface_species_concentration_raw)

    @property
    def bulk_species_node_concentration_raw(self) -> np.ndarray:
        """
        Gets the raw bulk species concentrations at nodes.

        Returns
        -------
        `numpy.ndarray`
            Raw species concentrations.
        """
        return deepcopy(self.__bulk_species_node_concentration_raw)

    @property
    def bulk_species_link_concentration_raw(self) -> np.ndarray:
        """
        Gets the raw bulk species concentrations at links/pipes.

        Returns
        -------
        `numpy.ndarray`
            Raw species concentrations.
        """
        return deepcopy(self.__bulk_species_link_concentration_raw)

    @property
    def pump_energy_usage_data(self) -> np.ndarray:
        """
        Gets the energy usage of each pump.

        .. note::
            This attribute is NOT included in
            :func:`~epyt_flow.simulation.scada.scada_data.ScadaData.get_data` --
            calling this function is the only way of accessing the energy usage of each pump.

        Returns
        -------
        `numpy.ndarray`
            Energy usage of each pump.
        """
        return deepcopy(self.__pump_energy_usage_data)

    @property
    def pump_efficiency_data(self) -> np.ndarray:
        """
        Gets the pumps' efficiency.

        .. note::
            This attribute is NOT included in
            :func:`~epyt_flow.simulation.scada.scada_data.ScadaData.get_data` --
            calling this function is the only way of accessing the pumps' efficiency.

        Returns
        -------
        `numpy.ndarray`
            Pumps' efficiency.
        """
        return deepcopy(self.__pump_efficiency_data)

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
            elif sensor_event.sensor_type == SENSOR_TYPE_TANK_VOLUME:
                idx = self.__sensor_config.get_index_of_reading(
                    tank_volume_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_NODE_BULK_SPECIES:
                idx = self.__sensor_config.get_index_of_reading(
                    bulk_species_node_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_LINK_BULK_SPECIES:
                idx = self.__sensor_config.get_index_of_reading(
                    bulk_species_link_sensor=sensor_event.sensor_id)
            elif sensor_event.sensor_type == SENSOR_TYPE_SURFACE_SPECIES:
                idx = self.__sensor_config.get_index_of_reading(
                    surface_species_sensor=sensor_event.sensor_id)

            self.__apply_sensor_reading_events.append((idx, sensor_event.apply))

        self.__sensor_readings = None

    def get_attributes(self) -> dict:
        attr = {"sensor_config": self.__sensor_config,
                "frozen_sensor_config": self.__frozen_sensor_config,
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
                "tanks_volume_data_raw": self.__tanks_volume_data_raw,
                "surface_species_concentration_raw": self.__surface_species_concentration_raw,
                "bulk_species_node_concentration_raw": self.__bulk_species_node_concentration_raw,
                "bulk_species_link_concentration_raw": self.__bulk_species_link_concentration_raw,
                "pump_energy_usage_data": self.__pump_energy_usage_data,
                "pump_efficiency_data": self.__pump_efficiency_data}

        return super().get_attributes() | attr

    def __eq__(self, other) -> bool:
        if not isinstance(other, ScadaData):
            raise TypeError(f"Can not compare 'ScadaData' instance to '{type(other)}' instance")

        try:
            return self.__sensor_config == other.sensor_config \
                and self.__frozen_sensor_config == other.frozen_sensor_config \
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
                and np.all(self.__tanks_volume_data_raw == other.tanks_volume_data_raw) \
                and np.all(self.__surface_species_concentration_raw ==
                           other.surface_species_concentration_raw) \
                and np.all(self.__bulk_species_node_concentration_raw ==
                           other.bulk_species_node_concentration_raw) \
                and np.all(self.__bulk_species_link_concentration_raw ==
                           other.bulk_species_link_concentration_raw) \
                and np.all(self.__pump_energy_usage_data == other.pump_energy_usage_data) \
                and np.all(self.__pump_efficiency_data == other.pump_efficiency_data)
        except Exception as ex:
            warnings.warn(ex.__str__())
            return False

    def __str__(self) -> str:
        return f"sensor_config: {self.__sensor_config} " + \
            f"frozen_sensor_config: {self.__frozen_sensor_config} " + \
            f"sensor_noise: {self.__sensor_noise} " + \
            f"sensor_reading_events: {self.__sensor_reading_events} " + \
            f"pressure_data_raw: {self.__pressure_data_raw} " + \
            f"flow_data_raw: {self.__flow_data_raw} demand_data_raw: {self.__demand_data_raw} " + \
            f"node_quality_data_raw: {self.__node_quality_data_raw} " + \
            f"link_quality_data_raw: {self.__link_quality_data_raw} " + \
            f"sensor_readings_time: {self.__sensor_readings_time} " + \
            f"pumps_state_data_raw: {self.__pumps_state_data_raw} " + \
            f"valves_state_data_raw: {self.__valves_state_data_raw} " + \
            f"tanks_volume_data_raw: {self.__tanks_volume_data_raw} " + \
            f"surface_species_concentration_raw: {self.__surface_species_concentration_raw} " + \
            f"bulk_species_node_concentration_raw: {self.__bulk_species_node_concentration_raw}" +\
            f" bulk_species_link_concentration_raw: {self.__bulk_species_link_concentration_raw}" +\
            f" pump_efficiency_data: {self.__pump_efficiency_data} " + \
            f"pump_energy_usage_data: {self.__pump_energy_usage_data}"

    def change_sensor_config(self, sensor_config: SensorConfig) -> None:
        """
        Changes the sensor configuration.

        Parameters
        ----------
        sensor_config : :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
            New sensor configuration.
        """
        if self.__frozen_sensor_config is True:
            raise RuntimeError("Sensor configuration can not be changed because it is frozen")
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

        sensor_faults : list[:class:`~epyt_flow.simulation.events.sensor_faults.SensorFault`]
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

        sensor_reading_attacks : list[:class:`~epyt_flow.simulation.events.sensor_reading_attack.SensorReadingAttack`]
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

        sensor_reading_events : list[:class:`~epyt_flow.simulation.events.sensor_reading_event.SensorReadingEvent`]
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
        Joins two :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instances based
        on the sensor reading times. Consequently, **both instances must be equal in their
        sensor reading times**.
        Attributes (i.e. types of sensor readings) that are NOT present in THIS instance
        but in `others` will be added to this instance -- all other attributes are ignored.
        The sensor configuration is updated according to the sensor readings in `other`.

        Parameters
        ----------
        other : :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData`
            Other scada data to be concatenated to this data.
        """
        if not isinstance(other, ScadaData):
            raise TypeError("'other' must be an instance of 'ScadaData' " +
                            f"but not of '{type(other)}'")
        if self.__frozen_sensor_config != other.frozen_sensor_config:
            raise ValueError("Sensor configurations of both instances must be " +
                             "either frozen or not frozen")
        if not np.all(self.__sensor_readings_time == other.sensor_readings_time):
            raise ValueError("Both 'ScadaData' instances must be equal in their " +
                             "sensor readings times")
        if any(e1 != e2 for e1, e2 in zip(self.__sensor_reading_events,
                                          other.sensor_reading_events)):
            raise ValueError("'other' must have the same sensor reading events as this instance!")
        if self.__sensor_config.nodes != other.sensor_config.nodes:
            raise ValueError("Inconsistency in nodes found")
        if self.__sensor_config.links != other.sensor_config.links:
            raise ValueError("Inconsistency in links/pipes found")
        if self.__sensor_config.valves != other.sensor_config.valves:
            raise ValueError("Inconsistency in valves found")
        if self.__sensor_config.pumps != other.sensor_config.pumps:
            raise ValueError("Inconsistency in pumps found")
        if self.__sensor_config.tanks != other.sensor_config.tanks:
            raise ValueError("Inconsistency in tanks found")
        if self.__sensor_config.bulk_species != other.sensor_config.bulk_species:
            raise ValueError("Inconsistency in bulk species found")
        if self.__sensor_config.surface_species != other.sensor_config.surface_species:
            raise ValueError("Inconsistency in surface species found")

        self.__sensor_readings = None

        if self.__pressure_data_raw is None and other.pressure_data_raw is not None:
            self.__pressure_data_raw = other.pressure_data_raw
            self.__sensor_config.pressure_sensors = other.sensor_config.pressure_sensors

        if self.__flow_data_raw is None and other.flow_data_raw is not None:
            self.__flow_data_raw = other.flow_data_raw
            self.__sensor_config.flow_sensors = other.sensor_config.flow_sensors

        if self.__demand_data_raw is None and other.demand_data_raw is not None:
            self.__demand_data_raw = other.demand_data_raw
            self.__sensor_config.demand_sensors = other.sensor_config.demand_sensors

        if self.__node_quality_data_raw is None and other.node_quality_data_raw is not None:
            self.__node_quality_data_raw = other.node_quality_data_raw
            self.__sensor_config.quality_node_sensors = other.sensor_config.quality_node_sensors

        if self.__link_quality_data_raw is None and other.link_quality_data_raw is not None:
            self.__link_quality_data_raw = other.link_quality_data_raw
            self.__sensor_config.quality_node_sensors = other.sensor_config.quality_node_sensors

        if self.__valves_state_data_raw is None and other.valves_state_data_raw is not None:
            self.__valves_state_data_raw = other.valves_state_data_raw
            self.__sensor_config.valve_state_sensors = other.sensor_config.valve_state_sensors

        if self.__pumps_state_data_raw is None and other.pumps_state_data_raw is not None:
            self.__pumps_state_data_raw = other.pumps_state_data_raw
            self.__sensor_config.pump_state_sensors = other.sensor_config.pump_state_sensors

        if self.__tanks_volume_data_raw is None and other.tanks_volume_data_raw is not None:
            self.__tanks_volume_data_raw = other.tanks_volume_data_raw
            self.__sensor_config.tank_volume_sensors = other.sensor_config.tank_volume_sensors

        if self.__bulk_species_node_concentration_raw is None and \
                other.bulk_species_node_concentration_raw is not None:
            self.__bulk_species_node_concentration_raw = other.bulk_species_node_concentration_raw
            self.__sensor_config.bulk_species_node_sensors = \
                other.sensor_config.bulk_species_node_sensors

        if self.__bulk_species_link_concentration_raw is None and \
                other.bulk_species_link_concentration_raw is not None:
            self.__bulk_species_link_concentration_raw = other.bulk_species_link_concentration_raw
            self.__sensor_config.bulk_species_link_sensors = \
                other.sensor_config.bulk_species_link_sensors

        if self.__surface_species_concentration_raw is None and \
                other.surface_species_concentration_raw is not None:
            self.__surface_species_concentration_raw = other.surface_species_concentration_raw
            self.__sensor_config.surface_species_sensors = \
                other.sensor_config.surface_species_sensors

        if self.__pump_energy_usage_data is None and other.pump_energy_usage_data is not None:
            self.__pump_energy_usage_data = other.pump_energy_usage_data

        if self.__pump_efficiency_data is None and other.pump_efficiency_data is not None:
            self.__pump_efficiency_data = other.pump_efficiency_data

        self.__init()

    def concatenate(self, other) -> None:
        """
        Concatenates two :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instances
        -- i.e. add SCADA data from another given
        :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instance to this one.

        Note that the two :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData` instances
        must be the same in all other attributs (e.g. sensor configuration, etc.).

        Parameters
        ----------
        other : :class:`~epyt_flow.simulation.scada_data.scada_data.ScadaData`
            Other scada data to be concatenated to this data.
        """
        if not isinstance(other, ScadaData):
            raise TypeError(f"'other' must be an instance of 'ScadaData' but not of {type(other)}")
        if self.__sensor_config != other.sensor_config:
            raise ValueError("Sensor configurations must be the same!")
        if self.__frozen_sensor_config != other.frozen_sensor_config:
            raise ValueError("Sensor configurations of both instances must be " +
                             "either frozen or not frozen")
        if len(self.__sensor_reading_events) != len(other.sensor_reading_events):
            raise ValueError("'other' must have the same sensor reading events as this instance!")
        if any(e1 != e2 for e1, e2 in zip(self.__sensor_reading_events,
                                          other.sensor_reading_events)):
            raise ValueError("'other' must have the same sensor reading events as this instance!")

        self.__sensor_readings = None

        self.__sensor_readings_time = np.concatenate(
            (self.__sensor_readings_time, other.sensor_readings_time), axis=0)

        if self.__pressure_data_raw is not None:
            self.__pressure_data_raw = np.concatenate(
                (self.__pressure_data_raw, other.pressure_data_raw), axis=0)

        if self.__flow_data_raw is not None:
            self.__flow_data_raw = np.concatenate(
                (self.__flow_data_raw, other.flow_data_raw), axis=0)

        if self.__demand_data_raw is not None:
            self.__demand_data_raw = np.concatenate(
                (self.__demand_data_raw, other.demand_data_raw), axis=0)

        if self.__node_quality_data_raw is not None:
            self.__node_quality_data_raw = np.concatenate(
                (self.__node_quality_data_raw, other.node_quality_data_raw), axis=0)

        if self.__link_quality_data_raw is not None:
            self.__link_quality_data_raw = np.concatenate(
                (self.__link_quality_data_raw, other.link_quality_data_raw), axis=0)

        if self.__pumps_state_data_raw is not None:
            self.__pumps_state_data_raw = np.concatenate(
                (self.__pumps_state_data_raw, other.pumps_state_data_raw), axis=0)

        if self.__valves_state_data_raw is not None:
            self.__valves_state_data_raw = np.concatenate(
                (self.__valves_state_data_raw, other.valves_state_data_raw), axis=0)

        if self.__tanks_volume_data_raw is not None:
            self.__tanks_volume_data_raw = np.concatenate(
                (self.__tanks_volume_data_raw, other.tanks_volume_data_raw), axis=0)

        if self.__surface_species_concentration_raw is not None:
            self.__surface_species_concentration_raw = np.concatenate(
                (self.__surface_species_concentration_raw,
                 other.surface_species_concentration_raw),
                axis=0)

        if self.__bulk_species_node_concentration_raw is not None:
            self.__bulk_species_node_concentration_raw = np.concatenate(
                (self.__bulk_species_node_concentration_raw,
                 other.bulk_species_node_concentration_raw),
                axis=0)

        if self.__bulk_species_link_concentration_raw is not None:
            self.__bulk_species_link_concentration_raw = np.concatenate(
                (self.__bulk_species_link_concentration_raw,
                 other.bulk_species_link_concentration_raw),
                axis=0)

        if self.__pump_energy_usage_data is not None:
            self.__pump_energy_usage_data = np.concatenate(
                (self.__pump_energy_usage_data, other.pump_energy_usage_data),
                axis=0)

        if self.__pump_efficiency_data is not None:
            self.__pump_efficiency_data = np.concatenate(
                (self.__pump_efficiency_data, other.pump_efficiency_data),
                axis=0)

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
        if self.__frozen_sensor_config is False:
            args = {"pressures": self.__pressure_data_raw,
                    "flows": self.__flow_data_raw,
                    "demands": self.__demand_data_raw,
                    "nodes_quality": self.__node_quality_data_raw,
                    "links_quality": self.__link_quality_data_raw,
                    "pumps_state": self.__pumps_state_data_raw,
                    "valves_state": self.__valves_state_data_raw,
                    "tanks_volume": self.__tanks_volume_data_raw,
                    "bulk_species_node_concentrations": self.__bulk_species_node_concentration_raw,
                    "bulk_species_link_concentrations": self.__bulk_species_link_concentration_raw,
                    "surface_species_concentrations": self.__surface_species_concentration_raw}
            sensor_readings = self.__sensor_config.compute_readings(**args)
        else:
            data = []

            if self.__pressure_data_raw is not None:
                data.append(self.__pressure_data_raw)
            if self.__flow_data_raw is not None:
                data.append(self.__flow_data_raw)
            if self.__demand_data_raw is not None:
                data.append(self.__demand_data_raw)
            if self.__node_quality_data_raw is not None:
                data.append(self.__node_quality_data_raw)
            if self.__link_quality_data_raw is not None:
                data.append(self.__link_quality_data_raw)
            if self.__valves_state_data_raw is not None:
                data.append(self.__valves_state_data_raw)
            if self.__pumps_state_data_raw is not None:
                data.append(self.__pumps_state_data_raw)
            if self.__tanks_volume_data_raw is not None:
                data.append(self.__tanks_volume_data_raw)
            if self.__surface_species_concentration_raw is not None:
                data.append(self.__surface_species_concentration_raw)
            if self.__bulk_species_node_concentration_raw is not None:
                data.append(self.__bulk_species_node_concentration_raw)
            if self.__bulk_species_link_concentration_raw is not None:
                data.append(self.__bulk_species_link_concentration_raw)

            sensor_readings = np.concatenate(data, axis=1)

        # Apply sensor uncertainties
        state_sensors_idx = []   # Pump states and valve states are NOT affected!
        for link_id in self.sensor_config.pump_state_sensors:
            state_sensors_idx.append(
                self.__sensor_config.get_index_of_reading(pump_state_sensor=link_id))
        for link_id in self.sensor_config.valve_state_sensors:
            state_sensors_idx.append(
                self.__sensor_config.get_index_of_reading(valve_state_sensor=link_id))

        mask = np.ones(sensor_readings.shape[1], dtype=bool)
        mask[state_sensors_idx] = False

        sensor_readings[:, mask] = self.__apply_sensor_noise(sensor_readings[:, mask])

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
        if self.__sensor_config.pressure_sensors == []:
            raise ValueError("No pressure sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.pressure_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "pressure sensor configuration")
        else:
            sensor_locations = self.__sensor_config.pressure_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(pressure_sensor=s_id)
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
        if self.__sensor_config.flow_sensors == []:
            raise ValueError("No flow sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.flow_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "flow sensor configuration")
        else:
            sensor_locations = self.__sensor_config.flow_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(flow_sensor=s_id)
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
        if self.__sensor_config.demand_sensors == []:
            raise ValueError("No demand sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.demand_sensors for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "demand sensor configuration")
        else:
            sensor_locations = self.__sensor_config.demand_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(demand_sensor=s_id)
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
        if self.__sensor_config.quality_node_sensors == []:
            raise ValueError("No node quality sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.quality_node_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "node quality sensor configuration")
        else:
            sensor_locations = self.__sensor_config.quality_node_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(node_quality_sensor=s_id)
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
        if self.__sensor_config.quality_link_sensors == []:
            raise ValueError("No link quality sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.quality_link_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "link quality sensor configuration")
        else:
            sensor_locations = self.__sensor_config.quality_link_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(link_quality_sensor=s_id)
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
        if self.__sensor_config.pump_state_sensors == []:
            raise ValueError("No pump state sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.pump_state_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "pump state sensor configuration")
        else:
            sensor_locations = self.__sensor_config.pump_state_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(pump_state_sensor=s_id)
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
        if self.__sensor_config.valve_state_sensors == []:
            raise ValueError("No valve state sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.valve_state_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "valve state sensor configuration")
        else:
            sensor_locations = self.__sensor_config.valve_state_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(valve_state_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_tanks_water_volume(self, sensor_locations: list[str] = None) -> np.ndarray:
        """
        Gets the final water tanks volume sensor readings -- note that those might be subject to
        given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        sensor_locations : `list[str]`, optional
            Existing flow sensor locations for which the sensor readings are requested.
            If None, the readings from all water tanks volume sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Water tanks volume sensor readings.
        """
        if self.__sensor_config.tank_volume_sensors == []:
            raise ValueError("No tank volume sensors set")
        if sensor_locations is not None:
            if not isinstance(sensor_locations, list):
                raise TypeError("'sensor_locations' must be an instance of 'list[str]' " +
                                f"but not of '{type(sensor_locations)}'")
            if any(s_id not in self.__sensor_config.tank_volume_sensors
                   for s_id in sensor_locations):
                raise ValueError("Invalid sensor ID in 'sensor_locations' -- note that all " +
                                 "sensors in 'sensor_locations' must be set in the current " +
                                 "water tanks volume sensor configuration")
        else:
            sensor_locations = self.__sensor_config.tank_volume_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(tank_volume_sensor=s_id)
               for s_id in sensor_locations]
        return self.__sensor_readings[:, idx]

    def get_data_surface_species_concentration(self,
                                               surface_species_sensor_locations: dict = None
                                               ) -> np.ndarray:
        """
        Gets the final surface species concentration sensor readings --
        note that those might be subject to given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        surface_species_sensor_locations : `dict`, optional
            Existing surface species concentration sensors (species ID and link/pipe IDs) for which
            the sensor readings are requested.
            If None, the readings from all surface species concentration sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Surface species concentration sensor readings.
        """
        if self.__sensor_config.surface_species_sensors == {}:
            raise ValueError("No surface species sensors set")
        if surface_species_sensor_locations is not None:
            if not isinstance(surface_species_sensor_locations, dict):
                raise TypeError("'surface_species_sensor_locations' must be an instance of 'dict'" +
                                f" but not of '{type(surface_species_sensor_locations)}'")
            for species_id in surface_species_sensor_locations:
                if species_id not in self.__sensor_config.surface_species_sensors:
                    raise ValueError(f"Species '{species_id}' is not included in the " +
                                     "sensor configuration")

                my_surface_species_sensor_locations = \
                    self.__sensor_config.surface_species_sensors[species_id]
                for sensor_id in surface_species_sensor_locations[species_id]:
                    if sensor_id not in my_surface_species_sensor_locations:
                        raise ValueError(f"Link '{sensor_id}' is not included in the " +
                                         f"sensor configuration for species '{species_id}'")
        else:
            surface_species_sensor_locations = self.__sensor_config.surface_species_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(
            surface_species_sensor=(species_id, link_id))
                for species_id in surface_species_sensor_locations
                for link_id in surface_species_sensor_locations[species_id]]
        return self.__sensor_readings[:, idx]

    def get_data_bulk_species_node_concentration(self,
                                                 bulk_species_sensor_locations: dict = None
                                                 ) -> np.ndarray:
        """
        Gets the final bulk species node concentration sensor readings --
        note that those might be subject to given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        bulk_species_sensor_locations : `dict`, optional
            Existing bulk species concentration sensors (species ID and node IDs) for which
            the sensor readings are requested.
            If None, the readings from all bulk species node concentration sensors are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Bulk species concentration sensor readings.
        """
        if self.__sensor_config.bulk_species_node_sensors == {}:
            raise ValueError("No bulk species node sensors set")
        if bulk_species_sensor_locations is not None:
            if not isinstance(bulk_species_sensor_locations, dict):
                raise TypeError("'bulk_species_sensor_locations' must be an instance of 'dict'" +
                                f" but not of '{type(bulk_species_sensor_locations)}'")
            for species_id in bulk_species_sensor_locations:
                if species_id not in self.__sensor_config.bulk_species_sensors:
                    raise ValueError(f"Species '{species_id}' is not included in the " +
                                     "sensor configuration")

                my_bulk_species_sensor_locations = \
                    self.__sensor_config.bulk_species_node_sensors[species_id]
                for sensor_id in bulk_species_sensor_locations[species_id]:
                    if sensor_id not in my_bulk_species_sensor_locations:
                        raise ValueError(f"Link '{sensor_id}' is not included in the " +
                                         f"sensor configuration for species '{species_id}'")
        else:
            bulk_species_sensor_locations = self.__sensor_config.bulk_species_node_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(
            bulk_species_node_sensor=(species_id, node_id))
                for species_id in bulk_species_sensor_locations
                for node_id in bulk_species_sensor_locations[species_id]]
        return self.__sensor_readings[:, idx]

    def get_data_bulk_species_link_concentration(self,
                                                 bulk_species_sensor_locations: dict = None
                                                 ) -> np.ndarray:
        """
        Gets the final bulk species link/pipe concentration sensor readings --
        note that those might be subject to given sensor faults and sensor noise/uncertainty.

        Parameters
        ----------
        bulk_species_sensor_locations : `dict`, optional
            Existing bulk species concentration sensors (species ID and link/pipe IDs) for which
            the sensor readings are requested.
            If None, the readings from all bulk species concentration link/pipe sensors
            are returned.

            The default is None.

        Returns
        -------
        `numpy.ndarray`
            Bulk species concentration sensor readings.
        """
        if self.__sensor_config.bulk_species_link_sensors == {}:
            raise ValueError("No bulk species link/pipe sensors set")
        if bulk_species_sensor_locations is not None:
            if not isinstance(bulk_species_sensor_locations, dict):
                raise TypeError("'bulk_species_sensor_locations' must be an instance of 'dict'" +
                                f" but not of '{type(bulk_species_sensor_locations)}'")
            for species_id in bulk_species_sensor_locations:
                if species_id not in self.__sensor_config.bulk_species_link_sensors:
                    raise ValueError(f"Species '{species_id}' is not included in the " +
                                     "sensor configuration")

                my_bulk_species_sensor_locations = \
                    self.__sensor_config.bulk_species_link_sensors[species_id]
                for sensor_id in bulk_species_sensor_locations[species_id]:
                    if sensor_id not in my_bulk_species_sensor_locations:
                        raise ValueError(f"Link '{sensor_id}' is not included in the " +
                                         f"sensor configuration for species '{species_id}'")
        else:
            bulk_species_sensor_locations = self.__sensor_config.bulk_species_link_sensors

        if self.__sensor_readings is None:
            self.get_data()

        idx = [self.__sensor_config.get_index_of_reading(
            bulk_species_link_sensor=(species_id, node_id))
                for species_id in bulk_species_sensor_locations
                for node_id in bulk_species_sensor_locations[species_id]]
        return self.__sensor_readings[:, idx]
