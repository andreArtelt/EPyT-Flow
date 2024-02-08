from abc import abstractmethod, ABC
import numpy as np
import epyt

from . import ScadaData


class AdvancedControlModule(ABC):
    """
    Base class for a control module.

    Attributes
    ----------
    epanet_api : `epyt.epanet`
        API to EPANET and EPANET-MSX. Is set in :func:`init`.
    """
    def __init__(self, **kwds):
        self._epanet_api = None

        super().__init__(**kwds)

    def init(self, epanet_api:epyt.epanet) -> None:
        """
        Initializes the control module.

        Parameters
        ----------
        epanet_api : `epyt.epanet`
            API to EPANET for implementing the control module.
        """
        if not isinstance(epanet_api, epyt.epanet):
            raise ValueError("'epanet_api' must be an instance of 'epyt.epanet' but not of "+\
                             f"'{type(epanet_api)}'")

        self._epanet_api = epanet_api

    def set_pump_status(self, pump_id:str, status:int) -> None:
        """
        Sets the status of a pump.

        Parameters
        ----------
        pump_id : `str`
            ID of the pump for which the status is set.
        status : `int`
            New status of the pump -- either open or closed.
            One of the following: 

                - EN_PUMP_CLOSED  = 2 
                - EN_PUMP_OPEN    = 3  
        """
        pump_idx = self._epanet_api.getLinkPumpNameID().index(pump_id)
        pump_link_idx = self._epanet_api.getLinkPumpIndex()[pump_idx]
        self._epanet_api.setLinkStatus(pump_link_idx, status)

    def set_pump_speed(self, pump_id:str, speed:float) -> None:
        """
        Sets the speed of pump.

        Parameters
        ----------
        pump_id : `str`
            ID of the pump for which the pump speed is set.
        speed : `float`
            New pump speed.
        """
        pump_idx = self._epanet_api.getLinkPumpNameID().index(pump_id)
        pattern_idx = self._epanet_api.getLinkPumpPatternIndex(pump_idx + 1)
        self._epanet_api.setPattern(pattern_idx, np.array([speed]))

    def set_valve_status(self, valve_id:str, status:int) -> None:
        """
        Sets the status of a valve.

        Parameters
        ----------
        valve_id : `str`
            ID of the valve for which the status is set.
        status : `int`
            New status of the valve -- either open or closed.
            Must be one of the following:

                - EN_CLOSED       = 0
                - EN_OPEN         = 1
        """
        valve_idx = self._epanet_api.getLinkValveNameID().index(valve_id)
        valve_link_idx = self._epanet_api.getLinkValveIndex()[valve_idx]
        self._epanet_api.setLinkStatus(valve_link_idx, status)

    def set_node_quality_source_value(self, node_id:str, pattern_id:str, qual_value:float) -> None:
        """
        Sets the quality source at a particular node to a specific value -- e.g. 
        setting the chlorine concentration injection to a specified value.

        Parameters
        ----------
        node_id : `str`
            ID of the node.
        pattern_id : `str`
            ID of the quality pattern at the specific node.
        qual_value : `float`
            New quality source value.
        """
        node_idx = self._epanet_api.getNodeIndex(node_id)
        pattern_idx = self._epanet_api.getPatternIndex(pattern_id)
        self._epanet_api.setNodeSourceQuality(node_idx, 1)
        self._epanet_api.setPattern(pattern_idx, np.array([qual_value]))

    @abstractmethod
    def step(self, scada_data:ScadaData) -> None:
        """
        Implements the control algorithm -- i.e. mapping of sensor reading to actions.
        
        Parameters
        ----------
        scada_data : :class:`~epyt_flow.simulation.scada.scada_data.ScadaData`
            Sensor readings.
        """
        raise NotImplementedError()
