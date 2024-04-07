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
        self.active = a

    @property
    def id(self):
        return self.active["id"]

    @property
    def serial(self):
        return self.data["devices"][0]["deviceUID"]

    @property
    def lastOn(self):
        return self.data["lastOn"]

    @property
    def isActive(self):
        return self.data["devices"][0]["active"]

    @property
    def updateTime(self):
        return self.stats["time"]

    @property
    def isBoosting(self):
        return self.stats["isBoosting"]

    @property
    def mode(self):
        return self.stats["mode"]
    
    @property
    def state(self):
        return self.stats["state"]

    @property
    def activeEnergyFromEv(self):
        return self.stats["data"]["activeEnergyFromEv"]

    @property
    def activeEnergyToEv(self):
        return self.stats["data"]["activeEnergyToEv"]

    @property
    def powerToEv(self):
        return self.stats["data"]["powerToEv"]

    @property
    def houseLoad(self):
        return self.stats["data"]["ctClamp"]

    @property
    def current(self):
        return self.stats["data"]["current"]

    @property
    def voltage(self):
        return self.stats["data"]["voltage"]

    @property
    def freq(self):
        return self.stats["data"]["freq"]

    @property
    def temperature(self):
        return self.stats["data"]["temp"]

    @property
    def soc(self):
        return self.stats["data"]["soc"]

    @property
    def isInterrupted(self):
        return self.active["isInterrupted"]
    
    
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
