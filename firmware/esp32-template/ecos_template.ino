/*
 * ECOS ESP32 Firmware Template
 * Level 3: Physical Twin - Hardware Integration
 * 
 * This template provides a foundation for all 13 ECOS projects
 * to communicate with the MQTT broker and send telemetry data.
 * 
 * Customization points:
 * - PROJECT_CODE: Set to P01-P13
 * - DEVICE_TYPE: Specific sensor/actuator type
 * - Measurement functions: Implement project-specific logic
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

// ============================================
// CONFIGURATION - Customize per project
// ============================================

#define PROJECT_CODE "P08"  // Change to P01-P13
#define DEVICE_TYPE "bulb"  // e.g., bulb, sensor, pump, valve
#define FIRMWARE_VERSION "v1.0.0"

// WiFi credentials (should be set via config portal in production)
const char* WIFI_SSID = "ECOS-Network";
const char* WIFI_PASSWORD = "change_me_in_production";

// MQTT broker configuration
// WARNING: This template uses unencrypted MQTT (port 1883) for development.
// For production, use TLS-secured MQTT (port 8883) with WiFiClientSecure:
//   - Change WiFiClient to WiFiClientSecure
//   - Set MQTT_PORT to 8883
//   - Load and verify server certificates
//   - See: https://github.com/espressif/arduino-esp32/tree/master/libraries/WiFiClientSecure
const char* MQTT_BROKER = "mqtt.ecos.local";  // Or IP address
const int MQTT_PORT = 1883;  // Use 8883 for TLS in production
const char* MQTT_USERNAME = "ecos_iot";
const char* MQTT_PASSWORD = "change_me_in_production";

// Device configuration
String deviceId;  // Generated from MAC address
String telemetryTopic;
String controlTopic;

// Telemetry interval (milliseconds)
const unsigned long TELEMETRY_INTERVAL = 5000;  // 5 seconds
unsigned long lastTelemetryTime = 0;

// Control loop latency tracking
unsigned long controlCommandTime = 0;
bool controlCommandPending = false;

// WiFi and MQTT clients
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// ============================================
// SIMULATION MODE (for testing without hardware)
// ============================================

#define SIMULATION_MODE  // Comment out to use real hardware

#ifdef SIMULATION_MODE
  #define SENSOR_READ(pin) (random(0, 1024))
  #define ACTUATOR_WRITE(pin, value) (Serial.printf("ACTUATOR: Pin %d = %d\n", pin, value))
#else
  #define SENSOR_READ(pin) (analogRead(pin))
  #define ACTUATOR_WRITE(pin, value) (digitalWrite(pin, value))
#endif

// ============================================
// HELPER FUNCTIONS
// ============================================

String getMacAddress() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    snprintf(macStr, sizeof(macStr), "%02X%02X%02X%02X%02X%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    return String(macStr);
}

String getIsoTimestamp() {
    time_t now;
    struct tm timeinfo;
    char buffer[30];
    
    time(&now);
    gmtime_r(&now, &timeinfo);
    strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    
    return String(buffer);
}

void setupWiFi() {
    Serial.println("\n🔌 Connecting to WiFi...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi connected!");
        Serial.printf("   IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("   MAC: %s\n", getMacAddress().c_str());
    } else {
        Serial.println("\n❌ WiFi connection failed");
    }
}

void setupNTP() {
    Serial.println("⏰ Configuring NTP...");
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    
    // Wait for time sync
    int attempts = 0;
    while (time(nullptr) < 100000 && attempts < 10) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    Serial.println("\n✅ NTP synchronized");
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("📨 MQTT message on %s\n", topic);
    
    // Record control command receipt time for latency measurement
    if (String(topic) == controlTopic && !controlCommandPending) {
        controlCommandTime = millis();
        controlCommandPending = true;
    }
    
    // Parse JSON payload
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    
    if (error) {
        Serial.printf("❌ JSON parsing failed: %s\n", error.c_str());
        return;
    }
    
    // Extract command
    const char* action = doc["action"];
    if (action) {
        handleControlCommand(action, doc["params"]);
    }
}

void connectMQTT() {
    while (!mqttClient.connected()) {
        Serial.println("🔌 Connecting to MQTT broker...");
        
        if (mqttClient.connect(deviceId.c_str(), MQTT_USERNAME, MQTT_PASSWORD)) {
            Serial.println("✅ MQTT connected!");
            
            // Subscribe to control topic
            mqttClient.subscribe(controlTopic.c_str());
            Serial.printf("📡 Subscribed to: %s\n", controlTopic.c_str());
            
            // Publish online status
            publishStatus("online");
        } else {
            Serial.printf("❌ MQTT connection failed, rc=%d\n", mqttClient.state());
            Serial.println("   Retrying in 5 seconds...");
            delay(5000);
        }
    }
}

// ============================================
// PROJECT-SPECIFIC FUNCTIONS (Customize these)
// ============================================

void handleControlCommand(const char* action, JsonVariant params) {
    Serial.printf("🎮 Control Command: %s\n", action);
    
    // Example: Turn on/off an actuator
    if (strcmp(action, "set_power") == 0) {
        bool powerOn = params["enabled"].as<bool>();
        ACTUATOR_WRITE(2, powerOn ? HIGH : LOW);
        Serial.printf("   Power: %s\n", powerOn ? "ON" : "OFF");
    }
    else if (strcmp(action, "set_brightness") == 0) {
        int brightness = params["value"].as<int>();
        analogWrite(5, brightness);
        Serial.printf("   Brightness: %d%%\n", brightness);
    }
    
    // Calculate control loop latency
    if (controlCommandPending) {
        unsigned long latency = millis() - controlCommandTime;
        Serial.printf("⏱️  Control Loop Latency: %lu ms", latency);
        if (latency < 200) {
            Serial.println(" ✅");
        } else {
            Serial.println(" ⚠️  (>200ms target)");
        }
        controlCommandPending = false;
    }
}

void publishTelemetry(const char* measurementType, float value, const char* unit) {
    StaticJsonDocument<256> doc;
    
    doc["sensor_id"] = deviceId;
    doc["measurement_type"] = measurementType;
    doc["measurement_value"] = value;
    doc["unit"] = unit;
    doc["timestamp"] = getIsoTimestamp();
    doc["quality_flag"] = "valid";
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    if (mqttClient.publish(telemetryTopic.c_str(), buffer, true)) {
        Serial.printf("📤 Telemetry: %s = %.2f %s\n", measurementType, value, unit);
    } else {
        Serial.println("❌ Failed to publish telemetry");
    }
}

void publishStatus(const char* status) {
    StaticJsonDocument<128> doc;
    doc["device_id"] = deviceId;
    doc["status"] = status;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["uptime_ms"] = millis();
    
    char buffer[128];
    serializeJson(doc, buffer);
    
    String statusTopic = "ecos/" + String(PROJECT_CODE) + "/" + deviceId + "/status";
    mqttClient.publish(statusTopic.c_str(), buffer, true);
}

void collectAndPublishTelemetry() {
    // Example telemetry collection (customize per project)
    
    // Default: Generic sensor readings
    float sensorValue = SENSOR_READ(34);
    publishTelemetry("sensor_value", sensorValue, "raw");
    
    // Add project-specific measurements here
}

// ============================================
// ARDUINO SETUP & LOOP
// ============================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n╔═══════════════════════════════════════╗");
    Serial.println("║   ECOS ESP32 Firmware Template       ║");
    Serial.println("║   Level 3: Physical Twin             ║");
    Serial.println("╚═══════════════════════════════════════╝\n");
    
    Serial.printf("Project: %s\n", PROJECT_CODE);
    Serial.printf("Device Type: %s\n", DEVICE_TYPE);
    Serial.printf("Firmware: %s\n", FIRMWARE_VERSION);
    
    // Generate device ID from MAC
    deviceId = String(DEVICE_TYPE) + "-" + getMacAddress().substring(6);
    Serial.printf("Device ID: %s\n", deviceId.c_str());
    
    // Configure MQTT topics
    telemetryTopic = "ecos/" + String(PROJECT_CODE) + "/" + deviceId + "/telemetry";
    controlTopic = "ecos/" + String(PROJECT_CODE) + "/" + deviceId + "/control";
    
    Serial.printf("Telemetry Topic: %s\n", telemetryTopic.c_str());
    Serial.printf("Control Topic: %s\n\n", controlTopic.c_str());
    
    // Initialize hardware
    #ifndef SIMULATION_MODE
        pinMode(2, OUTPUT);  // Actuator/relay
        pinMode(34, INPUT);  // Sensor input (ADC)
    #endif
    
    // Connect to WiFi
    setupWiFi();
    
    if (WiFi.status() == WL_CONNECTED) {
        // Configure NTP for timestamps
        setupNTP();
        
        // Configure MQTT
        mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
        mqttClient.setCallback(mqttCallback);
        mqttClient.setBufferSize(512);
        
        // Initial connection
        connectMQTT();
    }
    
    Serial.println("\n✅ Setup complete - entering main loop\n");
}

void loop() {
    // Maintain MQTT connection
    if (WiFi.status() == WL_CONNECTED) {
        if (!mqttClient.connected()) {
            connectMQTT();
        }
        mqttClient.loop();
    } else {
        Serial.println("⚠️  WiFi disconnected, reconnecting...");
        setupWiFi();
    }
    
    // Publish telemetry at regular intervals
    unsigned long now = millis();
    if (now - lastTelemetryTime >= TELEMETRY_INTERVAL) {
        collectAndPublishTelemetry();
        lastTelemetryTime = now;
    }
    
    // Small delay to prevent watchdog timeout
    delay(10);
}
