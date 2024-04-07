
# pyindrav2h

A basic API client and example CLI to interact with Indra V2H Chargers.  Required by Home Assistant.

This is a very early Alpha release, and functionality may change very rapidly.

NOTE: Indra Renewable Technologies Limited are aware of this integration.  However, this is an unofficial integration and Indra are not able to provide support for direct API integrations.  The Indra API will likely change in future which may result in functionality provided by this integration failing at any time.



## Installation

Install pyindrav2h with pip.  Using venv is recommended.

```bash
  pip install pyindrav2h
```
to update pyindrav2h
```bash
  pip install pyindrav2h -U
```
On installation a CLI will become available: ```indracli```
## Usage/Examples

### CLI

```bash
usage: indracli [-h] [-u EMAIL] [-p PASSWORD] [-d] {statistics,device,all,loadmatch,idle,exportmatch,charge,discharge,schedule} ...

Indra V2H CLI

positional arguments:
  {statistics,device,all,loadmatch,idle,exportmatch,charge,discharge,schedule}
    statistics          show device statistics
    device              show device info
    all                 show all info
    loadmatch           set mode to load matching
    idle                set mode to IDLE
    exportmatch         set mode to export matching
    charge              set mode to CHARGE
    discharge           set mode to discharge
    schedule            return to scheuduled mode

options:
  -h, --help            show this help message and exit
  -u EMAIL, --email EMAIL
  -p PASSWORD, --password PASSWORD
  -d, --debug
```

It is possible to provide a configuration file to provide Indra Smart Portal credentials.  If no username/email or password is provided it will be retrieved from ```./.indra.cfg``` or ```~/.indra.cfg```

#### Example .indra.cfg Configuration file
```
[indra-account]
email=useremail@email.com
password=yourindrapassword
```

### Library Usage

Intended for use with Indra V2H Home Assistant integration.
Documentation to follow.

## Support

This is a community project that lacks formal support.


For support from the community please join the Indra V2H trial support community: https://indra.v2h.zendesk.com/hc/en-gb/community/topics



For bugs or feature requests please create a GitHub Issue: https://github.com/creatingwake/pyindrav2h/issues

---
#### NOTE: Please do not contact Indra Support.  Indra are unable to assist with unofficial API integrations.


## Acknowledgements

 - [trizmark](https://github.com/trizmark) for help with home assistant API integration examples


