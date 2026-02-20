"""
ECOS MQTT Service - Level 2/3 IoT Pipeline
Real-time telemetry ingestion and device control
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Optional
import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, ValidationError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelemetryMessage(BaseModel):
    """Validated telemetry message format"""
    sensor_id: str = Field(min_length=1)
    project_code: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    measurement_type: str = Field(min_length=1)
    measurement_value: float
    unit: str = Field(min_length=1)
    timestamp: str  # ISO 8601 format
    quality_flag: str = Field(default="valid")


class EcosMqttService:
    """
    MQTT service for ECOS ecosystem
    
    Handles:
    - Real-time telemetry from IoT devices
    - Control commands to devices
    - Cross-project dispatcher messages
    """
    
    def __init__(
        self,
        broker_host: str = None,
        broker_port: int = None,
        username: str = None,
        password: str = None,
        on_telemetry: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_control: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.broker_host = broker_host or os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(broker_port or os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = username or os.getenv("MQTT_USERNAME")
        self.password = password or os.getenv("MQTT_PASSWORD")
        
        self.on_telemetry_callback = on_telemetry
        self.on_control_callback = on_control
        
        # MQTT client setup
        self.client = mqtt.Client(client_id="ecos-gateway", clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.is_connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Subscribe to all telemetry topics
            client.subscribe("ecos/+/+/telemetry")
            logger.info("📡 Subscribed to: ecos/+/+/telemetry")
            
            # Subscribe to all control topics
            client.subscribe("ecos/+/+/control")
            logger.info("📡 Subscribed to: ecos/+/+/control")
            
            # Subscribe to dispatcher commands
            client.subscribe("ecos/dispatcher/#")
            logger.info("📡 Subscribed to: ecos/dispatcher/#")
        else:
            logger.error(f"❌ MQTT connection failed with code {rc}")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"⚠️  Unexpected disconnection from MQTT broker (code: {rc})")
        else:
            logger.info("🔌 Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"📨 Received message on {topic}")
            
            # Handle dispatcher messages first (before generic parsing)
            if topic.startswith("ecos/dispatcher/"):
                self._handle_dispatcher(topic, payload)
                return
            
            # Parse topic: ecos/{project_code}/{device_id}/{type}
            parts = topic.split('/')
            
            if len(parts) >= 4 and parts[0] == "ecos":
                project_code = parts[1]
                device_id = parts[2]
                msg_type = parts[3]
                
                if msg_type == "telemetry":
                    self._handle_telemetry(project_code, device_id, payload)
                elif msg_type == "control":
                    self._handle_control(project_code, device_id, payload)
            
        except Exception as e:
            logger.error(f"❌ Error processing message on {msg.topic}: {e}")
    
    def _handle_telemetry(self, project_code: str, device_id: str, payload: str):
        """Process telemetry message"""
        try:
            data = json.loads(payload)
            
            # Validate message format
            telemetry = TelemetryMessage(
                sensor_id=data.get("sensor_id", device_id),
                project_code=project_code,
                device_id=device_id,
                measurement_type=data["measurement_type"],
                measurement_value=float(data["measurement_value"]),
                unit=data["unit"],
                timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                quality_flag=data.get("quality_flag", "valid"),
            )
            
            logger.info(
                f"📊 Telemetry: {project_code}/{device_id} - "
                f"{telemetry.measurement_type}={telemetry.measurement_value}{telemetry.unit}"
            )
            
            # Call callback if registered
            if self.on_telemetry_callback:
                self.on_telemetry_callback(telemetry.model_dump())
        
        except ValidationError as e:
            logger.error(f"❌ Invalid telemetry format: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in telemetry: {e}")
        except Exception as e:
            logger.error(f"❌ Error handling telemetry: {e}")
    
    def _handle_control(self, project_code: str, device_id: str, payload: str):
        """Process control command"""
        try:
            command = json.loads(payload)
            logger.info(f"🎮 Control: {project_code}/{device_id} - {command.get('action', 'unknown')}")
            
            # Call callback if registered
            if self.on_control_callback:
                self.on_control_callback(f"{project_code}/{device_id}", command)
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in control command: {e}")
        except Exception as e:
            logger.error(f"❌ Error handling control: {e}")
    
    def _handle_dispatcher(self, topic: str, payload: str):
        """Process dispatcher message"""
        try:
            data = json.loads(payload)
            logger.info(f"🔀 Dispatcher: {topic} - {data.get('action', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Error handling dispatcher message: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(f"🔌 Connecting to MQTT broker at {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"❌ Failed to connect to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("👋 Disconnected from MQTT broker")
    
    def publish_telemetry(
        self,
        project_code: str,
        device_id: str,
        measurement_type: str,
        measurement_value: float,
        unit: str,
        quality_flag: str = "valid",
    ) -> bool:
        """Publish telemetry data to MQTT"""
        topic = f"ecos/{project_code}/{device_id}/telemetry"
        
        payload = {
            "sensor_id": device_id,
            "measurement_type": measurement_type,
            "measurement_value": measurement_value,
            "unit": unit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quality_flag": quality_flag,
        }
        
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"📤 Published telemetry to {topic}")
                return True
            else:
                logger.error(f"❌ Failed to publish telemetry: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"❌ Error publishing telemetry: {e}")
            return False
    
    def publish_control(
        self,
        project_code: str,
        device_id: str,
        action: str,
        params: Dict[str, Any] = None,
    ) -> bool:
        """Publish control command to device"""
        topic = f"ecos/{project_code}/{device_id}/control"
        
        payload = {
            "action": action,
            "params": params or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=2)  # QoS 2 for control
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Published control to {topic}: {action}")
                return True
            else:
                logger.error(f"❌ Failed to publish control: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"❌ Error publishing control: {e}")
            return False


# Example usage
if __name__ == "__main__":
    def on_telemetry_received(data: Dict[str, Any]):
        """Callback for telemetry"""
        print(f"Received telemetry: {data}")
    
    def on_control_received(device: str, command: Dict[str, Any]):
        """Callback for control commands"""
        print(f"Received control for {device}: {command}")
    
    # Create MQTT service
    mqtt_service = EcosMqttService(
        on_telemetry=on_telemetry_received,
        on_control=on_control_received,
    )
    
    # Connect and run
    try:
        mqtt_service.connect()
        
        # Publish test data
        mqtt_service.publish_telemetry(
            project_code="P08",
            device_id="bulb-001",
            measurement_type="voltage",
            measurement_value=12.5,
            unit="V",
        )
        
        # Keep running
        import time
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        mqtt_service.disconnect()
