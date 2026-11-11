# roBa / Tempest 34 — XIAO nRF52840 Plus

Firmware adaptation of [kumamuk-git/zmk-config-roBa](https://github.com/kumamuk-git/zmk-config-roBa) for the reversible roBa / Tempest PCB: 17 keys per half, MID + FAR thumbs, no encoder, and optional PMW3610 modules on either or both halves. The **right half is always the central**: connect it to the host for USB, Bluetooth, and ZMK Studio.

The original `roBa` shield and personal keymap remain available in their original files. The default build matrix now targets `roba_tempest_34`.

## Build and choose firmware

Push this branch or run **Build roBa Tempest 34** from GitHub Actions. Builds run on isolated GitHub-hosted runners using the ZMK 3.5 build container. No local Docker/Rancher installation is needed. Each artifact contains its UF2, resolved dependency manifest, commit identifier, and generated Kconfig/devicetree diagnostics. Successful keyboard builds also contain `configuration-checks.json`.

| Hardware | Right half image | Left half image |
|---|---|---|
| Right trackball only | `rt34-right-trackball.uf2` | `rt34-left-keyboard.uf2` |
| Left trackball only | `rt34-right-keyboard.uf2` | `rt34-left-trackball.uf2` |
| Two trackballs | `rt34-right-trackball.uf2` | `rt34-left-trackball.uf2` |
| Keyboard only | `rt34-right-keyboard.uf2` | `rt34-left-keyboard.uf2` |

Flash a trackball image only on a half with a sensor installed. The central accepts left-side sensor events through a `zmk,input-split` proxy, including in its keyboard-only image. `rt34-settings-reset.uf2` is a recovery image that clears saved settings/pairings; flash normal firmware again afterwards. Reset both halves' settings together when clearing split pairing.

## Hardware changes

- Matrix rows: D1/P0.03, D2/P0.28, D3/P0.29, D6/P1.11.
- Local matrix columns, outer to inner: D10/P1.15, D9/P1.14, D8/P1.13, D7/P1.12, **D11/P0.15**. Both halves scan the same nets; the right transform adds a column offset of five.
- Sensor: SCK=D5/P0.05, shared MOSI/MISO SDIO=D4/P0.04, **CS=D12/P0.19**, MOTION=D0/P0.02. The original roBa three-wire driver protocol is retained.
- NFC pins P0.09/P0.10 remain unused. No encoder driver/nodes are enabled.
- Plus battery sensing: ADC AIN7/P0.31 with P0.14 open-drain, active-low enable. Official Plus schematic R16=1 MΩ, R17=499 kΩ gives `output-ohms=499000`, `full-ohms=1499000`, overriding the base board's 510 kΩ divider.
- The existing `seeeduino_xiao_ble` target supplies nRF52840, stock XIAO UF2 partitioning, USB and BLE. External QSPI flash is unused and disabled; firmware/settings use internal flash. UART, I2C0 and SPI2 are disabled to avoid matrix/sensor pin conflicts.
- External reset is a hardware connection and requires no special firmware behavior. Battery-negative switching remains hardware controlled.

## Keymap and pointing

`config/roba_tempest_34.keymap` is a starting 34-key map retaining roBa's QWERTY and home-row modifiers, with remapped thumb/layer controls. Every layer has exactly 34 entries: BASE, NUM, SYM, NAV, MOUSE, SCROLL, SYS. Hold Z for NUM and slash for SYM. Thumbs, from left outer to right outer, are BACKSPACE/NAV, SPACE/SCROLL, ENTER/SYS, DELETE/MOUSE (tap/hold).

Moving either sensor temporarily activates MOUSE for 700 ms on the **central**. SCROLL maps either sensor's XY movement to wheel events there, so peripheral sensing does not require a peripheral keymap or synchronized layer state. Sensor rotation inherits roBa's 180° default and needs physical verification for the chosen housing and half.

Studio is enabled on the right over USB with locking enabled. Hold right FAR/ENTER for SYS, then press left C to unlock Studio. SYS also provides Bluetooth profile selection/clearing and bootloader/reset controls. The `roba_tempest_34-layout.dtsi` physical layout is generated from the PCB geometry snapshot, including splay and MID/FAR thumb angles.

## Dependency compatibility and checks

ZMK is pinned to the immutable `v0.3.0` release; the sensor driver is pinned to commit `5e04553ab803d24405bd45621a41310ea3050e59`. Actions applies `patches/pmw3610-peripheral.patch` to that exact driver revision. It bypasses keymap-dependent mode selection and behavior invocation on a peripheral, which has no host keymap/behavior queue. Layer-dependent pointing is handled centrally instead. The patch is checked before application and does not change the sensor bus implementation or ZMK core.

Run configuration checks without a toolchain:

```sh
python3 scripts/check_config.py
python3 scripts/generate_layout.py --check
```

From the PCB workspace, compare against the actual electrical and geometry sources:

```sh
python3 firmware/scripts/check_config.py --pcb-root .
```

Actions additionally audits **compiled** GPIO assignments, matrix/physical/keymap counts, central/peripheral roles, optional sensor/listener/proxy nodes, battery divider, Studio locking, and disabled conflicting peripherals. It builds all four normal images plus settings reset. Resolved West revisions are recorded with every build; transitive Zephyr dependencies still follow the official stable manifest.

A passing build is not a hardware test. Verify the stock Plus bootloader, both halves' key order, USB/BLE pairing, battery voltage/percentage, sensor direction/scrolling, sleep current, and optional dual pointing on real hardware before treating these images as validated for daily use. No firmware is flashed automatically.
