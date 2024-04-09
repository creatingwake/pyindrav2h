import logging

from .connection import Connection
from . import V2H_MODES

_LOGGER = logging.getLogger(__name__)

class v2hDevice:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self.data = {}
        self.stats = {}
        self.active = {}

    async def refresh_device_info(self):
        d = await self.connection.get("/authorize/validate")
        _LOGGER.debug(f"/validate RESPONSE: {d}")
        self.data = d
    
    async def __set_mode(self, mode, payload=None):
        s = await self.connection.post("/transactions/" + self.id + 
                                        "/interrupt/" + mode,
                                        payload)
        return s

    async def load_match(self):
        return await self.__set_mode(V2H_MODES['LOAD_MATCH'])

    async def idle(self):
        return await self.__set_mode(V2H_MODES['IDLE'])       

    async def schedule(self):
        return await self.__set_mode(V2H_MODES['SCHEDULE'])
    
    async def select_charger_mode(self, mode, rate=None):
        if mode in {'CHARGE', 'DISCHARGE'}:
            rate = {"limitAmps": 25} # charge / discharge fixed at max rate for now
        return await self.__set_mode(V2H_MODES[mode], rate)

    async def refresh_stats(self):
        s = await self.connection.get("/telemetry/devices/" + self.serial + 
                                      "/latest")
        self.stats = s
        _LOGGER.debug(f"Stats: {s}")
        a = await self.connection.get("/transactions/" + self.serial + 
                                      "/00000000-0000-0000-0000-000000000000/active")
        _LOGGER.debug(f"/active RESPONSE: {a}")
        self.active = a
    
    @property
    def id(self):
        try:
            return self.active["id"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function id")
            return None

    @property
    def serial(self):
        try:
            return self.data["devices"][0]["deviceUID"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function serial")
            return None

    @property
    def lastOn(self):
        try:
            return self.data["lastOn"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function lastOn")
            return None
       
    @property
    def isActive(self):
        try:
            return self.data["devices"][0]["active"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function isActive")
            return None   

    @property
    def updateTime(self):
        try:
            return self.stats["time"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function updateTime")
            return None     

    @property
    def isBoosting(self):
        try:
            return self.stats["isBoosting"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function isBoosting")
            return None
        
    @property
    def mode(self):
        try:
            return self.stats["mode"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function mode")
            return None
        
    @property
    def state(self):
        try:
            return self.stats["state"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function state")
            return None

    @property
    def activeEnergyFromEv(self):
        try:
            return self.stats["data"]["activeEnergyFromEv"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function activeEnergyFromEv")
            return None

    @property
    def activeEnergyToEv(self):
        try:
            return self.stats["data"]["activeEnergyToEv"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function activeEnergyToEv")
            return None

    @property
    def powerToEv(self):
        try:
            return self.stats["data"]["powerToEv"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function powerToEv")
            return None

    @property
    def houseLoad(self):
        try:
            return self.stats["data"]["ctClamp"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function houseLoad")
            return None

    @property
    def current(self):
        try:
            return self.stats["data"]["current"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function current")
            return None

    @property
    def voltage(self):
        try:
            return self.stats["data"]["voltage"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function voltage")
            return None

    @property
    def freq(self):
        try:
            return self.stats["data"]["freq"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function freq")
            return None

    @property
    def temperature(self):
        try:
            return self.stats["data"]["temp"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function temperature")
            return None

    @property
    def soc(self):
        try:
            return self.stats["data"]["soc"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function soc")
            return None

    @property
    def isInterrupted(self):
        try:
            return self.active["isInterrupted"]
        except KeyError as e:
            _LOGGER.error(f"KeyError [{e}] in function isInterrupted")
            return None
    
    
    def showDevice(self):
        ret = ""
        
        ret = ret + "--- Device info ---\n"
        ret = ret + f"Device UID: {self.serial}\n"
        ret = ret + f"Last On date: {self.lastOn}\n"
        ret = ret + f"Device active: {self.isActive}"

        return ret

    def showStats(self):
        ret = ""

        ret = ret + "--- Statistics ---\n"
        ret = ret + f"Update time: {self.updateTime}\n"
        ret = ret + f"Boost mode on?: {self.isBoosting}\n"
        ret = ret + f"Mode: {self.mode}\n"
        ret = ret + f"State: {self.state}\n"
        ret = ret + f"Active Energy from EV: {self.activeEnergyFromEv}\n"
        ret = ret + f"Active Energy to EV: {self.activeEnergyToEv}\n"
        ret = ret + f"EV load + / discharge - (W): {self.powerToEv}\n"
        ret = ret + f"House load + / Export - (W): {self.houseLoad}\n"
        ret = ret + f"Current: {self.current}\n"
        ret = ret + f"Voltage: {self.voltage}\n"
        ret = ret + f"Frequency: {self.freq}\n"
        ret = ret + f"Temperature: {self.temperature}\n"
        ret = ret + f"Vehicle SoC: {self.soc}\n"
        ret = ret + f"Schedule active?: {not self.isInterrupted}\n"
        return ret

    def showAll(self):
        return self.showDevice() + "\n\n" + self.showStats()
  
    def getDevices(self):
        return self.data["devices"]