# roBa / Tempest 34 — XIAO nRF52840 Plus

This version adapts [kumamuk-git's roBa firmware](https://github.com/kumamuk-git/zmk-config-roBa) to our reversible **34-key roBa / Tempest PCB**, with a **Seeed XIAO nRF52840 Plus** on each half, two thumb keys per half, no encoders, and optional PMW3610 trackballs.

The **right half is always the central**. Connect the right half to the host for USB, Bluetooth and ZMK Studio. The left half is the wireless peripheral, even when the only trackball is on the left.

Development branch: [`codex/roba-tempest-34-xiao-plus`](https://github.com/pageegap/zmk-config-roBa/tree/codex/roba-tempest-34-xiao-plus). The original [roBa shield](boards/shields/roBa) and [personal keymap](config/roBa.keymap) are retained separately; the default build matrix targets the new `roba_tempest_34` shield.

## Contents

- [Changes from the original roBa](#changes-from-the-original-roba)
- [Build and choose firmware](#build-and-choose-firmware)
- [Configuration file guide](#configuration-file-guide)
- [Hardware and pin configuration](#hardware-and-pin-configuration)
- [Keymap, layers and controls](#keymap-layers-and-controls)
- [Trackball configuration](#trackball-configuration)
- [Bluetooth, battery and Studio settings](#bluetooth-battery-and-studio-settings)
- [Dependencies and driver compatibility](#dependencies-and-driver-compatibility)
- [Checks and hardware validation](#checks-and-hardware-validation)

## Changes from the original roBa

| Area | Changes in this version |
|---|---|
| Controller | Uses the XIAO **nRF52840 Plus** extra GPIO pads. It retains the nRF52840 processor and the existing `seeeduino_xiao_ble` build target, with Plus-specific overrides. |
| Keyboard layout | 17 keys per half: 15 finger keys and Tempest **MID + FAR** thumbs. The NEAR thumb is omitted. Matrix transforms, keymap positions and Studio geometry now contain 34 keys. |
| Matrix | Moves the inner column from P0.10/NFC2 to **D11/P0.15**. Both halves use the same local 4 × 5 scan wiring and `col2row` diodes. |
| Sensor wiring | Moves PMW3610 chip-select from P0.09/NFC1 to **D12/P0.19**. The roBa shared SDIO interface is retained. |
| NFC and encoders | P0.09/P0.10 are unused; NFC pins are not repurposed as GPIO. Encoder nodes and bindings are absent from the new shield/keymap. |
| Battery measurement | Corrects the inherited 510 kΩ divider setting to the Plus schematic's **1 MΩ + 499 kΩ** divider. |
| Optional pointing | Adds right-only, left-only, dual-trackball and keyboard-only combinations. Left-side motion is forwarded over the wireless split link. |
| Pointer layers | Processes automatic mouse-layer activation and scrolling on the central for both sensors, rather than relying on a peripheral keymap. |
| External flash | Disables the unused QSPI controller **and both inherited flash-chip nodes**, including in the recovery image. Firmware/settings use internal flash. |
| Studio | Enables USB Studio on the right with locking and a keymap unlock action. |
| Builds | Pins ZMK and the sensor driver, applies a small peripheral compatibility patch, and adds isolated Actions builds plus compiled hardware and UF2 checks. |

The PCB's exposed BAT+/RESET wire links and component-side-down module mounting do not need special firmware behavior. Reset remains a hardware signal. The battery-negative power switch is hardware controlled: USB can power the MCU while the battery is disconnected; battery charging requires its negative connection to be switched ON.

## Build and choose firmware

Push changes to this branch, or open **Actions → Build roBa Tempest 34 → Run workflow** and select the branch. The [workflow](.github/workflows/build.yml) uses isolated GitHub-hosted runners and the `zmkfirmware/zmk-build-arm:3.5` container. No local Docker/Rancher installation is required.

Download artifacts from a **successful** run. Choose the pair matching the installed sensors:

| Installed hardware | Right half image | Left half image |
|---|---|---|
| Right trackball only | `rt34-right-trackball.uf2` | `rt34-left-keyboard.uf2` |
| Left trackball only | `rt34-right-keyboard.uf2` | `rt34-left-trackball.uf2` |
| Two trackballs | `rt34-right-trackball.uf2` | `rt34-left-trackball.uf2` |
| Keyboard only | `rt34-right-keyboard.uf2` | `rt34-left-keyboard.uf2` |

A right-keyboard image still receives left-trackball events through the split proxy. Select a trackball image only on a half with a sensor installed.

Each artifact contains:

- Its named `.uf2` image.
- `config-commit.txt`: the exact firmware configuration commit.
- `resolved-west.yml`: exact revisions of active build dependencies.
- `zephyr.config` and `zephyr.dts`: the compiled configuration and hardware description.
- `uf2-checks.json`: binary hash, MCU family and application flash-bound checks.
- `configuration-checks.json`: compiled hardware checks for the four normal keyboard images.

### Flashing and recovery

1. Double-tap the reset button on the half being flashed to enter its stock XIAO UF2 bootloader.
2. Copy that half's selected `.uf2` to its bootloader drive. Repeat for the other half.
3. Connect the **right half** to the host and test all keys over USB before testing Bluetooth and pointing.
4. To use Studio, keep the right half connected over USB and unlock it as described below.

`rt34-settings-reset.uf2` is a separate recovery image that clears saved settings/pairings. When clearing split pairing, reset the settings on both halves, then flash their normal images again. Use recovery deliberately; it is not the normal firmware image.

## Configuration file guide

Paths below are relative to this firmware repository.

| File | Purpose |
|---|---|
| [build.yaml](build.yaml) | Build target, shield, snippets and artifact name for each image. |
| [config/west.yml](config/west.yml) | ZMK version and sensor-driver revision. |
| [config/roba_tempest_34.keymap](config/roba_tempest_34.keymap) | Key bindings, layers, combos and home-row hold-tap settings. |
| [config/roba_tempest_34.conf](config/roba_tempest_34.conf) | Settings shared by both halves: BLE, pointing, battery reporting and disabled encoders/NFC GPIO use. |
| [config/roba_tempest_34_right.conf](config/roba_tempest_34_right.conf) | Central battery proxy/fetching and Studio settings. |
| [roba_tempest_34.dtsi](boards/shields/roba_tempest_34/roba_tempest_34.dtsi) | Shared matrix, GPIOs, battery divider, sensor bus and disabled peripherals. |
| [Right overlay](boards/shields/roba_tempest_34/roba_tempest_34_right.overlay) | Right column offset, local/remote pointer processing, mouse timeout and scroll scaling. |
| [Left overlay](boards/shields/roba_tempest_34/roba_tempest_34_left.overlay) | Shared hardware inclusion for the peripheral. |
| [Central trackball settings](snippets/rt34-trackball-central/rt34-trackball-central.conf) | Right sensor sensitivity, orientation and power-related settings. |
| [Peripheral trackball settings](snippets/rt34-trackball-peripheral/rt34-trackball-peripheral.conf) | Left sensor sensitivity, orientation and power-related settings. |
| [config/settings_reset.overlay](config/settings_reset.overlay) | Disables unused external flash in the recovery image. |
| [Kconfig.defconfig](boards/shields/roba_tempest_34/Kconfig.defconfig) | Keyboard name and fixed right-central/left-peripheral roles. |
| [hardware/pcb-pinout.json](hardware/pcb-pinout.json) | PCB electrical snapshot used by checks. |
| [hardware/layout-points.json](hardware/layout-points.json) | PCB geometry snapshot used to generate Studio's physical layout. |

The `rt34-trackball-central` and `rt34-trackball-peripheral` snippets enable the sensor only for the appropriate image. They also select the local listener or peripheral input-forwarding node. The right images use `studio-rpc-usb-uart` for Studio's USB transport.

## Hardware and pin configuration

These assignments describe the PCB wiring; they are not arbitrary user preferences.

| Function | XIAO pad | nRF52840 GPIO |
|---|---|---|
| Top row | D1 | P0.03 |
| Home row | D2 | P0.28 |
| Bottom row | D3 | P0.29 |
| Thumb row | D6 | P1.11 |
| Pinky column | D10 | P1.15 |
| Ring column | D9 | P1.14 |
| Middle column | D8 | P1.13 |
| Index column | D7 | P1.12 |
| Inner column | D11 | P0.15 |
| Sensor SCLK | D5 | P0.05 |
| Sensor SDIO, shared MOSI/MISO | D4 | P0.04 |
| Sensor chip-select, active low | D12 | P0.19 |
| Sensor MOTION, active low with pull-up | D0 | P0.02 |
| Battery ADC, sensing only | D16 / AIN7 | P0.31 |
| Battery measurement enable, active-low open-drain | Internal module connection | P0.14 |

The sensor bus uses `spi-max-frequency = <2000000>` (2 MHz). MOSI and MISO deliberately use the **same** SDIO pin, matching the roBa driver and sensor connection. UART, I2C0 and SPI2 are disabled to avoid conflicts.

Each half scans four rows and five columns, but uses only 17 switch positions. The shared transform has four rows and ten columns: left columns 0–4 and right columns 5–9. The right overlay sets `col-offset = <5>`; the left uses zero. Only the index and inner columns have thumb-row switches.

### Battery calibration

The Plus overrides in the shared `.dtsi` are:

```dts
&vbatt {
    io-channels = <&adc 7>;
    power-gpios = <&gpio0 14 (GPIO_OPEN_DRAIN | GPIO_ACTIVE_LOW)>;
    output-ohms = <499000>;
    full-ohms = <1499000>;
};
```

`output-ohms` is the lower divider resistance; `full-ohms` is the total series resistance. These values follow the official Plus schematic's R16=1 MΩ and R17=499 kΩ. P0.14 must sink current to enable measurement, hence open-drain and active-low. D16/P0.31 is a measurement input, **not VBAT power**. Change these values only to match a verified hardware revision, and update the hardware snapshot/audits with it.

## Keymap, layers and controls

### Positions and layer indices

The order of bindings in every layer is:

```text
Left: outer → inner        Right: inner → outer
 0   1   2   3   4           5   6   7   8   9
10  11  12  13  14          15  16  17  18  19
20  21  22  23  24          25  26  27  28  29
            30  31         32  33
          MID  FAR        FAR  MID
```

| Index | Layer | Default access/function |
|---|---|---|
| 0 | BASE | QWERTY with home-row modifiers. |
| 1 | NUM | Hold Z; numbers and additional shortcuts. |
| 2 | SYM | Hold slash; symbols. |
| 3 | NAV | Hold left MID/Backspace; navigation, media and mouse controls. |
| 4 | MOUSE | Hold right MID/Delete, or temporarily activate by moving either sensor. |
| 5 | SCROLL | Hold left FAR/Space; convert either sensor's motion to wheel events. |
| 6 | SYS | Hold right FAR/Enter; Bluetooth profiles, Studio unlock, reset and bootloader controls. |

Thumb bindings are tap/hold: **Backspace/NAV**, **Space/SCROLL**, **Enter/SYS**, **Delete/MOUSE**, in the position order 30–33 above. Transparent entries fall through to lower active layers.

Keep **34 bindings per layer**. If changing layer order or indices, also update the keymap's layer references and both listeners' MOUSE/SCROLL references in the right overlay. The checks currently expect the seven named layers shown above.

### Home-row modifiers and combos

A/S/D/F hold Left GUI/Alt/Ctrl/Shift; J/K/L/semicolon hold Right Shift/Ctrl/Alt/GUI. Their hold-tap nodes are `ht_left` and `ht_right` in the keymap.

| Parameter | Current value | Purpose |
|---|---|---|
| `flavor` | `tap-preferred` | Hold-tap decision policy. |
| `tapping-term-ms` | `200` | Timing window in milliseconds. |
| `quick-tap-ms` | `160` | Quick repeated-tap window. |
| `require-prior-idle-ms` | `150` | Prior typing activity affects hold eligibility. |
| `hold-trigger-key-positions` | Opposite hand + positions 30–33 | Positions used by positional hold-tap. |
| `hold-trigger-on-release` | Present | Evaluate the positional trigger on release. |

These settings apply to the two custom home-row behaviors. The thumb/Z/slash layer taps use ZMK's separate `&lt` behavior; editing home-row timings does not automatically change `&lt` timings.

Default combos are positions 11+12 for Tab, 12+13 for Shift+Tab, and 6+7 for Escape. Escape has an explicit 50 ms combo timeout. Edit the combo nodes to change their bindings, positions or timeouts.

### SYS and Studio

Hold right FAR/Enter for SYS, then press:

| Position / BASE key | SYS action |
|---|---|
| 1–4 / W E R T | Select Bluetooth profiles 3, 2, 1, 0 respectively. |
| 5–8 / Y U I O | Select Bluetooth profiles 0, 1, 2, 3 respectively. |
| 22 / left C | Unlock ZMK Studio over the right half's USB connection. |
| 20 or 29 / Z or slash | Bootloader behavior. |
| 21 or 28 / X or period | Reset behavior. |
| 30 or 33 / Backspace or Delete thumb | Clear the selected Bluetooth profile's bond. |

## Trackball configuration

### Per-half sensor parameters

Edit the **central snippet's `.conf` for the right sensor** and the **peripheral snippet's `.conf` for the left sensor**. Both currently have these explicit defaults:

| Parameter | Configured value | Effect / supported values |
|---|---|---|
| `CONFIG_SPI` | `y` | Enable the sensor bus. |
| `CONFIG_INPUT` | `y` | Enable input events. |
| `CONFIG_PMW3610` | `y` | Enable the PMW3610 driver. |
| `CONFIG_PMW3610_CPI` | `1300` | Sensor sensitivity; driver range 200–3200, programmed in 200-CPI steps. See quantization note below. |
| `CONFIG_PMW3610_CPI_DIVIDOR` | `1` | Software movement divisor, range 1–100. Larger values reduce pointer movement. `DIVIDOR` is the upstream option's spelling. |
| `CONFIG_PMW3610_ORIENTATION_180` | `y` | Selects the 180° orientation. Other choices are `_0`, `_90`, `_270`; select exactly one. |
| `CONFIG_PMW3610_INVERT_X` | `n` | Optional horizontal inversion. `CONFIG_PMW3610_INVERT_Y` is also available and defaults off. |
| `CONFIG_PMW3610_RUN_DOWNSHIFT_TIME_MS` | `3264` | Requested idle time before RUN → REST1; allowed range 13–3264 ms. |
| `CONFIG_PMW3610_REST1_SAMPLE_TIME_MS` | `20` | REST1 sampling interval; range 10–2550 ms in 10 ms hardware steps. |
| `CONFIG_PMW3610_SMART_ALGORITHM` | `y` | Enable the driver's surface-coverage algorithm. |
| `CONFIG_PMW3610_POLLING_RATE_125_SW` | `y` | Select the driver's software 125 Hz mode. Alternatives are `_POLLING_RATE_125` and `_POLLING_RATE_250`; select one mode. Actual timing needs hardware measurement. |

**CPI quantization:** the pinned driver writes `CPI / 200` using integer division. The inherited setting of **1300 therefore programs 1200 CPI**. Use multiples of 200 when tuning to make the requested and programmed values agree.

For example, to tune the **left sensor**, edit [its snippet](snippets/rt34-trackball-peripheral/rt34-trackball-peripheral.conf):

```ini
CONFIG_PMW3610_CPI=1200
CONFIG_PMW3610_CPI_DIVIDOR=1
CONFIG_PMW3610_ORIENTATION_180=n
CONFIG_PMW3610_ORIENTATION_90=y
CONFIG_PMW3610_INVERT_X=y
```

This is an example, not a measured orientation for the final housing. Choose rotation/inversion after testing actual pointer direction. Right and left settings can differ without changing the split roles.

### Automatic mouse layer and scrolling

These are controlled in the **right overlay**, for both the local and forwarded sensor. The left peripheral sends motion without consulting a host keymap.

| Setting | Current value | Where to change it |
|---|---|---|
| Automatic mouse layer and timeout | `<&zip_temp_layer 4 700>` | Both `trackball_listener` and `remote_trackball_listener`: layer 4, 700 ms inactivity timeout. |
| Keys that do not cancel the temporary mouse layer | `<21 22 23 24 25 26 27 28>` | `&zip_temp_layer`'s `excluded-positions`; these are the mouse-button positions. |
| Scroll layer | `layers = <5>` | The `scroll` child of both listeners. |
| Motion-to-wheel mapping | `<&zip_xy_to_scroll_mapper>` | Maps Y to vertical wheel and X to horizontal wheel. |
| Scroll scaling | `<&zip_scroll_scaler 1 12>` | Multiply wheel movement by 1/12. A larger denominator slows scrolling. |
| Driver-level automatic mouse mode | `automouse-layer = <0>` | Shared sensor node: intentionally disabled. Leave at zero for this architecture. |

For a 1000 ms mouse timeout and slower scrolling, change the corresponding properties in **both** listeners:

```dts
input-processors = <&zip_temp_layer 4 1000>;
// Inside each listener's scroll child:
input-processors = <&zip_xy_to_scroll_mapper>, <&zip_scroll_scaler 1 18>;
```

Do not substitute `automouse-layer = <(-1)>`: an explicit negative devicetree cell can become an unsigned value and enable the driver's preprocessor-gated automouse code. Zero disables it reliably.

The driver's `CONFIG_PMW3610_AUTOMOUSE_TIMEOUT_MS`, `CONFIG_PMW3610_MOVEMENT_THRESHOLD`, `CONFIG_PMW3610_SCROLL_TICK`, `scroll-layers` and `snipe-layers` are **not the controls for this version's central input-processing path**. Use the listener settings above for mouse activation/scrolling, rather than re-enabling driver-level layer processing on the peripheral.

## Bluetooth, battery and Studio settings

| Parameter | Current value / scope | Meaning |
|---|---|---|
| `CONFIG_ZMK_BLE` | `y`, shared | Bluetooth operation and the wireless split. |
| `CONFIG_ZMK_POINTING` | `y`, shared | Pointer support, including mouse-button bindings and split input forwarding. |
| `CONFIG_ZMK_BATTERY_REPORTING` | `y`, shared | Battery reporting. |
| `CONFIG_NFCT_PINS_AS_GPIOS` | `n`, shared | NFC pins remain unused by this PCB. |
| `CONFIG_EC11` | `n`, shared | Encoders disabled. |
| `CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_FETCHING` | `y`, right | Fetch the left half's battery level. |
| `CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_PROXY` | `y`, right | Proxy peripheral battery information through the central. |
| `CONFIG_ZMK_STUDIO` | `y`, right | Studio support. |
| `CONFIG_ZMK_STUDIO_LOCKING` | `y`, right | Require the Studio unlock action. |
| `ZMK_KEYBOARD_NAME` | `roBa Tempest 34`, Kconfig default | Keyboard name, set in `Kconfig.defconfig`; an explicit `CONFIG_ZMK_KEYBOARD_NAME="..."` in the right `.conf` can override it. |
| `ZMK_SPLIT_ROLE_CENTRAL` | Right half | Fixed by the shield defaults; do not change only this flag to swap roles. Matrix offsets, transport/listeners, Studio and audits are coupled to the role selection. |

Studio edits key bindings at runtime. GPIOs, sensor orientation/CPI, battery-divider values, build snippets and listener processing are compile-time settings: edit the files and rebuild. Existing Studio-saved keymaps may need resetting/reapplying when changing the compiled keymap or physical layout; a rebuild alone is not a guarantee that saved runtime mappings are replaced.

The current compiled audits enforce the right-central role, hardware pinout, battery divider, disabled peripherals and right-side Studio/locking settings. If deliberately changing those baseline assumptions, update the corresponding checks as well. Ordinary sensor sensitivity/orientation and hold-tap tuning do not require changing the PCB snapshot.

## Dependencies and driver compatibility

[config/west.yml](config/west.yml) pins:

| Dependency | Revision |
|---|---|
| ZMK | `v0.3.0` |
| `kumamuk-git/zmk-pmw3610-driver` | `5e04553ab803d24405bd45621a41310ea3050e59` |
| Actions build container | `zmkfirmware/zmk-build-arm:3.5` |

Actions checks and applies [pmw3610-peripheral.patch](patches/pmw3610-peripheral.patch) to that exact sensor-driver revision. The patch bypasses keymap-dependent mode selection and behavior invocation on a peripheral, where the host keymap/behavior queue are absent. It preserves the sensor bus implementation and does not patch ZMK core.

To change the driver revision, update the manifest **and** the workflow's expected commit, review/regenerate the compatibility patch, and rebuild every variant. A ZMK upgrade also needs review of the container/Zephyr version, board target, devicetree bindings and driver compatibility. The frozen artifact manifest records the actual active dependency revisions; transitive dependencies follow the official ZMK manifest, and the container tag is a version tag rather than a digest pin.

## Checks and hardware validation

Run the configuration checks from this repository without a firmware toolchain:

```sh
python3 scripts/check_config.py
python3 scripts/generate_layout.py --check
```

To compare the snapshots with the PCB project, run this from the **parent PCB workspace**:

```sh
python3 firmware/scripts/check_config.py --pcb-root .
```

After deliberately updating [hardware/layout-points.json](hardware/layout-points.json), regenerate Studio geometry with `python3 scripts/generate_layout.py`. Do not hand-edit the generated [layout `.dtsi`](boards/shields/roba_tempest_34/roba_tempest_34-layout.dtsi). Keep the electrical snapshot, actual PCB and firmware GPIO definitions in agreement.

Actions performs:

1. Source checks for PCB GPIOs, 17+17 matrix mapping, generated layout, seven 34-entry keymap layers, combo/layer references and dependency pins.
2. Builds of the four normal images and settings-reset image.
3. Audits of the **compiled** matrix/GPIOs, layout/keymap counts, roles, optional sensor/listener/proxy nodes, battery divider, Studio settings and disabled conflicting peripherals.
4. UF2 structure, nRF52840 family-ID and application flash-bound checks. Payloads must remain within `0x27000`–`0xEC000` (upper bound exclusive), preserving reserved bootloader/settings regions.
5. Packaging of the images, checks and diagnostics described above.

Last verified firmware baseline: [commit a5f3e84](https://github.com/pageegap/zmk-config-roBa/commit/a5f3e849baf07dfbd94afd2fdfce44effee4862b), with [all five builds passing](https://github.com/pageegap/zmk-config-roBa/actions/runs/43070294686).

Hardware validation remains necessary: verify the stock Plus bootloader, every key and thumb position, USB/BLE pairing, battery voltage/percentage, sensor direction and scrolling, sleep current, and dual pointing with the chosen housings. Build checks establish configuration/binary consistency; the physical behavior still needs testing on the keyboard.
