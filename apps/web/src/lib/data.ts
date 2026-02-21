// Project data based on Business Outline
export interface ResourceNeed {
  category: string;
  items: string[];
}

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
  partnershipNeeds: string[];
  affiliateOpportunities: string[];
  resourceNeeds: ResourceNeed[];
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
    apiEndpoints: ['/api/bulb/predict'],
    partnershipNeeds: [
      'Commercial property management firms for deployment',
      'Utility companies for grid integration',
      'IoT hardware manufacturers for custom bulb supply',
      'Insurance providers for uptime guarantee underwriting',
    ],
    affiliateOpportunities: [
      'Energy efficiency consultants',
      'Smart building integrators',
      'Facility management companies',
      'Municipal procurement partners',
    ],
    resourceNeeds: [
      { category: 'Hardware', items: ['ESP32 microcontrollers', 'LED driver boards', 'Wireless mesh modules'] },
      { category: 'Facilities', items: ['Assembly / QA lab', 'Warehouse for fleet inventory'] },
      { category: 'Software Dev', items: ['Embedded firmware engineers', 'Cloud dashboard developers'] },
      { category: 'Capital', items: ['Seed funding for pilot fleet deployment', 'R&D grants for predictive model'] },
      { category: 'Labor', items: ['Field installation technicians', 'Data-science interns'] },
    ]
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
    apiEndpoints: ['/api/hydro/forecast'],
    partnershipNeeds: [
      'Remote-community energy co-ops',
      'Eco-resort developers',
      'Hydrology engineering firms',
      'Battery / storage technology suppliers',
    ],
    affiliateOpportunities: [
      'Off-grid living influencers and media',
      'Renewable energy brokers',
      'Rural electrification NGOs',
      'Carbon credit marketplace platforms',
    ],
    resourceNeeds: [
      { category: 'Land', items: ['Riparian rights / water access agreements', 'Creek or river-adjacent sites'] },
      { category: 'Hardware', items: ['Turbine runners', 'Industrial PLCs', 'Battery banks'] },
      { category: 'Capital', items: ['Equipment financing', 'Project-finance lenders for ESCO contracts'] },
      { category: 'Labs', items: ['Hydraulics testing facility', 'Flow-measurement instrumentation'] },
      { category: 'Labor', items: ['Civil/mechanical engineers', 'On-site maintenance crew'] },
    ]
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
    apiEndpoints: ['/api/awg/forecast', '/api/awg/optimize'],
    partnershipNeeds: [
      'Water utility companies for regulatory pathway',
      'Climate-resilience NGOs for deployment grants',
      'HVAC manufacturers for condenser-coil integration',
      'Carbon credit registries for water-production credits',
    ],
    affiliateOpportunities: [
      'Disaster-preparedness equipment retailers',
      'Sustainable living community networks',
      'International development organisations',
      'Green building certification bodies',
    ],
    resourceNeeds: [
      { category: 'Hardware', items: ['Condensation units', 'Filtration assemblies', 'ESP32 sensor nodes'] },
      { category: 'Facilities', items: ['Clean assembly room', 'Water-quality testing lab'] },
      { category: 'Capital', items: ['Working capital for unit production runs', 'Grant funding (USDA / EPA)'] },
      { category: 'Software Dev', items: ['ML forecasting engineers (Prophet/Python)', 'Mobile monitoring app'] },
      { category: 'Labor', items: ['Water-quality chemists', 'Field deployment technicians'] },
    ]
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
    apiEndpoints: ['/api/symbiosis/recommend'],
    partnershipNeeds: [
      'Commercial farms and agri-tech co-operatives',
      'Soil-science research universities',
      'Sensor hardware suppliers (IoT soil probes)',
      'Organic certification bodies',
    ],
    affiliateOpportunities: [
      'Regenerative agriculture educators and YouTubers',
      'Seed and organic fertiliser retailers',
      'Farm management software platforms',
      'Permaculture design consultants',
    ],
    resourceNeeds: [
      { category: 'Land', items: ['Test plots (min 1 acre) for strain trials'] },
      { category: 'Labs', items: ['Mycology inoculation lab', 'Soil analysis equipment'] },
      { category: 'Hardware', items: ['Soil-moisture / nutrient sensors', 'Data-logger stations'] },
      { category: 'Software Dev', items: ['scikit-learn ML pipeline engineers', 'React Native mobile app devs'] },
      { category: 'Capital', items: ['Lab set-up capital', 'University partnership grants'] },
      { category: 'Labor', items: ['Mycologists / microbiologists', 'Field agronomists'] },
    ]
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
    apiEndpoints: ['/api/farm/optimize'],
    partnershipNeeds: [
      'Carbon credit exchanges and registries',
      'Precision-ag equipment manufacturers',
      'Grocery chains and food distributors for off-take agreements',
      'Insurance providers for crop yield guarantees',
    ],
    affiliateOpportunities: [
      'Regenerative farm influencers and media',
      'Farm-to-table restaurant networks',
      'CSA (Community Supported Agriculture) platforms',
      'Sustainable food certification programmes',
    ],
    resourceNeeds: [
      { category: 'Land', items: ['6+ acres for closed-loop farm operations', 'Water rights for irrigation'] },
      { category: 'Facilities', items: ['Processing and storage barns', 'Composting infrastructure'] },
      { category: 'Hydroponics', items: ['Greenhouse hydroponic bays', 'Nutrient dosing systems'] },
      { category: 'Software Dev', items: ['NestJS / PostGIS backend engineers', 'Geospatial data scientists'] },
      { category: 'Capital', items: ['USDA farm operating loans', 'Impact-investment capital'] },
      { category: 'Labor', items: ['Farm managers', 'Composting technicians', 'Data operators'] },
    ]
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
    apiEndpoints: ['/api/bioreactor/status'],
    partnershipNeeds: [
      'Municipalities for plastic waste tipping-fee contracts',
      'Petrochemical companies as monomer off-takers',
      'Biotech research institutions for strain licensing',
      'Environmental regulators for pilot permits',
    ],
    affiliateOpportunities: [
      'Waste management and recycling companies',
      'Circular-economy advocacy organisations',
      'Corporate ESG / sustainability consultants',
      'Universities with bioengineering programmes',
    ],
    resourceNeeds: [
      { category: 'Labs', items: ['Biosafety Level 1 wet lab', 'Bioreactor vessels (10–500 L)', 'Analytical chemistry equipment'] },
      { category: 'Facilities', items: ['Industrial bioreactor hall', 'Feedstock pre-processing area'] },
      { category: 'Hardware', items: ['Industrial PLCs', 'pH / temperature sensors', 'Peristaltic pumps'] },
      { category: 'Capital', items: ['DOE / EPA grants for bio-remediation R&D', 'Equipment-leasing finance'] },
      { category: 'Labor', items: ['Bioprocess engineers', 'Microbiologists', 'PLC automation technicians'] },
      { category: 'Software Dev', items: ['Control-loop engineers (Python)', 'XGBoost ML data scientists'] },
    ]
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
    apiEndpoints: ['/api/foam-homes/status'],
    partnershipNeeds: [
      'Affordable-housing developers and non-profits',
      'Spray-foam insulation material suppliers',
      'Construction robotics companies',
      'Architects and parametric-design studios',
    ],
    affiliateOpportunities: [
      'Tiny-home and off-grid living communities',
      'Real estate investment trusts (REITs) focused on sustainability',
      'Green building material retailers',
      'Home builders and contractors networks',
    ],
    resourceNeeds: [
      { category: 'Architecture and Design', items: ['Parametric building designers (Grasshopper/Rhino)', 'Structural engineers', 'Interior designers'] },
      { category: 'Facilities', items: ['Robotic spray fabrication shed', 'Material storage yard'] },
      { category: 'Land', items: ['Zoned residential parcels', 'Community layout planning'] },
      { category: 'Software Dev', items: ['Three.js / WebGL 3D visualisation', 'NestJS BOM generation engine'] },
      { category: 'Hardware', items: ['CNC foam-cutting robots', 'On-site sensor rigs'] },
      { category: 'Capital', items: ['Construction finance', 'HUD / affordable-housing grants'] },
      { category: 'Labor', items: ['Construction foremen', 'Foam-spray operators', 'Electricians and plumbers'] },
    ]
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
    apiEndpoints: ['/api/geothermal/optimize'],
    partnershipNeeds: [
      'District-energy utility operators',
      'Geothermal drilling companies',
      'HVAC engineering firms for integration',
      'Municipal governments for long-term concession agreements',
    ],
    affiliateOpportunities: [
      'Green building certification consultants (LEED/BREEAM)',
      'Real estate developers building net-zero communities',
      'Heat-pump equipment distributors',
      'Energy-efficiency financing platforms',
    ],
    resourceNeeds: [
      { category: 'Land', items: ['Subsurface drilling rights', 'Utility corridor easements'] },
      { category: 'Facilities', items: ['Plant room for heat exchangers', 'Monitoring control centre'] },
      { category: 'Hardware', items: ['Ground-loop pipes', 'Heat-exchange units', 'Variable-flow pumps'] },
      { category: 'Capital', items: ['Infrastructure project-finance', 'Green bonds / PACE financing'] },
      { category: 'Software Dev', items: ['Go network optimisation engineers', 'Real-time SCADA dashboard'] },
      { category: 'Labor', items: ['Geothermal drilling crews', 'Mechanical / piping engineers'] },
    ]
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
    apiEndpoints: ['/api/solar/forecast'],
    partnershipNeeds: [
      'Community solar project developers',
      'Utility companies for virtual net metering',
      'Stripe / payment processors for subscriber billing',
      'Solar installation and EPC contractors',
    ],
    affiliateOpportunities: [
      'Rooftop solar referral networks',
      'Sustainable finance and green-banking platforms',
      'HOA and property-management companies',
      'Electric vehicle charging network operators',
    ],
    resourceNeeds: [
      { category: 'Hardware', items: ['Solar panels (bifacial)', 'String inverters', 'Smart meters'] },
      { category: 'Facilities', items: ['Carport / rooftop mounting structures', 'Electrical switchgear room'] },
      { category: 'Software Dev', items: ['Stripe billing integration', 'Irradiance forecasting ML', 'Subscriber portal (mobile)'] },
      { category: 'Capital', items: ['Solar project tax-equity financing', 'ITC / IRA investment-tax-credit structures'] },
      { category: 'Labor', items: ['Licensed electricians', 'Solar project managers'] },
    ]
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
    apiEndpoints: ['/api/hemp-lab/status'],
    partnershipNeeds: [
      'OEM automotive partners for material testing contracts',
      'Hemp fibre cultivation farms and processors',
      'University materials-science departments',
      'National labs with HPC simulation facilities',
    ],
    affiliateOpportunities: [
      'Sustainable automotive and EV communities',
      'Biocomposite material distributors',
      'Fleet electrification consultants',
      'Agri-industrial hemp growers associations',
    ],
    resourceNeeds: [
      { category: 'Labs', items: ['FEA / crash-testing simulation cluster (HPC)', 'Physical materials testing lab', 'Lifecycle assessment software (SimaPro)'] },
      { category: 'Hardware', items: ['3D composite lay-up equipment', 'On-vehicle sensor arrays'] },
      { category: 'Land', items: ['Hemp cultivation pilot plots (1–5 acres)'] },
      { category: 'Capital', items: ['SBIR / DOE grants for biocomposites R&D', 'VC funding for commercialisation'] },
      { category: 'Software Dev', items: ['WebGL / Three.js visualisation engineers', 'AWS Batch HPC job orchestration'] },
      { category: 'Labor', items: ['Materials scientists', 'Mechanical engineers', 'Hemp agronomists'] },
    ]
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
    apiEndpoints: ['/api/greenhouse/status'],
    partnershipNeeds: [
      'Commercial greenhouse and vertical-farm operators',
      'LED grow-light hardware manufacturers',
      'Botanical research institutions',
      'Cannabis / medicinal-herb licensed producers',
    ],
    affiliateOpportunities: [
      'Controlled-environment agriculture (CEA) communities',
      'Hydroponic supply retailers',
      'Plant-science educators and course creators',
      'Agri-tech investment syndicates',
    ],
    resourceNeeds: [
      { category: 'Hydroponics', items: ['NFT / DWC hydroponic channels', 'Nutrient reservoir systems', 'pH and EC controllers'] },
      { category: 'Facilities', items: ['Climate-controlled greenhouse', 'Dark-room calibration chamber'] },
      { category: 'Hardware', items: ['Custom LED frequency boards', 'Computer-vision cameras', 'Frequency generator circuits'] },
      { category: 'Labs', items: ['Plant-response measurement lab', 'Spectral analysis equipment'] },
      { category: 'Software Dev', items: ['Rust/C++ firmware engineers', 'Go control-loop developers', 'CV model training pipeline'] },
      { category: 'Capital', items: ['Hardware R&D seed funding', 'USDA specialty-crop grants'] },
      { category: 'Labor', items: ['Horticulturists', 'Electronics engineers', 'Computer-vision ML engineers'] },
    ]
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
    apiEndpoints: ['/api/reactor/status'],
    partnershipNeeds: [
      'Nuclear regulatory bodies (NRC, IAEA) for data-sharing agreements',
      'Utility companies for training-simulator licensing',
      'National nuclear laboratories (INL, ANL, ORNL)',
      'University nuclear-engineering departments',
    ],
    affiliateOpportunities: [
      'Nuclear energy advocacy organisations',
      'Clean-energy investment platforms',
      'Defence / national-security research contractors',
      'Advanced reactor developer consortia (TerraPower, X-energy)',
    ],
    resourceNeeds: [
      { category: 'Labs', items: ['HPC cluster for neutronics simulation', 'Validation test-data sets from NRC'] },
      { category: 'Software Dev', items: ['OpenMC neutronics engineers', 'Kafka streaming data pipeline', 'Python physics modelling team'] },
      { category: 'Capital', items: ['DOE Advanced Reactor Demonstration Programme funding', 'University research grants'] },
      { category: 'Facilities', items: ['Secure server room with redundant power', 'Collaborative simulation centre'] },
      { category: 'Labor', items: ['Nuclear engineers (PhD level)', 'Thermal-hydraulics modellers', 'Regulatory affairs specialists'] },
    ]
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
    apiEndpoints: [],
    partnershipNeeds: [
      'Molten-salt chemistry research institutions',
      'Thorium fuel-cycle technology developers',
      'Nuclear regulatory consultants',
      'Advanced materials suppliers (refractory alloys)',
    ],
    affiliateOpportunities: [
      'Next-gen nuclear investor networks',
      'Clean-energy policy think tanks',
      'Deep-tech accelerators and incubators',
      'University nuclear-engineering research partnerships',
    ],
    resourceNeeds: [
      { category: 'Labs', items: ['Corrosion-testing lab for molten-salt materials', 'Chemistry analysis equipment'] },
      { category: 'Capital', items: ['Long-term R&D endowment funding', 'ARPA-E grants'] },
      { category: 'Software Dev', items: ['Java Spring Boot simulation engine', 'C++ physics kernel team', 'Python thermo-chemistry modellers'] },
      { category: 'Facilities', items: ['Contained R&D lab (radiation shielding)', 'Secure data centre for simulation outputs'] },
      { category: 'Labor', items: ['Nuclear chemists', 'Materials engineers (high-temp alloys)', 'Regulatory strategy team'] },
    ]
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
