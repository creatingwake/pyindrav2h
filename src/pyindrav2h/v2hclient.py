import logging
from .connection import Connection
from .v2hdevice import v2hDevice

_LOGGER = logging.getLogger(__name__)

class v2hClient:
    def __init__(
        self, connection: Connection
    ) -> None:
        self._connection = connection
        self._device = None

    async def refresh(self):
        if self._device is None:
            self._device = v2hDevice(self._connection)

        await self._device.refresh_device_info()
        await self._device.refresh_stats()

    @property
    def device(self):
        return self._device