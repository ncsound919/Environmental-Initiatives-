/*
 * ECOS firmware scaffold — P13 (turbine-controller)
 * Verify-only scaffold: satisfies the IDS gate that a matching PROJECT_CODE
 * exists. Implement readSensors()/applyControl() per config/hardware-manifests.json
 * and packages/hardware-sdk TelemetrySchema before a real build.
 */
#define PROJECT_CODE "P13"
#define DEVICE_TYPE "turbine-controller"
#define FIRMWARE_VERSION "v0.1.0-scaffold"

// Telemetry: ecos/P13/<deviceId>/telemetry   Control: ecos/P13/<deviceId>/control
// See firmware/esp32-template/ecos_template.ino for the full template.
