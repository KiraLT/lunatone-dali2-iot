# CHANGELOG


## v3.0.0 (2026-11-08)

### Features

- Support the gateway firmware 1.18.7 API
  ([`4f0593e`](https://github.com/KiraLT/lunatone-dali2-iot/commit/4f0593e18432209453707edadb10f9ebb9d0c04e))

Update openapi.json to the spec served by firmware v1.18.7/1.4.6 and add everything the clients were
  missing:

- Device scenes, energy reporting and diagnostics endpoints - Line status and raw 16-bit and 24-bit
  DALI frames - Periodic status query settings per line - Event trigger actions - Sensor delete
  endpoints and typed Sensor responses - Line query parameters on group and broadcast control and
  bulk deletes - The one-off *WithFade control fields, dimUp and dimDown, and the colour activate
  flag - New fields on Device, Info, Scan, Settings and EthernetSettings, and the new enum values

ControlData.fade_time is now documented as the stored device setting it is. The email endpoints
  answer 404 on 1.18.7, so those methods emit a DeprecationWarning. The link endpoints stay: the
  gateway still serves them although the spec no longer lists them.

BREAKING CHANGE: list_sensors() and get_sensor() return Sensor models instead of raw dicts.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

### Breaking Changes

- List_sensors() and get_sensor() return Sensor models instead of raw dicts.


## v2.1.0 (2026-05-05)


## v2.0.0 (2026-05-05)

### Features

- Websocket support
  ([`8a90a57`](https://github.com/KiraLT/lunatone-dali2-iot/commit/8a90a57ab981741f2f7f7ac7f1e2603b1d1c3a43))


## v1.1.0 (2025-02-15)

### Chores

- Update git to correct version
  ([`81b97dc`](https://github.com/KiraLT/lunatone-dali2-iot/commit/81b97dc1c3429f9e83ccbb0021b577e062d6c46b))

### Features

- Rewrite and simplify API
  ([`8a93d16`](https://github.com/KiraLT/lunatone-dali2-iot/commit/8a93d16a8db31c44e5d899a5471d1c0e286b45cf))

BREAKING CHANGE: API restructure

- Simplify generate api modules
  ([`d2da0ba`](https://github.com/KiraLT/lunatone-dali2-iot/commit/d2da0ba6759eac2eedb486f8ed789e2c84a23667))

### Breaking Changes

- Api restructure


## v0.1.0 (2025-02-13)

### Chores

- Add build step to publish workflow and remove build command from pyproject.toml
  ([`db365d4`](https://github.com/KiraLT/lunatone-dali2-iot/commit/db365d4d8976f4e2fba5021c463ed18d28706c69))

- Add workflows again
  ([`c7e5859`](https://github.com/KiraLT/lunatone-dali2-iot/commit/c7e5859378b63c365add7377f5cd05ebe9dd7c26))

- File rename
  ([`8f51a2f`](https://github.com/KiraLT/lunatone-dali2-iot/commit/8f51a2fda3e11d629d90a4fcc45fd27735ca8cf5))

- Fix publish workflow versions
  ([`498f069`](https://github.com/KiraLT/lunatone-dali2-iot/commit/498f0694bf4383fd356969b75f1006132adcff83))

- Remove workflows
  ([`d785515`](https://github.com/KiraLT/lunatone-dali2-iot/commit/d785515d2fc2f2003c6e52f3308ba6ababf34dc4))

- Update GitHub Actions to latest versions for publishing docs
  ([`15c8731`](https://github.com/KiraLT/lunatone-dali2-iot/commit/15c873191eeb693e279aae2b8c84a19ee73fe472))

- Update issue templates
  ([`b7ee647`](https://github.com/KiraLT/lunatone-dali2-iot/commit/b7ee64725c647d7eacc2d250925d037a2eb2caea))

### Features

- Initial commit
  ([`cedebfc`](https://github.com/KiraLT/lunatone-dali2-iot/commit/cedebfcab52276f841b44aa99b61e4664deba7df))
