# RFQ — Quote-Required BOM Lines

Capital equipment with no public list price. Fill a quote per line into `initiatives/rfq/quotes.json`, then run `node initiatives/rfq.mjs --apply`.

## EcoHomes OS (P01_FOAM_HOMES) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Commercial thermostat (0-10V) | 1 | 120 |  | HVAC distributor |  |
| CO2/VOC sensor | 1 | 45 |  | Digi-Key |  |
| Damper actuator | 4 | 60 |  | HVAC distributor |  |
| Heat-pump control board | 1 | 55 |  | HVAC distributor |  |
| BMS edge gateway | 1 | 150 |  | Industrial supplier |  |

## AgriConnect (P02_SYMBIOSIS) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Soil probe array | 6 | 45 |  | Generic |  |
| LoRa gateway | 1 | 220 |  | Digi-Key |  |
| Irrigation valve + actuator | 4 | 85 |  | Agricultural supplier |  |
| Fertigation dosing pump | 1 | 250 |  | Agricultural supplier |  |
| Zone controller | 1 | 150 |  | Industrial supplier |  |
| Solar + battery PSU | 1 | 180 |  | Generic |  |

## RegeneraFarm (P03_FARM) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Compost probe set | 8 | 45 |  | Generic |  |
| Aerator blower | 1 | 350 |  | Agricultural supplier |  |
| Nutrient dosing pump | 1 | 300 |  | Agricultural supplier |  |
| Loop controller | 1 | 180 |  | Industrial supplier |  |
| LoRa gateway | 1 | 200 |  | Digi-Key |  |
| Windrow sensor | 1 | 250 |  | Agricultural supplier |  |

## HempMobility (P04_HEMP_LAB) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Universal testing machine (small) | 1 | 12000 |  | Materials lab supplier |  |
| Thermal chamber | 1 | 6000 |  | Environmental supplier |  |
| DAQ system | 1 | 1500 |  | National Instruments |  |
| HPC workstation | 1 | 4500 |  | Hardware vendor |  |
| Instrumented fixtures | 1 | 500 |  | Materials lab supplier |  |

## LumiFreq (P05_GREENHOUSE) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| LED array (4-channel) | 20 | 320 |  | LED supplier |  |
| Spectral sensor | 6 | 220 |  | Apogee Instruments |  |
| Zone controller | 1 | 350 |  | Industrial supplier |  |
| Gateway | 1 | 200 |  | Industrial supplier |  |

## NucleoSim (P06_REACTOR) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| HPC node (dual CPU) | 1 | 12000 |  | OEM |  |
| GPU accelerator | 1 | 8000 |  | OEM |  |
| Rack + PDU | 1 | 2500 |  | Datacenter supplier |  |
| Cooling | 1 | 1800 |  | Datacenter supplier |  |
| Networking (100GbE) | 1 | 3000 |  | Datacenter supplier |  |

## PlastiCycle (P07_BIOREACTOR) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| 100 L bioreactor vessel | 1 | 8000 |  | Biotech supplier |  |
| Agitator drive | 1 | 2000 |  | Biotech supplier |  |
| DO/pH controllers | 1 | 1500 |  | Biotech supplier |  |
| Feed/air pumps | 1 | 900 |  | Biotech supplier |  |
| Industrial PLC | 1 | 2500 |  | Siemens |  |
| HMI panel | 1 | 1200 |  | Siemens |  |

## EverLume (P08_BULB) — enterprise, per 100-fixture building

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Commercial LED troffer/high-bay fixture (0-10V dimmable) | 100 | 55 |  | Commercial lighting distributor |  |
| 0-10V dimmable LED driver | 100 | 25 |  | Commercial lighting distributor |  |
| Thread/Zigbee mesh module (per fixture) | 100 | 8 |  | Digi-Key |  |
| Per-circuit energy meter (CT clamp) | 8 | 20 |  | Digi-Key |  |
| Industrial PoE MQTT gateway | 1 | 150 |  | Industrial supplier |  |
| PoE network switch (24-port) | 1 | 120 |  | Network supplier |  |

## AquaGen (P09_AWG) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| AWG unit (1000 L/day) | 10 | 12000 |  | Water tech supplier |  |
| Water-quality lab kit | 1 | 3000 |  | Lab supplier |  |
| Controls + sensors | 1 | 1500 |  | Industrial supplier |  |
| Installation | 1 | 4000 |  | Contractor |  |

## ThermalGrid (P10_GEOTHERMAL) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Ground loop + drilling | 1 | 250000 |  | Geothermal EPC |  |
| Heat pumps | 8 | 8000 |  | HVAC supplier |  |
| Circulation pumps | 4 | 3500 |  | HVAC supplier |  |
| PLC/SCADA | 1 | 12000 |  | Industrial supplier |  |
| Flow/temp sensors | 1 | 6000 |  | Industrial supplier |  |

## SolarShare (P12_SOLAR) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Solar PV (200 kW) | 1 | 60000 |  | Solar supplier |  |
| String inverters | 1 | 12000 |  | Solar supplier |  |
| Monitoring + CT | 1 | 4000 |  | Industrial supplier |  |
| Mounting/racking | 1 | 15000 |  | Solar supplier |  |
| Installation | 1 | 20000 |  | EPC |  |

## MicroHydro (P13_HYDRO) — enterprise, per site

| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |
|---|---:|---:|---:|---|---|
| Turbine + generator (5 kW) | 1 | 45000 |  | Hydro supplier |  |
| PLC/controls | 1 | 8000 |  | Industrial supplier |  |
| Gate actuator | 1 | 6000 |  | Hydro supplier |  |
| Flow/head sensors | 1 | 3000 |  | Industrial supplier |  |
| Civil works | 1 | 40000 |  | EPC |  |

_62 lines awaiting quotes._
