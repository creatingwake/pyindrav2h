import logging
from .connection import Connection
from .v2hdevice import v2hDevice

_LOGGER = logging.getLogger(__name__)

class v2hSchedule:
    """
    Support for preset schedules.

    As of June 2026 the Indra API supports schedules at the
    `/trials/v2h/schedules` endpoint. Info on each preset is returned as a JSON
    object with the following properties:

      - id: a unique identifier for the preset
      - name: a human-readable name
      - description: a few sentences describing the modes and times of
        the preset.
      - rules: a list of objects describing each different window of
        operation, one entry per window:
        - start: the start time in HH:MM format.
        - end: the end time in HH:MM format.
        - mode: the charger mode (one of the V2H_MODES keys).
        - recurrance: how often the rule runs ('MO,TU,WE,TH,FR,SA,SU') is
          all week.

    The available presets are expected to change infrequently, and can be
    downloaded and cached using v2hSchedule.refresh_schedules().

    The available presets are accessible through vh2Schedule.presets,
    which returns a dictionary keyed by the schedule IDs, one entry for
    each schedule as a dictionary in the format listed above.

    To make a V2H device use a preset schedule, call
    `v2hSchedule.set_schedule(device, schedule), with device being
    a v2hDevice instance and schedule being the ID of one of the
    available presets. An error occurs if a preset is asked for which
    does not exist in the local cache. It may be prudent to call
    `refresh_schedules` before calling `set_schedule` in case the available
    list of schedules has changed since it was last fetched.
    """
    def __init__(
        self, connection: Connection
    ) -> None:
        self._connection = connection
        self._preset_schedules = None

    async def refresh_schedules(self):
        scheds = await self._connection.get('/trials/v2h/schedules/presets/')
        self._preset_schedules = scheds

    async def get_schedule(self, device):
        """
        Get the currently-active schedule of a charger.

        Parameters
        ----------
        device: a v2hDevice instance of a charger device.

        Returns
        -------

        The ID of the currently-active schedule. This can be used as a
        key to v2hSchedule.presets to retrieve the full schedule details.
        """
        active = await self._connection.get(
            f'/trials/v2h/devices/{device.serial}/schedules/active'
        )
        active_schedule = self.presets[active['presetSourceId']]
        return active_schedule

    async def set_schedule(self, device, schedule):
        """
        Set the active schedule of a device.

        Parameters
        ----------
        device:   a v2hDevice instance of a charger device.
        schedule: the ID of one of the schedules in v2hSchedule.presets
        """
        if schedule not in self.presets:
            raise ValueError(
                'schedule must be one of the IDs in v2hSchedule.presets.\n'
                'Use v2hSchedule.refresh_schedules() to get an up-to-date list '
                'of available presets.'
            )
        resp = await self._connection.post(
            '/trials/v2h/schedules',
            {'deviceUid': device.serial, 'presetSourceID': schedule}
        )
        return resp

    @property
    def presets(self):
        return {schedule['id']: schedule for schedule in self._preset_schedules}
