/**
 * ECOS Hardware SDK
 * Shared MQTT/IoT communication layer for all devices
 */

import mqtt, { MqttClient } from 'mqtt';
import { z } from 'zod';

// ============================================
// TELEMETRY SCHEMA (matches Prisma schema)
// ============================================

export const TelemetrySchema = z.object({
  sensorId: z.string().uuid(),
  locationId: z.string().optional(),
  measurementType: z.string(),
  measurementValue: z.number(),
  unit: z.string(),
  timestamp: z.string().datetime(),
  qualityFlag: z.enum(['valid', 'suspect', 'error']).default('valid'),
  schemaVersion: z.string().default('1.0.0'),
  sourceSystem: z.string(),
  ingestionTime: z.string().datetime().optional(),
});

export type Telemetry = z.infer<typeof TelemetrySchema>;

// ============================================
// MQTT CLIENT
// ============================================

export interface MqttConfig {
  brokerUrl: string;
  clientId?: string;
  username?: string;
  password?: string;
}

export class EcosMqttClient {
  private client: MqttClient | null = null;
  private config: MqttConfig;

  constructor(config: MqttConfig) {
    this.config = config;
  }

  /**
   * Connect to MQTT broker
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.client = mqtt.connect(this.config.brokerUrl, {
        clientId: this.config.clientId,
        username: this.config.username,
        password: this.config.password,
      });

      this.client.on('connect', () => {
        console.log('Connected to MQTT broker');
        resolve();
      });

      this.client.on('error', (error) => {
        console.error('MQTT connection error:', error);
        reject(error);
      });
    });
  }

  /**
   * Publish telemetry data
   * Topic format: ecos/{project_code}/{device_id}/telemetry
   */
  async publishTelemetry(
    projectCode: string,
    deviceId: string,
    telemetry: Telemetry
  ): Promise<void> {
    if (!this.client) {
      throw new Error('MQTT client not connected');
    }

    // Validate telemetry data
    const validatedTelemetry = TelemetrySchema.parse(telemetry);

    const topic = `ecos/${projectCode}/${deviceId}/telemetry`;
    const payload = JSON.stringify(validatedTelemetry);

    return new Promise((resolve, reject) => {
      this.client!.publish(topic, payload, { qos: 1 }, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  }

  /**
   * Subscribe to telemetry topic
   */
  async subscribe(
    projectCode: string,
    deviceId: string,
    callback: (telemetry: Telemetry) => void
  ): Promise<void> {
    if (!this.client) {
      throw new Error('MQTT client not connected');
    }

    const topic = `ecos/${projectCode}/${deviceId}/telemetry`;

    this.client.subscribe(topic, { qos: 1 });

    this.client.on('message', (messageTopic, payload) => {
      if (messageTopic === topic) {
        try {
          const data = JSON.parse(payload.toString());
          const telemetry = TelemetrySchema.parse(data);
          callback(telemetry);
        } catch (error) {
          console.error('Invalid telemetry data:', error);
        }
      }
    });
  }

  /**
   * Send control command to device
   * Topic format: ecos/{project_code}/{device_id}/command
   */
  async sendCommand(
    projectCode: string,
    deviceId: string,
    command: {
      action: string;
      params?: Record<string, any>;
    }
  ): Promise<void> {
    if (!this.client) {
      throw new Error('MQTT client not connected');
    }

    const topic = `ecos/${projectCode}/${deviceId}/command`;
    const payload = JSON.stringify({
      action: command.action,
      params: command.params || {},
      timestamp: new Date().toISOString(),
    });

    return new Promise((resolve, reject) => {
      this.client!.publish(topic, payload, { qos: 1 }, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  }

  /**
   * Disconnect from MQTT broker
   */
  async disconnect(): Promise<void> {
    if (this.client) {
      return new Promise((resolve) => {
        this.client!.end(false, {}, () => {
          console.log('Disconnected from MQTT broker');
          resolve();
        });
      });
    }
  }
}

// ============================================
// DEVICE MANAGER
// ============================================

export interface DeviceInfo {
  deviceId: string;
  projectCode: string;
  deviceType: string;
  locationId?: string;
  status: 'active' | 'inactive' | 'maintenance' | 'offline';
}

export class DeviceManager {
  private devices: Map<string, DeviceInfo> = new Map();

  /**
   * Register a new device
   */
  registerDevice(device: DeviceInfo): void {
    this.devices.set(device.deviceId, device);
  }

  /**
   * Get device information
   */
  getDevice(deviceId: string): DeviceInfo | undefined {
    return this.devices.get(deviceId);
  }

  /**
   * Update device status
   */
  updateDeviceStatus(
    deviceId: string,
    status: DeviceInfo['status']
  ): void {
    const device = this.devices.get(deviceId);
    if (device) {
      device.status = status;
    }
  }

  /**
   * Get all devices for a project
   */
  getProjectDevices(projectCode: string): DeviceInfo[] {
    return Array.from(this.devices.values()).filter(
      (device) => device.projectCode === projectCode
    );
  }

  /**
   * Get all active devices
   */
  getActiveDevices(): DeviceInfo[] {
    return Array.from(this.devices.values()).filter(
      (device) => device.status === 'active'
    );
  }
}

// ============================================
// EXPORTS
// ============================================

export default {
  EcosMqttClient,
  DeviceManager,
  TelemetrySchema,
};
