/*
 * ECOS firmware scaffold — P02 (soil-probe)
 * Verify-only scaffold: satisfies the IDS gate that a matching PROJECT_CODE
 * exists. Implement readSensors()/applyControl() per config/hardware-manifests.json
 * and packages/hardware-sdk TelemetrySchema before a real build.
 */
#define PROJECT_CODE "P02"
#define DEVICE_TYPE "soil-probe"
#define FIRMWARE_VERSION "v0.1.0-scaffold"

// Telemetry: ecos/P02/<deviceId>/telemetry   Control: ecos/P02/<deviceId>/control
// See firmware/esp32-template/ecos_template.ino for the full template.
