// Project data based on Business Outline
export interface Project {
  id: string;
  code: string;
  name: string;
  type: string;
  phase: number;
  icon: string;
  color: string;
  readiness: number;
  description: string;
  businessModel: string;
  features: string[];
  techStack: string[];
  regenCityRole: string;
  apiEndpoints: string[];
}

export interface Phase {
  id: number;
  name: string;
  description: string;
}

export const phases: Phase[] = [
  {
    id: 1,
    name: 'Infrastructure Layer (IoT & Utility)',
    description: 'High-frequency data, recurring utility revenue, and the physical backbone.'
  },
  {
    id: 2,
    name: 'Biological Layer (Ag & Waste)',
    description: 'Living systems controlled by digital twins.'
  },
  {
    id: 3,
    name: 'Habitation Layer (Construction & Heat)',
    description: 'Complex physics simulations and B2C platforms.'
  },
  {
    id: 4,
    name: 'Innovation Layer (Deep Tech R&D)',
    description: 'Heavy simulation, regulatory compliance, and high barriers to entry.'
  }
];

export const projects: Project[] = [
  // Phase 1: Infrastructure Layer
  {
    id: 'P08',
    code: 'P08_BULB',
    name: 'EverLume',
    type: 'Centennial Bulb',
    phase: 1,
    icon: '💡',
    color: '#fbbf24',
    readiness: 70,
    description: 'Lighting-as-a-Service with predictive maintenance using Bayesian reliability models to predict failure years in advance.',
    businessModel: 'Commercial clients pay monthly subscription for guaranteed uptime',
    features: ['Predictive Maintenance', 'Bayesian Reliability Model', 'Fleet Management', 'Mesh Network'],
    techStack: ['C++ (ESP32)', 'AWS IoT Core', 'React Dashboard'],
    regenCityRole: 'Streetlights and housing illumination; establishes mesh network for other sensors',
    apiEndpoints: ['/api/bulb/predict']
  },
  {
    id: 'P13',
    code: 'P13_HYDRO',
    name: 'MicroHydro',
    type: 'Micro-Hydro Power',
    phase: 1,
    icon: '💧',
    color: '#3b82f6',
    readiness: 70,
    description: 'Energy-as-a-Service with containerized generation units using LSTM neural networks to forecast stream flow.',
    businessModel: 'Charges per kWh consumed at remote communities/resorts',
    features: ['Stream Flow Forecasting', 'LSTM Neural Networks', 'Battery Management', 'Weather Integration'],
    techStack: ['Go/Node.js', 'TimescaleDB', 'Industrial PLCs'],
    regenCityRole: 'Provides baseload power to construction HQ and server room',
    apiEndpoints: ['/api/hydro/forecast']
  },
  {
    id: 'P09',
    code: 'P09_AWG',
    name: 'AquaGen',
    type: 'Atmospheric Water Generator',
    phase: 1,
    icon: '🌊',
    color: '#06b6d4',
    readiness: 70,
    description: 'Water-as-a-Service using machine learning to predict humidity windows and minimize energy cost per liter.',
    businessModel: 'Water subscriptions or carbon credits from networked units',
    features: ['Humidity Forecasting', 'Cost Optimization', 'Prophet ML', 'PuLP Solver'],
    techStack: ['ESP32/MQTT', 'Python', 'Prophet'],
    regenCityRole: 'Distributed drinking water nodes for residential zone',
    apiEndpoints: ['/api/awg/forecast', '/api/awg/optimize']
  },
  // Phase 2: Biological Layer
  {
    id: 'P02',
    code: 'P02_SYMBIOSIS',
    name: 'AgriConnect',
    type: 'Plant-Fungi Symbiosis',
    phase: 2,
    icon: '🍄',
    color: '#84cc16',
    readiness: 70,
    description: 'Vertical SaaS with scikit-learn model matching fungal strains to soil microbiomes for maximum yield.',
    businessModel: 'Software subscription + lease fees for soil sensors',
    features: ['Fungal Strain Recommendation', 'Soil Analysis', 'Yield Prediction', 'ML Matching'],
    techStack: ['React Native', 'TimescaleDB', 'scikit-learn'],
    regenCityRole: 'Inoculates Zone C soil to boost initial crop yields by ~30%',
    apiEndpoints: ['/api/symbiosis/recommend']
  },
  {
    id: 'P03',
    code: 'P03_FARM',
    name: 'RegeneraFarm',
    type: 'Closed-Loop Farm',
    phase: 2,
    icon: '🌾',
    color: '#22c55e',
    readiness: 70,
    description: 'Enterprise SaaS digital twin platform using OR-Tools linear programming for nutrient cycle optimization.',
    businessModel: 'Digital twin platform + verified carbon credits from soil regeneration',
    features: ['Nutrient Cycle Optimizer', 'Carbon Credits', 'Geospatial Tracking', 'Compost Management'],
    techStack: ['NestJS', 'PostGIS', 'OR-Tools', 'Mapbox'],
    regenCityRole: 'Operating system for the 6-acre main farm',
    apiEndpoints: ['/api/farm/optimize']
  },
  {
    id: 'P07',
    code: 'P07_BIOREACTOR',
    name: 'PlastiCycle',
    type: 'Plastic-Eating Bacteria',
    phase: 2,
    icon: '♻️',
    color: '#14b8a6',
    readiness: 70,
    description: 'Equipment leasing with bioprocess control OS using PID controllers and ML models for bacterial growth optimization.',
    businessModel: 'Tipping fees from municipalities + monomer sales to chemical companies',
    features: ['Bioprocess Control', 'pH/Temp Management', 'Degradation Forecast', 'XGBoost ML'],
    techStack: ['Industrial PLCs', 'React Dashboard', 'Python'],
    regenCityRole: 'Processes construction waste and community plastic in Zone B',
    apiEndpoints: ['/api/bioreactor/status']
  },
  // Phase 3: Habitation Layer
  {
    id: 'P01',
    code: 'P01_FOAM_HOMES',
    name: 'EcoHomes OS',
    type: 'Foam Homes',
    phase: 3,
    icon: '🏠',
    color: '#f97316',
    readiness: 70,
    description: 'B2B2C platform with parametric design engine generating robot toolpaths and Bill of Materials from 3D models.',
    businessModel: 'SaaS for designers/builders + transaction fees on material marketplace',
    features: ['Parametric Design', 'BOM Generation', 'Robot Toolpaths', '3D Visualization'],
    techStack: ['Three.js', 'NestJS', 'Redis', 'Python/Grasshopper'],
    regenCityRole: 'Rapidly constructs 40 tiny homes in Zone A',
    apiEndpoints: ['/api/foam-homes/status']
  },
  {
    id: 'P10',
    code: 'P10_GEOTHERMAL',
    name: 'ThermalGrid',
    type: 'Geothermal Network',
    phase: 3,
    icon: '🔥',
    color: '#ef4444',
    readiness: 70,
    description: 'Heat-as-a-Service utility using graph theory algorithms to balance heat loads and manage ground-loop storage.',
    businessModel: 'Long-term 20-year contracts for district heating/cooling',
    features: ['Heat Flow Optimizer', 'Graph Theory', 'Valve Control', 'Sankey Visualization'],
    techStack: ['Go', 'NetworkX', 'Real-time Control'],
    regenCityRole: 'District heating loop under residential zone',
    apiEndpoints: ['/api/geothermal/optimize']
  },
  {
    id: 'P12',
    code: 'P12_SOLAR',
    name: 'SolarShare',
    type: 'Community Solar',
    phase: 3,
    icon: '☀️',
    color: '#eab308',
    readiness: 70,
    description: 'Fintech/Admin platform managing subscriptions and utility bill credits with credit allocation algorithms.',
    businessModel: 'Manages subscriptions and utility bill credits for community solar',
    features: ['Credit Allocator', 'Irradiance Forecasting', 'Subscriber Portal', 'Grid Injection'],
    techStack: ['Stripe', 'Utility APIs', 'Mobile App'],
    regenCityRole: 'Administers solar array on parking structures',
    apiEndpoints: ['/api/solar/forecast']
  },
  // Phase 4: Innovation Layer
  {
    id: 'P04',
    code: 'P04_HEMP_LAB',
    name: 'HempMobility',
    type: 'Hemp Car Lab',
    phase: 4,
    icon: '🚗',
    color: '#8b5cf6',
    readiness: 70,
    description: 'R&D-as-a-Service with FEA and LCA models for biocomposite material testing and fleet analytics.',
    businessModel: 'Contracts with OEMs for material testing + fleet analytics SaaS',
    features: ['FEA Simulation', 'Lifecycle Assessment', 'Crash Testing', 'WebGL Visualization'],
    techStack: ['AWS Batch/HPC', 'WebGL', 'Python'],
    regenCityRole: 'Garage in Zone D maintaining compound EV fleet',
    apiEndpoints: ['/api/hemp-lab/status']
  },
  {
    id: 'P05',
    code: 'P05_GREENHOUSE',
    name: 'LumiFreq',
    type: 'Resonant Illumination',
    phase: 4,
    icon: '🌱',
    color: '#a855f7',
    readiness: 70,
    description: 'Hardware + SaaS with computer vision feedback loop controller for AI-tuned light recipes.',
    businessModel: 'Sell controllers + subscription for AI-tuned light recipes',
    features: ['Light Recipe Control', 'Computer Vision', 'Frequency Generation', 'Plant Response'],
    techStack: ['Rust/C++', 'Go', 'DDS'],
    regenCityRole: 'Accelerates medicinal crop growth in Zone C greenhouses',
    apiEndpoints: ['/api/greenhouse/status']
  },
  {
    id: 'P06',
    code: 'P06_REACTOR',
    name: 'NucleoSim',
    type: 'Fast Reactor Twin',
    phase: 4,
    icon: '⚛️',
    color: '#ec4899',
    readiness: 70,
    description: 'Enterprise licensing with high-fidelity neutronics and thermal-hydraulics solvers for safety validation.',
    businessModel: 'Sold to regulators (NRC) and utilities for safety validation and training',
    features: ['Physics Engine', 'Neutronics Simulation', 'Safety Validation', '3D Visualization'],
    techStack: ['OpenMC', 'Kafka', 'Python'],
    regenCityRole: 'Server room simulation lab (no physical reactor yet)',
    apiEndpoints: ['/api/reactor/status']
  },
  {
    id: 'P11',
    code: 'P11_RESERVED',
    name: 'ThoriumOS',
    type: 'Reserved - Thorium Reactor',
    phase: 4,
    icon: '🔬',
    color: '#6b7280',
    readiness: 0,
    description: 'IP Licensing & Consulting for next-gen nuclear operating systems with molten-salt thermodynamics.',
    businessModel: 'Long-term play for next-gen nuclear operating systems',
    features: ['Chemistry Simulator', 'Molten-Salt Modeling', 'Fuel Burnup Cycles'],
    techStack: ['Java Spring Boot', 'Python', 'C++ Physics'],
    regenCityRole: 'R&D lab in Zone D designing future power source',
    apiEndpoints: []
  }
];

// API endpoints for the dashboard
export const apiEndpoints = {
  health: '/health',
  projects: '/projects',
  hydro: {
    forecast: '/api/hydro/forecast'
  },
  solar: {
    forecast: '/api/solar/forecast'
  },
  awg: {
    forecast: '/api/awg/forecast',
    optimize: '/api/awg/optimize'
  },
  bulb: {
    predict: '/api/bulb/predict'
  },
  farm: {
    optimize: '/api/farm/optimize'
  },
  geothermal: {
    optimize: '/api/geothermal/optimize'
  },
  symbiosis: {
    recommend: '/api/symbiosis/recommend'
  },
  dispatch: {
    status: '/api/dispatch/status',
    action: '/api/dispatch'
  }
};

// Mock data for dashboard charts
export const mockTelemetryData = {
  solar: [
    { time: '06:00', value: 50 },
    { time: '08:00', value: 200 },
    { time: '10:00', value: 450 },
    { time: '12:00', value: 600 },
    { time: '14:00', value: 550 },
    { time: '16:00', value: 350 },
    { time: '18:00', value: 100 },
  ],
  hydro: [
    { time: '00:00', value: 45 },
    { time: '04:00', value: 42 },
    { time: '08:00', value: 48 },
    { time: '12:00', value: 52 },
    { time: '16:00', value: 50 },
    { time: '20:00', value: 47 },
  ],
  water: [
    { time: '00:00', value: 12 },
    { time: '04:00', value: 18 },
    { time: '08:00', value: 8 },
    { time: '12:00', value: 5 },
    { time: '16:00', value: 15 },
    { time: '20:00', value: 22 },
  ]
};

export const systemMetrics = {
  totalPowerGeneration: 152.5,
  waterProduction: 85.3,
  carbonOffset: 12.7,
  activeDevices: 47,
  systemUptime: 99.2
};
