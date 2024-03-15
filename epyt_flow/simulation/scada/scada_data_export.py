"""
Module provides classes for exporting SCADA data stored in
:class:`~epyt_flow.simulation.scada.scada_data.ScadaData`.
"""
from abc import abstractmethod
import numpy as np
from scipy.io import savemat
import pandas as pd

from .scada_data import ScadaData
from ..sensor_config import SensorConfig


class ScadaDataExport():
    """
    Base class for exporting SCADA data stored in
    :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`.

    Parameters
    ----------
    f_out : `str`
        Path to the file to which the SCADA data will be exported.
    export_raw_data : `bool`, optional
        If True, the raw measurements (i.e. sensor reading without any noise or faults)
        are exported instead of the final sensor readings.

        The default is False.
    """

    def __init__(self, f_out: str, export_raw_data: bool = False, **kwds):
        self.__f_out = f_out
        self.__export_raw_data = export_raw_data

        super().__init__(**kwds)

    @property
    def f_out(self) -> str:
        """
        Gets the path to the file to which the SCADA data will be exported.

        Returns
        -------
        `str`
            Path to the file to which the SCADA data will be exported.
        """
        return self.__f_out

    @property
    def export_raw_data(self) -> bool:
        """
        True if the raw measurements instead of the final sensor readings are requested.

        Returns
        -------
        `bool`
            True if the raw measurements instead of the final sensor readings are requested.
        """
        return self.__export_raw_data

    def create_global_sensor_config(self, scada_data: ScadaData) -> SensorConfig:
        """
        Creates a global sensor configuration with sensors placed everywhere.

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data for which the global sensor configuration is to be created.

        Returns
        -------
        :class:`~epyt_flow.simulation.sensor_config.SensorConfig`
            Global sensor configuration.
        """
        old_sensor_config = scada_data.sensor_config

        sensor_config = SensorConfig(nodes=old_sensor_config.nodes,
                                     links=old_sensor_config.links,
                                     valves=old_sensor_config.valves,
                                     pumps=old_sensor_config.pumps,
                                     tanks=old_sensor_config.tanks)
        sensor_config.pressure_sensors = sensor_config.nodes
        sensor_config.flow_sensors = sensor_config.links
        sensor_config.demand_sensors = sensor_config.nodes
        sensor_config.quality_node_sensors = sensor_config.nodes
        sensor_config.quality_link_sensors = sensor_config.links
        sensor_config.valve_state_sensors = sensor_config.valves
        sensor_config.tank_level_sensors = sensor_config.tanks
        sensor_config.pump_state_sensors = sensor_config.pumps

        return sensor_config

    def create_column_desc(self, scada_data: ScadaData) -> np.ndarray:
        """
        Creates columns descriptions -- i.e. sensor type and location for each column

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data to be described.

        Returns
        -------
        `numpy.ndarray`
            2-dimensional array describing all columns of the sensor readings:
            The first dimension describes the sensor type, and the second dimension
            describes the sensor location.
        """
        sensor_readings = scada_data.get_data()

        col_desc = [None for _ in range(sensor_readings.shape[1])]
        sensor_config = scada_data.sensor_config
        sensors_id_to_idx = sensor_config.sensors_id_to_idx
        for sensor_type in sensors_id_to_idx:
            for item_id in sensors_id_to_idx[sensor_type]:
                col_id = sensors_id_to_idx[sensor_type][item_id]
                col_desc[col_id] = [sensor_type, item_id]

        return np.array(col_desc, dtype=object)

    @abstractmethod
    def export(self, scada_data: ScadaData) -> None:
        """
        Exports given SCADA data.

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data to be exported.
        """
        raise NotImplementedError()


class ScadaDataNumpyExport(ScadaDataExport):
    """
    Class for exporting SCADA data to numpy (.npz file).
    """

    def export(self, scada_data: ScadaData) -> None:
        """
        Exports given SCADA data.

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data to be exported.
        """
        if not isinstance(scada_data, ScadaData):
            raise TypeError("'scada_data' must be an instance of " +
                            "'epyt_flow.simulation.scada_data.ScadaData' and not of " +
                            f"'{type(scada_data)}'")

        old_sensor_config = None
        if self.export_raw_data is True:
            # Backup old sensor config and set a new one with sensors everywhere
            old_sensor_config = scada_data.sensor_config
            scada_data.change_sensor_config(self.create_global_sensor_config(scada_data))

        sensor_readings = scada_data.get_data()
        col_desc = self.create_column_desc(scada_data)
        sensor_readings_time = scada_data.sensor_readings_time

        if self.export_raw_data is True:
            # Restore old sensor config
            scada_data.change_sensor_config(old_sensor_config)

        np.savez(self.f_out, sensor_readings=sensor_readings, col_desc=col_desc,
                 sensor_readings_time=sensor_readings_time)


class ScadaDataXlsxExport(ScadaDataExport):
    """
    Class for exporting SCADA data to Excel (.xlsx file).
    """

    def export(self, scada_data: ScadaData) -> None:
        """
        Exports given SCADA data.

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data to be exported.
        """
        if not isinstance(scada_data, ScadaData):
            raise TypeError("'scada_data' must be an instance of " +
                            "'epyt_flow.simulation.scada_data.ScadaData' and not of " +
                            f"'{type(scada_data)}'")

        old_sensor_config = None
        if self.export_raw_data is True:
            # Backup old sensor config and set a new one with sensors everywhere
            old_sensor_config = scada_data.sensor_config
            scada_data.change_sensor_config(self.create_global_sensor_config(scada_data))

        sensor_readings = scada_data.get_data()
        sensor_readings_time = scada_data.sensor_readings_time
        col_desc = self.create_column_desc(scada_data)
        sensors_name = np.array([f"Sensor {i}" for i in range(1, sensor_readings.shape[1] + 1)],
                                dtype=object).reshape(-1, 1)
        col_desc = np.concatenate((sensors_name, col_desc), axis=1)

        if self.export_raw_data is True:
            # Restore old sensor config
            scada_data.change_sensor_config(old_sensor_config)

        with pd.ExcelWriter(self.f_out) as writer:
            pd.DataFrame(sensor_readings, columns=[f"Sensor {i}" for i in
                                                   range(1, sensor_readings.shape[1] + 1)]). \
                to_excel(writer, sheet_name="Sensor readings", index=False)
            pd.DataFrame(sensor_readings_time, columns=["Time (s)"]). \
                to_excel(writer, sheet_name="Sensor readings time", index=False)
            pd.DataFrame(col_desc, columns=["Name", "Type", "Location"]). \
                to_excel(writer, sheet_name="Sensors description", index=False)


class ScadaDataMatlabExport(ScadaDataExport):
    """
    Class for exporting SCADA data to MATLAB (.mat file).
    """

    def export(self, scada_data: ScadaData) -> None:
        """
        Exports given SCADA data.

        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            SCADA data to be exported.
        """
        if not isinstance(scada_data, ScadaData):
            raise TypeError("'scada_data' must be an instance of " +
                            "'epyt_flow.simulation.scada_data.ScadaData' and not of " +
                            f"'{type(scada_data)}'")

        old_sensor_config = None
        if self.export_raw_data is True:
            # Backup old sensor config and set a new one with sensors everywhere
            old_sensor_config = scada_data.sensor_config
            scada_data.change_sensor_config(self.create_global_sensor_config(scada_data))

        sensor_readings = scada_data.get_data()
        sensor_readings_time = scada_data.sensor_readings_time
        col_desc = self.create_column_desc(scada_data)

        if self.export_raw_data is True:
            # Restore old sensor config
            scada_data.change_sensor_config(old_sensor_config)

        savemat(self.f_out, {"sensor_readings": sensor_readings,
                             "sensor_readings_time": sensor_readings_time, "col_desc": col_desc})
