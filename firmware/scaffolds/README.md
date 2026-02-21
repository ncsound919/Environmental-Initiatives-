# Firmware Scaffolds for EcoSphere Initiatives

This directory provides lightweight scaffolds to align device firmware with the shared telemetry/control contract.

## Common MQTT Contract
- Telemetry topic: `ecos/{project}/{deviceId}/telemetry`
- Control topic: `ecos/{project}/{deviceId}/control`
- Payload schema: see `packages/hardware-sdk/src/index.ts#TelemetrySchema`

## Per-Initiative Starting Points
- **P01 EcoHomes OS (HVAC Controller)**: publish `temperature`, `humidity`, `co2`; act on `setpoint`, `fan-mode`.
- **P02 AgriConnect (Soil Probe/Irrigation)**: publish `soil_moisture`, `soil_ph`, `n`, `p`, `k`; act on `irrigate-now`, `dose-npk`.
- **P03 RegeneraFarm (Nutrient Loop)**: publish compost `temperature`, `moisture`; act on `balance-loop`, `dose-nutrients`.
- **P04 HempMobility (Material Testbench)**: publish `strain`, `stress`; act on `run-test`, `ramp-temp`.
- **P05 LumiFreq (Spectral Controller)**: publish `ppfd`, `spectrum`; act on `set-recipe`, `photoperiod`.
- **P06 NucleoSim (Simulation Node)**: publish `temp_sim`, `pressure_sim`; act on `start-sim`, `set-boundary`.
- **P07 PlastiCycle (Bioreactor)**: publish `ph`, `temperature`, `dissolved_oxygen`; act on `maintain-ph`, `dose-feed`.
- **P08 EverLume (LED Bulb)**: publish `voltage`, `thermal_cycles`, `uptime`; act on `set-brightness`, `firmware-ota`.
- **P09 AquaGen (AWG Unit)**: publish `humidity`, `temperature`, `power_draw`; act on `start-awg`, `optimize-cost`.
- **P10 ThermalGrid (Geothermal PLC)**: publish `flow_rate`, `supply_temp`, `return_temp`; act on `balance-loop`, `shed-load`.
- **P11 Future**: placeholder.
- **P12 SolarShare (Inverter/String Monitor)**: publish `irradiance`, `voltage`, `current`, `power`; act on `curtail`, `export`.
- **P13 MicroHydro (Turbine Controller)**: publish `flow`, `head`, `power`; act on `spin-up`, `island-mode`.

## Loop Skeleton (C/Python-like pseudocode)
```c
loop() {
  Telemetry t = readSensors();
  mqtt_publish("ecos/P09/awg-001/telemetry", t);

  Control cmd = mqtt_poll("ecos/P09/awg-001/control");
  if (cmd.action == "optimize-cost") {
    apply_awg_schedule(cmd.params);
  }
}
```

Use this as a starting point for ESP32/PLC/edge-compute code; map field names exactly to the manifest and TelemetrySchema.
