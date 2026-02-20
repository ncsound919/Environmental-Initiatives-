# ECOS ESP32 Firmware Template

## Level 3: Physical Twin - Hardware Integration

This directory contains firmware templates for ESP32 microcontrollers that power the physical devices across all 13 ECOS projects.

## ⚠️ Security Warning

**This template uses unencrypted MQTT for development purposes.** For production deployments:

1. **Enable TLS/SSL**: Use `WiFiClientSecure` instead of `WiFiClient`
2. **Use encrypted MQTT port**: Change from port 1883 to 8883
3. **Verify server certificates**: Load CA certificate and verify broker identity
4. **Secure WiFi credentials**: Store credentials in secure flash, not hardcoded
5. **Use device-specific passwords**: Generate unique MQTT credentials per device

See the "Production Security" section below for implementation details.

## Features

- ✅ **MQTT Communication**: Real-time telemetry and control via MQTT broker
- ✅ **WiFi Connectivity**: Automatic connection and reconnection
- ✅ **NTP Time Sync**: Accurate timestamps for all telemetry
- ✅ **Control Loop Latency Tracking**: Monitors <200ms requirement
- ✅ **Simulation Mode**: Test firmware without physical hardware
- ✅ **OTA Updates**: Ready for over-the-air firmware updates (via API endpoint)

## Hardware Requirements

- **ESP32 Development Board** (any variant)
- **Sensors** (project-specific)
- **Actuators/Relays** (project-specific)
- **Power Supply**: 5V USB or regulated 3.3V

## Software Requirements

- **Arduino IDE** 2.x or **PlatformIO**
- **ESP32 Board Support**: Install via Board Manager
- **Required Libraries**:
  - WiFi (built-in)
  - PubSubClient (MQTT client)
  - ArduinoJson (JSON parsing)

## Installation

### 1. Install Libraries

```bash
# Via Arduino Library Manager
- PubSubClient by Nick O'Leary
- ArduinoJson by Benoit Blanchon (v6+)

# Or via PlatformIO
pio lib install "knolleary/PubSubClient" "bblanchon/ArduinoJson"
```

### 2. Configure for Your Project

Edit `ecos_template.ino`:

```cpp
#define PROJECT_CODE "P08"  // Change to P01-P13
#define DEVICE_TYPE "bulb"  // e.g., sensor, pump, valve
#define FIRMWARE_VERSION "v1.0.0"

// WiFi credentials
const char* WIFI_SSID = "Your-WiFi-SSID";
const char* WIFI_PASSWORD = "your-password";

// MQTT broker (from .env)
const char* MQTT_BROKER = "192.168.1.100";  // Your MQTT broker IP
```

### 3. Customize Telemetry Collection

Implement `collectAndPublishTelemetry()` for your project:

```cpp
void collectAndPublishTelemetry() {
    // Example for Project #8 (Bulb)
    float voltage = analogRead(34) * (3.3 / 4095.0) * 4.0;
    publishTelemetry("voltage", voltage, "V");
    
    int thermalCycles = readEEPROM(0);  // Stored cycles
    publishTelemetry("thermal_cycles", thermalCycles, "count");
    
    float uptime = millis() / 3600000.0;  // hours
    publishTelemetry("uptime", uptime, "hours");
}
```

### 4. Flash to ESP32

```bash
# Via Arduino IDE
1. Select Board: ESP32 Dev Module
2. Select Port: /dev/ttyUSB0 (or COM3 on Windows)
3. Click Upload

# Via PlatformIO
pio run --target upload
```

## MQTT Topics

The firmware uses a standardized topic structure:

### Telemetry (Device → Cloud)
```
ecos/{PROJECT_CODE}/{DEVICE_ID}/telemetry
```

Example:
```json
{
  "sensor_id": "bulb-A1B2C3",
  "measurement_type": "voltage",
  "measurement_value": 12.5,
  "unit": "V",
  "timestamp": "2024-12-30T10:15:30Z",
  "quality_flag": "valid"
}
```

### Control (Cloud → Device)
```
ecos/{PROJECT_CODE}/{DEVICE_ID}/control
```

Example:
```json
{
  "action": "set_power",
  "params": {
    "enabled": true
  },
  "timestamp": "2024-12-30T10:15:30Z"
}
```

### Status (Device → Cloud)
```
ecos/{PROJECT_CODE}/{DEVICE_ID}/status
```

## Simulation Mode

For testing without hardware, enable `SIMULATION_MODE`:

```cpp
#define SIMULATION_MODE  // Enable simulation
```

In simulation mode:
- Sensor reads return random values
- Actuator writes print to serial instead of GPIO
- Useful for firmware logic testing

## Control Loop Latency

The firmware automatically measures control loop latency:

1. **Command Received**: Timestamp recorded
2. **Action Executed**: Latency calculated
3. **Target**: <200ms (Level 3 requirement)

Output example:
```
⏱️  Control Loop Latency: 45 ms ✅
```

## Project-Specific Customizations

### Project #8: Centennial Bulb (EverLume)
```cpp
#define PROJECT_CODE "P08"
#define DEVICE_TYPE "bulb"

void collectAndPublishTelemetry() {
    publishTelemetry("voltage", readVoltage(), "V");
    publishTelemetry("thermal_cycles", getThermalCycles(), "count");
    publishTelemetry("uptime", getUptime(), "hours");
}
```

### Project #9: AWG (AquaGen)
```cpp
#define PROJECT_CODE "P09"
#define DEVICE_TYPE "awg"

void collectAndPublishTelemetry() {
    publishTelemetry("humidity", readHumidity(), "percent");
    publishTelemetry("temperature", readTemperature(), "celsius");
    publishTelemetry("water_produced", getWaterVolume(), "liters");
}
```

### Project #12: Solar (SolarShare)
```cpp
#define PROJECT_CODE "P12"
#define DEVICE_TYPE "solar"

void collectAndPublishTelemetry() {
    publishTelemetry("irradiance", readIrradiance(), "W/m2");
    publishTelemetry("power_output", readPower(), "kW");
    publishTelemetry("voltage", readVoltage(), "V");
    publishTelemetry("current", readCurrent(), "A");
}
```

## Troubleshooting

### WiFi Won't Connect
- Check SSID and password
- Ensure ESP32 is within WiFi range
- Try 2.4GHz network (ESP32 doesn't support 5GHz)

### MQTT Connection Fails
- Verify broker IP/hostname
- Check username/password
- Ensure broker is running: `docker-compose up mqtt`
- Test with: `mosquitto_sub -h localhost -t "ecos/#" -v`

### No Telemetry Published
- Check serial monitor for error messages
- Verify MQTT broker is receiving: `mosquitto_sub -t "ecos/#"`
- Ensure `TELEMETRY_INTERVAL` is appropriate

### Control Commands Not Working
- Subscribe to control topic in serial monitor
- Test manually: `mosquitto_pub -t "ecos/P08/bulb-123/control" -m '{"action":"test"}'`
- Check `handleControlCommand()` implementation

## OTA Updates

The firmware is ready for OTA updates via the API gateway:

```bash
# Queue firmware update
curl -X POST http://localhost:8000/api/firmware/flash \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "bulb-A1B2C3",
    "project_code": "P08",
    "firmware_version": "v1.1.0",
    "checksum": "abc123..."
  }'
```

## Production Security

### Enabling TLS for MQTT

**Development (Current)**:
```cpp
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
const int MQTT_PORT = 1883;  // Unencrypted
```

**Production (Recommended)**:
```cpp
#include <WiFiClientSecure.h>

// Load CA certificate (broker's certificate authority)
const char* ca_cert = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDxTCCAq2gAwIBAgIBADANBgkqhkiG9w0BAQsFADCBgzELMAkGA1UEBhMCVVMx\n" \
"...\n" \
"-----END CERTIFICATE-----\n";

WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);
const int MQTT_PORT = 8883;  // TLS encrypted

void setup() {
    // Set CA certificate for verification
    wifiClient.setCACert(ca_cert);
    
    // Optional: Verify server hostname
    // wifiClient.setInsecure();  // Only for testing!
    
    // Connect to broker (same as before)
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    // ...
}
```

### Securing WiFi Credentials

Store credentials in EEPROM or SPIFFS instead of hardcoding:
```cpp
#include <Preferences.h>

Preferences preferences;

void loadCredentials() {
    preferences.begin("ecos", true);  // Read-only
    String ssid = preferences.getString("wifi_ssid", "");
    String password = preferences.getString("wifi_pass", "");
    preferences.end();
}
```

### Device-Specific MQTT Credentials

Generate unique credentials per device using device ID:
```cpp
String mqtt_username = "device_" + getMacAddress();
String mqtt_password = generateDevicePassword();  // From secure storage
```

## Next Steps

1. **Test in Simulation Mode**: Verify MQTT communication
2. **Connect Real Sensors**: Replace `SENSOR_READ()` with actual hardware
3. **Enable TLS**: Configure certificates for production
4. **Deploy to Device**: Flash to physical ESP32
5. **Monitor Telemetry**: View in dashboard at http://localhost:3000
6. **Test Control Loop**: Send commands and verify <200ms latency

## License

Proprietary - RegenCity Ecosystem
