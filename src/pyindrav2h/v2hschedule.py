import logging
from textwrap import dedent
from .connection import Connection

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

    The available presets are expected to change infrequently and can
    be downloaded and cached using v2hSchedule.refresh_schedules().
    Each time a get or set of the current schedule is performed, the
    latest available list of presets is retrived automatically too.

    The available presets are accessible through vh2Schedule.presets,
    which returns a dictionary keyed by the schedule IDs, one entry for
    each schedule as a dictionary in the format listed above.

    To make a V2H device use a preset schedule, call
    `v2hSchedule.set_schedule(device, schedule_id), with device being
    a v2hDevice instance and schedule_id being the ID of one of the
    available presets. An error occurs if a preset is asked for which
    does not exist remotely, noting that the list of available presets
    on Indra's servers may have changed since the last time the local
    client retrived them before the `set_schedule` call.
    """
    def __init__(
        self, connection: Connection
    ) -> None:
        self._connection = connection
        self._preset_schedules = {}

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
        if active['presetSourceId'] not in self.presets:
            # New schedules added and set since last refresh.
            await self.refresh_schedules()
        active_schedule = self.presets[active['presetSourceId']]
        return active_schedule

    async def set_schedule(self, device, schedule_id):
        """
        Set the active schedule of a device.

        Parameters
        ----------
        device:   a v2hDevice instance of a charger device.
        schedule: the ID of one of the schedules in v2hSchedule.presets
        """
        await self.refresh_schedules()
        if schedule_id not in self.presets:
            raise ValueError(
                'schedule must be one of the IDs in v2hSchedule.presets.\n'
                'Use v2hSchedule.refresh_schedules() to get an up-to-date list '
                'of available presets.'
            )
        resp = await self._connection.post(
            '/trials/v2h/schedules',
            {'deviceUid': device.serial, 'presetSourceID': schedule_id}
        )
        return resp

    @property
    def presets(self):
        return {schedule['id']: schedule for schedule in self._preset_schedules}

    def describe_schedule(self, schedule_id):
        """
        Return  details of the preset schedule specified by schedule_id
        as a multi-line string for printing.
        """
        schedule = self.presets[schedule_id]
        output = "\n".join([
            f"Schedule ID: {schedule_id}",
            f"Name: {schedule["name"]}",
            f"Description: {schedule["description"]}",
            "Rules:\n"
        ])
        for rule in schedule["rules"]:
            output += dedent(
                f"""\
                - Start time: {rule["start"]}
                  End time: {rule["end"]}
                  Mode: {rule["mode"]}
                  Recurrence: {rule["recurrence"]}
                """
            )
        return output
