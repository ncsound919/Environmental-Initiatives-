/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CHEETAH v3 PRO - PHASE 3: ADVANCED SYSTEMS TEMPLATE
 * ═══════════════════════════════════════════════════════════════════════════════
 * Milestone: Professional Features
 * Components: PrefabManager, LightingEditor, PhysicsPanel, InputManager
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useCallback, useMemo, memo } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPE DEFINITIONS - PHASE 3
// ═══════════════════════════════════════════════════════════════════════════════

// Prefab Types
export interface Prefab {
  id: string;
  name: string;
  category: string;
  thumbnail: string;
  description: string;
  tags: string[];
  components: string[];
  variants: PrefabVariant[];
  createdAt: Date;
  modifiedAt: Date;
}

export interface PrefabVariant {
  id: string;
  name: string;
  overrides: Record<string, unknown>;
}

export interface GameObject {
  id: string;
  name: string;
  type: string;
  components: GameComponent[];
  children: GameObject[];
  transform: Transform;
}

export interface GameComponent {
  id: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface Transform {
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
}

// Lighting Types
export interface Light {
  id: string;
  name: string;
  type: 'directional' | 'point' | 'spot' | 'area';
  color: string;
  intensity: number;
  range?: number;
  spotAngle?: number;
  castShadows: boolean;
  shadowStrength: number;
  transform: Transform;
}

export interface LightingSettings {
  ambientColor: string;
  ambientIntensity: number;
  skyboxType: 'color' | 'gradient' | 'hdri' | 'procedural';
  skyboxSettings: Record<string, unknown>;
  fogEnabled: boolean;
  fogColor: string;
  fogDensity: number;
  shadowQuality: 'low' | 'medium' | 'high' | 'ultra';
  globalIllumination: boolean;
}

// Physics Types
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface PhysicsSettings {
  gravity: Vector3;
  fixedTimestep: number;
  maxSubsteps: number;
  solverIterations: number;
  bounceThreshold: number;
  sleepThreshold: number;
}

export interface PhysicsLayer {
  id: number;
  name: string;
  color: string;
}

export interface PhysicsMaterial {
  id: string;
  name: string;
  friction: number;
  bounciness: number;
  frictionCombine: 'average' | 'minimum' | 'maximum' | 'multiply';
  bounceCombine: 'average' | 'minimum' | 'maximum' | 'multiply';
}

// Input Types
export interface InputAction {
  id: string;
  name: string;
  displayName: string;
  bindings: InputBinding[];
  actionType: 'button' | 'axis' | 'vector2';
}

export interface InputBinding {
  id: string;
  device: 'keyboard' | 'mouse' | 'gamepad' | 'touch';
  path: string;
  modifiers: string[];
  processors: string[];
}

export interface InputMapping {
  id: string;
  name: string;
  actions: InputAction[];
  isDefault: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SHARED STYLES - PHASE 3
// ═══════════════════════════════════════════════════════════════════════════════

const phase3Styles = {
  panel: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
    backgroundColor: '#1e1e1e',
    color: '#d4d4d4',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '13px',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 14px',
    backgroundColor: '#2d2d2d',
    borderBottom: '1px solid #3d3d3d',
    minHeight: '44px',
  },
  title: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    fontWeight: 600,
    color: '#ffffff',
  },
  icon: {
    fontSize: '18px',
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  content: {
    flex: 1,
    overflow: 'auto',
    padding: '12px',
  },
  section: {
    marginBottom: '16px',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '8px 10px',
    backgroundColor: '#2a2a2a',
    borderRadius: '4px',
    marginBottom: '8px',
    cursor: 'pointer',
    userSelect: 'none' as const,
  },
  sectionTitle: {
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    color: '#9cdcfe',
  },
  button: {
    padding: '6px 12px',
    backgroundColor: '#0e639c',
    color: '#ffffff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 500,
    transition: 'background-color 0.2s',
  },
  buttonSecondary: {
    padding: '6px 12px',
    backgroundColor: 'transparent',
    color: '#d4d4d4',
    border: '1px solid #3d3d3d',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  iconButton: {
    padding: '6px 8px',
    backgroundColor: 'transparent',
    color: '#d4d4d4',
    border: '1px solid #3d3d3d',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  input: {
    padding: '6px 10px',
    backgroundColor: '#3c3c3c',
    color: '#d4d4d4',
    border: '1px solid #3d3d3d',
    borderRadius: '4px',
    fontSize: '13px',
    outline: 'none',
    width: '100%',
  },
  select: {
    padding: '6px 10px',
    backgroundColor: '#3c3c3c',
    color: '#d4d4d4',
    border: '1px solid #3d3d3d',
    borderRadius: '4px',
    fontSize: '13px',
    outline: 'none',
    cursor: 'pointer',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
    gap: '10px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  listItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 12px',
    backgroundColor: '#2a2a2a',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.15s',
  },
  listItemSelected: {
    backgroundColor: '#094771',
  },
  card: {
    backgroundColor: '#2a2a2a',
    borderRadius: '6px',
    padding: '12px',
    cursor: 'pointer',
    transition: 'all 0.15s',
    border: '2px solid transparent',
  },
  cardSelected: {
    borderColor: '#0e639c',
    backgroundColor: '#1e3a5f',
  },
  label: {
    fontSize: '11px',
    fontWeight: 500,
    color: '#888888',
    marginBottom: '4px',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  value: {
    fontSize: '13px',
    color: '#d4d4d4',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '8px',
  },
  badge: {
    padding: '2px 8px',
    backgroundColor: '#3d3d3d',
    borderRadius: '10px',
    fontSize: '11px',
    color: '#9cdcfe',
  },
  divider: {
    height: '1px',
    backgroundColor: '#3d3d3d',
    margin: '12px 0',
  },
  empty: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    color: '#666666',
    textAlign: 'center' as const,
  },
  emptyIcon: {
    fontSize: '48px',
    marginBottom: '16px',
    opacity: 0.5,
  },
  slider: {
    width: '100%',
    height: '4px',
    WebkitAppearance: 'none' as const,
    appearance: 'none' as const,
    backgroundColor: '#3d3d3d',
    borderRadius: '2px',
    outline: 'none',
    cursor: 'pointer',
  },
  colorSwatch: {
    width: '32px',
    height: '32px',
    borderRadius: '4px',
    border: '2px solid #3d3d3d',
    cursor: 'pointer',
  },
  vector3Input: {
    display: 'flex',
    gap: '6px',
  },
  vectorField: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  vectorLabel: {
    fontSize: '11px',
    fontWeight: 600,
    width: '14px',
  },
  vectorInput: {
    flex: 1,
    padding: '4px 6px',
    backgroundColor: '#3c3c3c',
    color: '#d4d4d4',
    border: '1px solid #3d3d3d',
    borderRadius: '3px',
    fontSize: '12px',
    outline: 'none',
    width: '60px',
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT 1: PREFAB MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

interface PrefabManagerProps {
  onPrefabSelect?: (prefab: Prefab) => void;
  onPrefabInstantiate?: (prefabId: string) => void;
  onPrefabCreate?: (object: GameObject) => void;
}

const mockPrefabs: Prefab[] = [
  {
    id: 'prefab-1',
    name: 'Player Character',
    category: 'Characters',
    thumbnail: '🧑',
    description: 'Default player character with movement and animation',
    tags: ['player', 'character', 'main'],
    components: ['Transform', 'SpriteRenderer', 'Animator', 'CharacterController'],
    variants: [
      { id: 'v1', name: 'Warrior', overrides: { class: 'warrior' } },
      { id: 'v2', name: 'Mage', overrides: { class: 'mage' } },
    ],
    createdAt: new Date('2024-01-15'),
    modifiedAt: new Date('2024-01-20'),
  },
  {
    id: 'prefab-2',
    name: 'Enemy Basic',
    category: 'Characters',
    thumbnail: '👾',
    description: 'Basic enemy with AI patrol behavior',
    tags: ['enemy', 'ai', 'combat'],
    components: ['Transform', 'SpriteRenderer', 'AIController', 'Health'],
    variants: [],
    createdAt: new Date('2024-01-10'),
    modifiedAt: new Date('2024-01-18'),
  },
  {
    id: 'prefab-3',
    name: 'Collectible Coin',
    category: 'Items',
    thumbnail: '🪙',
    description: 'Collectible coin with spinning animation',
    tags: ['item', 'collectible', 'currency'],
    components: ['Transform', 'SpriteRenderer', 'Collider2D', 'Collectible'],
    variants: [
      { id: 'v1', name: 'Gold', overrides: { value: 10 } },
      { id: 'v2', name: 'Silver', overrides: { value: 5 } },
    ],
    createdAt: new Date('2024-01-12'),
    modifiedAt: new Date('2024-01-12'),
  },
  {
    id: 'prefab-4',
    name: 'Platform',
    category: 'Environment',
    thumbnail: '🟫',
    description: 'Basic platform block',
    tags: ['platform', 'environment', 'ground'],
    components: ['Transform', 'SpriteRenderer', 'BoxCollider2D'],
    variants: [
      { id: 'v1', name: 'Grass', overrides: { material: 'grass' } },
      { id: 'v2', name: 'Stone', overrides: { material: 'stone' } },
    ],
    createdAt: new Date('2024-01-08'),
    modifiedAt: new Date('2024-01-19'),
  },
  {
    id: 'prefab-5',
    name: 'Particle Explosion',
    category: 'Effects',
    thumbnail: '💥',
    description: 'Explosion particle effect',
    tags: ['effect', 'particle', 'explosion'],
    components: ['Transform', 'ParticleSystem'],
    variants: [],
    createdAt: new Date('2024-01-14'),
    modifiedAt: new Date('2024-01-14'),
  },
  {
    id: 'prefab-6',
    name: 'UI Health Bar',
    category: 'UI',
    thumbnail: '❤️',
    description: 'Health bar UI element',
    tags: ['ui', 'health', 'hud'],
    components: ['RectTransform', 'Image', 'HealthBarController'],
    variants: [],
    createdAt: new Date('2024-01-16'),
    modifiedAt: new Date('2024-01-16'),
  },
];

const categories = ['All', 'Characters', 'Items', 'Environment', 'Effects', 'UI'];

export const PrefabManager: React.FC<PrefabManagerProps> = memo(({
  onPrefabSelect,
  onPrefabInstantiate,
  onPrefabCreate,
}) => {
  const [prefabs] = useState<Prefab[]>(mockPrefabs);
  const [selectedPrefab, setSelectedPrefab] = useState<Prefab | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const filteredPrefabs = useMemo(() => {
    return prefabs.filter(prefab => {
      const matchesSearch = prefab.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prefab.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesCategory = categoryFilter === 'All' || prefab.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [prefabs, searchQuery, categoryFilter]);

  const handlePrefabClick = useCallback((prefab: Prefab) => {
    setSelectedPrefab(prefab);
    onPrefabSelect?.(prefab);
  }, [onPrefabSelect]);

  const handleInstantiate = useCallback(() => {
    if (selectedPrefab) {
      onPrefabInstantiate?.(selectedPrefab.id);
    }
  }, [selectedPrefab, onPrefabInstantiate]);

  return (
    <div style={phase3Styles.panel}>
      {/* Header */}
      <div style={phase3Styles.header}>
        <div style={phase3Styles.title}>
          <span style={phase3Styles.icon}>📦</span>
          <span>Prefab Manager</span>
        </div>
        <div style={phase3Styles.toolbar}>
          <button
            style={phase3Styles.iconButton}
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            title={`Switch to ${viewMode === 'grid' ? 'list' : 'grid'} view`}
          >
            {viewMode === 'grid' ? '☰' : '⊞'}
          </button>
          <button style={phase3Styles.button} onClick={() => onPrefabCreate?.({} as GameObject)}>
            + New Prefab
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div style={{ padding: '10px 12px', borderBottom: '1px solid #3d3d3d' }}>
        <div style={{ marginBottom: '8px' }}>
          <input
            type="text"
            placeholder="Search prefabs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={phase3Styles.input}
          />
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              style={{
                ...phase3Styles.buttonSecondary,
                backgroundColor: categoryFilter === cat ? '#0e639c' : 'transparent',
                borderColor: categoryFilter === cat ? '#0e639c' : '#3d3d3d',
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={phase3Styles.content}>
        {filteredPrefabs.length === 0 ? (
          <div style={phase3Styles.empty}>
            <div style={phase3Styles.emptyIcon}>📦</div>
            <div>No prefabs found</div>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>
              Try adjusting your search or filter
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div style={phase3Styles.grid}>
            {filteredPrefabs.map(prefab => (
              <div
                key={prefab.id}
                onClick={() => handlePrefabClick(prefab)}
                onDoubleClick={handleInstantiate}
                style={{
                  ...phase3Styles.card,
                  ...(selectedPrefab?.id === prefab.id ? phase3Styles.cardSelected : {}),
                }}
              >
                <div style={{ fontSize: '36px', textAlign: 'center', marginBottom: '8px' }}>
                  {prefab.thumbnail}
                </div>
                <div style={{ fontWeight: 500, textAlign: 'center', marginBottom: '4px' }}>
                  {prefab.name}
                </div>
                <div style={{ fontSize: '11px', color: '#888', textAlign: 'center' }}>
                  {prefab.category}
                </div>
                {prefab.variants.length > 0 && (
                  <div style={{ ...phase3Styles.badge, marginTop: '6px', textAlign: 'center' }}>
                    {prefab.variants.length} variants
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={phase3Styles.list}>
            {filteredPrefabs.map(prefab => (
              <div
                key={prefab.id}
                onClick={() => handlePrefabClick(prefab)}
                onDoubleClick={handleInstantiate}
                style={{
                  ...phase3Styles.listItem,
                  ...(selectedPrefab?.id === prefab.id ? phase3Styles.listItemSelected : {}),
                }}
              >
                <span style={{ fontSize: '24px', marginRight: '12px' }}>{prefab.thumbnail}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{prefab.name}</div>
                  <div style={{ fontSize: '11px', color: '#888' }}>{prefab.description}</div>
                </div>
                <span style={phase3Styles.badge}>{prefab.category}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Prefab Details */}
      {selectedPrefab && (
        <div style={{ padding: '12px', borderTop: '1px solid #3d3d3d', backgroundColor: '#252525' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
            <div>
              <div style={{ fontWeight: 600, marginBottom: '4px' }}>{selectedPrefab.name}</div>
              <div style={{ fontSize: '11px', color: '#888' }}>{selectedPrefab.description}</div>
            </div>
            <button style={phase3Styles.button} onClick={handleInstantiate}>
              Instantiate
            </button>
          </div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {selectedPrefab.tags.map(tag => (
              <span key={tag} style={phase3Styles.badge}>{tag}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

PrefabManager.displayName = 'PrefabManager';

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT 2: LIGHTING EDITOR
// ═══════════════════════════════════════════════════════════════════════════════

interface LightingEditorProps {
  sceneId: string;
  onLightingChange?: (settings: LightingSettings) => void;
}

const mockLights: Light[] = [
  {
    id: 'light-1',
    name: 'Directional Light',
    type: 'directional',
    color: '#fffde7',
    intensity: 1.0,
    castShadows: true,
    shadowStrength: 0.8,
    transform: { position: { x: 0, y: 10, z: 0 }, rotation: { x: 50, y: -30, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
  },
  {
    id: 'light-2',
    name: 'Point Light',
    type: 'point',
    color: '#ff9800',
    intensity: 0.8,
    range: 10,
    castShadows: false,
    shadowStrength: 0.5,
    transform: { position: { x: 5, y: 3, z: 2 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
  },
  {
    id: 'light-3',
    name: 'Spot Light',
    type: 'spot',
    color: '#ffffff',
    intensity: 1.2,
    range: 15,
    spotAngle: 45,
    castShadows: true,
    shadowStrength: 0.7,
    transform: { position: { x: -3, y: 8, z: -1 }, rotation: { x: 90, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
  },
];

export const LightingEditor: React.FC<LightingEditorProps> = memo(({
  sceneId,
  onLightingChange,
}) => {
  const [lights, setLights] = useState<Light[]>(mockLights);
  const [selectedLight, setSelectedLight] = useState<Light | null>(null);
  const [ambientColor, setAmbientColor] = useState('#404040');
  const [ambientIntensity, setAmbientIntensity] = useState(0.5);
  const [skyboxType, setSkyboxType] = useState<'color' | 'gradient' | 'hdri' | 'procedural'>('gradient');
  const [shadowQuality, setShadowQuality] = useState<'low' | 'medium' | 'high' | 'ultra'>('medium');
  const [fogEnabled, setFogEnabled] = useState(false);
  const [fogColor, setFogColor] = useState('#808080');
  const [fogDensity, setFogDensity] = useState(0.01);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['lights', 'environment']));

  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  }, []);

  const handleLightSelect = useCallback((light: Light) => {
    setSelectedLight(light);
  }, []);

  const handleLightPropertyChange = useCallback((property: string, value: unknown) => {
    if (!selectedLight) return;

    setLights(prev => prev.map(light =>
      light.id === selectedLight.id
        ? { ...light, [property]: value }
        : light
    ));

    setSelectedLight(prev => prev ? { ...prev, [property]: value } : null);
  }, [selectedLight]);

  const handleAddLight = useCallback((type: Light['type']) => {
    const newLight: Light = {
      id: `light-${Date.now()}`,
      name: `New ${type.charAt(0).toUpperCase() + type.slice(1)} Light`,
      type,
      color: '#ffffff',
      intensity: 1.0,
      range: type === 'point' || type === 'spot' ? 10 : undefined,
      spotAngle: type === 'spot' ? 30 : undefined,
      castShadows: false,
      shadowStrength: 0.5,
      transform: { position: { x: 0, y: 5, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
    };
    setLights(prev => [...prev, newLight]);
    setSelectedLight(newLight);
  }, []);

  const lightTypeIcon = (type: Light['type']) => {
    switch (type) {
      case 'directional': return '☀️';
      case 'point': return '💡';
      case 'spot': return '🔦';
      case 'area': return '⬜';
      default: return '💡';
    }
  };

  return (
    <div style={phase3Styles.panel}>
      {/* Header */}
      <div style={phase3Styles.header}>
        <div style={phase3Styles.title}>
          <span style={phase3Styles.icon}>💡</span>
          <span>Lighting Editor</span>
        </div>
        <div style={phase3Styles.toolbar}>
          <select
            style={phase3Styles.select}
            onChange={(e) => handleAddLight(e.target.value as Light['type'])}
            value=""
          >
            <option value="" disabled>+ Add Light</option>
            <option value="directional">Directional</option>
            <option value="point">Point</option>
            <option value="spot">Spot</option>
            <option value="area">Area</option>
          </select>
        </div>
      </div>

      <div style={phase3Styles.content}>
        {/* Lights Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('lights')}
          >
            <span style={phase3Styles.sectionTitle}>Scene Lights ({lights.length})</span>
            <span>{expandedSections.has('lights') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('lights') && (
            <div style={phase3Styles.list}>
              {lights.map(light => (
                <div
                  key={light.id}
                  onClick={() => handleLightSelect(light)}
                  style={{
                    ...phase3Styles.listItem,
                    ...(selectedLight?.id === light.id ? phase3Styles.listItemSelected : {}),
                  }}
                >
                  <span style={{ marginRight: '10px' }}>{lightTypeIcon(light.type)}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500 }}>{light.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>
                      {light.type} • Intensity: {light.intensity.toFixed(2)}
                    </div>
                  </div>
                  <div
                    style={{
                      ...phase3Styles.colorSwatch,
                      backgroundColor: light.color,
                      width: '20px',
                      height: '20px',
                    }}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Light Properties */}
        {selectedLight && (
          <div style={phase3Styles.section}>
            <div style={phase3Styles.sectionHeader}>
              <span style={phase3Styles.sectionTitle}>Light Properties</span>
            </div>

            <div style={{ padding: '8px' }}>
              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Name</label>
                <input
                  type="text"
                  value={selectedLight.name}
                  onChange={(e) => handleLightPropertyChange('name', e.target.value)}
                  style={{ ...phase3Styles.input, flex: 2 }}
                />
              </div>

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Color</label>
                <input
                  type="color"
                  value={selectedLight.color}
                  onChange={(e) => handleLightPropertyChange('color', e.target.value)}
                  style={{ ...phase3Styles.colorSwatch, cursor: 'pointer' }}
                />
              </div>

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Intensity</label>
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={selectedLight.intensity}
                  onChange={(e) => handleLightPropertyChange('intensity', parseFloat(e.target.value))}
                  style={{ ...phase3Styles.slider, flex: 2 }}
                />
                <span style={{ width: '40px', textAlign: 'right' }}>{selectedLight.intensity.toFixed(1)}</span>
              </div>

              {(selectedLight.type === 'point' || selectedLight.type === 'spot') && (
                <div style={phase3Styles.row}>
                  <label style={{ ...phase3Styles.label, flex: 1 }}>Range</label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    step="0.5"
                    value={selectedLight.range || 10}
                    onChange={(e) => handleLightPropertyChange('range', parseFloat(e.target.value))}
                    style={{ ...phase3Styles.slider, flex: 2 }}
                  />
                  <span style={{ width: '40px', textAlign: 'right' }}>{(selectedLight.range || 10).toFixed(1)}</span>
                </div>
              )}

              {selectedLight.type === 'spot' && (
                <div style={phase3Styles.row}>
                  <label style={{ ...phase3Styles.label, flex: 1 }}>Spot Angle</label>
                  <input
                    type="range"
                    min="1"
                    max="179"
                    step="1"
                    value={selectedLight.spotAngle || 30}
                    onChange={(e) => handleLightPropertyChange('spotAngle', parseInt(e.target.value))}
                    style={{ ...phase3Styles.slider, flex: 2 }}
                  />
                  <span style={{ width: '40px', textAlign: 'right' }}>{selectedLight.spotAngle || 30}°</span>
                </div>
              )}

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Cast Shadows</label>
                <input
                  type="checkbox"
                  checked={selectedLight.castShadows}
                  onChange={(e) => handleLightPropertyChange('castShadows', e.target.checked)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Environment Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('environment')}
          >
            <span style={phase3Styles.sectionTitle}>Environment</span>
            <span>{expandedSections.has('environment') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('environment') && (
            <div style={{ padding: '8px' }}>
              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Ambient Color</label>
                <input
                  type="color"
                  value={ambientColor}
                  onChange={(e) => setAmbientColor(e.target.value)}
                  style={phase3Styles.colorSwatch}
                />
              </div>

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Ambient Intensity</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.05"
                  value={ambientIntensity}
                  onChange={(e) => setAmbientIntensity(parseFloat(e.target.value))}
                  style={{ ...phase3Styles.slider, flex: 2 }}
                />
                <span style={{ width: '40px', textAlign: 'right' }}>{ambientIntensity.toFixed(2)}</span>
              </div>

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Skybox</label>
                <select
                  value={skyboxType}
                  onChange={(e) => setSkyboxType(e.target.value as typeof skyboxType)}
                  style={{ ...phase3Styles.select, flex: 2 }}
                >
                  <option value="color">Solid Color</option>
                  <option value="gradient">Gradient</option>
                  <option value="hdri">HDRI</option>
                  <option value="procedural">Procedural</option>
                </select>
              </div>

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Shadow Quality</label>
                <select
                  value={shadowQuality}
                  onChange={(e) => setShadowQuality(e.target.value as typeof shadowQuality)}
                  style={{ ...phase3Styles.select, flex: 2 }}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="ultra">Ultra</option>
                </select>
              </div>

              <div style={phase3Styles.divider} />

              <div style={phase3Styles.row}>
                <label style={{ ...phase3Styles.label, flex: 1 }}>Enable Fog</label>
                <input
                  type="checkbox"
                  checked={fogEnabled}
                  onChange={(e) => setFogEnabled(e.target.checked)}
                />
              </div>

              {fogEnabled && (
                <>
                  <div style={phase3Styles.row}>
                    <label style={{ ...phase3Styles.label, flex: 1 }}>Fog Color</label>
                    <input
                      type="color"
                      value={fogColor}
                      onChange={(e) => setFogColor(e.target.value)}
                      style={phase3Styles.colorSwatch}
                    />
                  </div>

                  <div style={phase3Styles.row}>
                    <label style={{ ...phase3Styles.label, flex: 1 }}>Fog Density</label>
                    <input
                      type="range"
                      min="0"
                      max="0.1"
                      step="0.001"
                      value={fogDensity}
                      onChange={(e) => setFogDensity(parseFloat(e.target.value))}
                      style={{ ...phase3Styles.slider, flex: 2 }}
                    />
                    <span style={{ width: '40px', textAlign: 'right' }}>{fogDensity.toFixed(3)}</span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

LightingEditor.displayName = 'LightingEditor';

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT 3: PHYSICS PANEL
// ═══════════════════════════════════════════════════════════════════════════════

interface PhysicsPanelProps {
  onSettingsChange?: (settings: PhysicsSettings) => void;
  onSimulate?: () => void;
}

const defaultLayers: PhysicsLayer[] = [
  { id: 0, name: 'Default', color: '#4caf50' },
  { id: 1, name: 'Player', color: '#2196f3' },
  { id: 2, name: 'Enemy', color: '#f44336' },
  { id: 3, name: 'Ground', color: '#795548' },
  { id: 4, name: 'Projectile', color: '#ff9800' },
  { id: 5, name: 'Trigger', color: '#9c27b0' },
  { id: 6, name: 'UI', color: '#607d8b' },
  { id: 7, name: 'Ignore Raycast', color: '#9e9e9e' },
];

const defaultMaterials: PhysicsMaterial[] = [
  { id: 'mat-1', name: 'Default', friction: 0.4, bounciness: 0.0, frictionCombine: 'average', bounceCombine: 'average' },
  { id: 'mat-2', name: 'Bouncy', friction: 0.2, bounciness: 0.8, frictionCombine: 'average', bounceCombine: 'maximum' },
  { id: 'mat-3', name: 'Ice', friction: 0.02, bounciness: 0.0, frictionCombine: 'minimum', bounceCombine: 'average' },
  { id: 'mat-4', name: 'Rubber', friction: 0.8, bounciness: 0.6, frictionCombine: 'maximum', bounceCombine: 'maximum' },
];

export const PhysicsPanel: React.FC<PhysicsPanelProps> = memo(({
  onSettingsChange,
  onSimulate,
}) => {
  const [gravity, setGravity] = useState<Vector3>({ x: 0, y: -9.81, z: 0 });
  const [layers] = useState<PhysicsLayer[]>(defaultLayers);
  const [materials, setMaterials] = useState<PhysicsMaterial[]>(defaultMaterials);
  const [selectedLayer, setSelectedLayer] = useState(0);
  const [selectedMaterial, setSelectedMaterial] = useState<PhysicsMaterial | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [collisionMatrix, setCollisionMatrix] = useState<boolean[][]>(() => {
    return Array(8).fill(null).map(() => Array(8).fill(true));
  });
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['gravity', 'layers']));

  // Physics settings
  const [fixedTimestep, setFixedTimestep] = useState(0.02);
  const [solverIterations, setSolverIterations] = useState(6);
  const [bounceThreshold, setBounceThreshold] = useState(2);

  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  }, []);

  const handleGravityChange = useCallback((axis: 'x' | 'y' | 'z', value: number) => {
    setGravity(prev => ({ ...prev, [axis]: value }));
  }, []);

  const toggleCollision = useCallback((layer1: number, layer2: number) => {
    setCollisionMatrix(prev => {
      const next = prev.map(row => [...row]);
      next[layer1][layer2] = !next[layer1][layer2];
      next[layer2][layer1] = !next[layer2][layer1];
      return next;
    });
  }, []);

  const handleSimulate = useCallback(() => {
    setIsSimulating(prev => !prev);
    onSimulate?.();
  }, [onSimulate]);

  return (
    <div style={phase3Styles.panel}>
      {/* Header */}
      <div style={phase3Styles.header}>
        <div style={phase3Styles.title}>
          <span style={phase3Styles.icon}>⚡</span>
          <span>Physics</span>
        </div>
        <div style={phase3Styles.toolbar}>
          <button
            style={{
              ...phase3Styles.button,
              backgroundColor: isSimulating ? '#d32f2f' : '#4caf50',
            }}
            onClick={handleSimulate}
          >
            {isSimulating ? '⏹ Stop' : '▶ Simulate'}
          </button>
        </div>
      </div>

      <div style={phase3Styles.content}>
        {/* Gravity Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('gravity')}
          >
            <span style={phase3Styles.sectionTitle}>Gravity</span>
            <span>{expandedSections.has('gravity') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('gravity') && (
            <div style={{ padding: '8px' }}>
              <div style={phase3Styles.vector3Input}>
                {(['x', 'y', 'z'] as const).map(axis => (
                  <div key={axis} style={phase3Styles.vectorField}>
                    <span style={{
                      ...phase3Styles.vectorLabel,
                      color: axis === 'x' ? '#f44336' : axis === 'y' ? '#4caf50' : '#2196f3',
                    }}>
                      {axis.toUpperCase()}
                    </span>
                    <input
                      type="number"
                      step="0.1"
                      value={gravity[axis]}
                      onChange={(e) => handleGravityChange(axis, parseFloat(e.target.value) || 0)}
                      style={phase3Styles.vectorInput}
                    />
                  </div>
                ))}
              </div>

              <div style={{ marginTop: '12px' }}>
                <div style={phase3Styles.row}>
                  <label style={{ ...phase3Styles.label, flex: 1 }}>Fixed Timestep</label>
                  <input
                    type="number"
                    step="0.001"
                    value={fixedTimestep}
                    onChange={(e) => setFixedTimestep(parseFloat(e.target.value) || 0.02)}
                    style={{ ...phase3Styles.input, width: '80px' }}
                  />
                </div>

                <div style={phase3Styles.row}>
                  <label style={{ ...phase3Styles.label, flex: 1 }}>Solver Iterations</label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={solverIterations}
                    onChange={(e) => setSolverIterations(parseInt(e.target.value) || 6)}
                    style={{ ...phase3Styles.input, width: '80px' }}
                  />
                </div>

                <div style={phase3Styles.row}>
                  <label style={{ ...phase3Styles.label, flex: 1 }}>Bounce Threshold</label>
                  <input
                    type="number"
                    step="0.1"
                    value={bounceThreshold}
                    onChange={(e) => setBounceThreshold(parseFloat(e.target.value) || 2)}
                    style={{ ...phase3Styles.input, width: '80px' }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Layers Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('layers')}
          >
            <span style={phase3Styles.sectionTitle}>Layers ({layers.length})</span>
            <span>{expandedSections.has('layers') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('layers') && (
            <div style={phase3Styles.list}>
              {layers.map(layer => (
                <div
                  key={layer.id}
                  onClick={() => setSelectedLayer(layer.id)}
                  style={{
                    ...phase3Styles.listItem,
                    ...(selectedLayer === layer.id ? phase3Styles.listItemSelected : {}),
                  }}
                >
                  <div
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '2px',
                      backgroundColor: layer.color,
                      marginRight: '10px',
                    }}
                  />
                  <span style={{ flex: 1 }}>{layer.name}</span>
                  <span style={{ ...phase3Styles.badge, fontSize: '10px' }}>Layer {layer.id}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Collision Matrix Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('collision')}
          >
            <span style={phase3Styles.sectionTitle}>Collision Matrix</span>
            <span>{expandedSections.has('collision') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('collision') && (
            <div style={{ padding: '8px', overflowX: 'auto' }}>
              <div style={{ display: 'inline-block', minWidth: 'max-content' }}>
                {/* Header row */}
                <div style={{ display: 'flex', marginBottom: '2px' }}>
                  <div style={{ width: '80px' }} />
                  {layers.slice(0, 8).map(layer => (
                    <div
                      key={layer.id}
                      style={{
                        width: '24px',
                        height: '24px',
                        fontSize: '9px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transform: 'rotate(-45deg)',
                        marginLeft: '2px',
                      }}
                      title={layer.name}
                    >
                      {layer.name.slice(0, 3)}
                    </div>
                  ))}
                </div>

                {/* Matrix rows */}
                {layers.slice(0, 8).map((layer, i) => (
                  <div key={layer.id} style={{ display: 'flex', marginBottom: '2px' }}>
                    <div style={{
                      width: '80px',
                      fontSize: '11px',
                      display: 'flex',
                      alignItems: 'center',
                      paddingRight: '8px',
                    }}>
                      {layer.name}
                    </div>
                    {layers.slice(0, 8).map((_, j) => (
                      <div
                        key={j}
                        onClick={() => toggleCollision(i, j)}
                        style={{
                          width: '24px',
                          height: '24px',
                          backgroundColor: collisionMatrix[i][j] ? '#4caf50' : '#3d3d3d',
                          marginLeft: '2px',
                          borderRadius: '2px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '10px',
                          transition: 'background-color 0.15s',
                        }}
                      >
                        {collisionMatrix[i][j] ? '✓' : ''}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Physics Materials Section */}
        <div style={phase3Styles.section}>
          <div
            style={phase3Styles.sectionHeader}
            onClick={() => toggleSection('materials')}
          >
            <span style={phase3Styles.sectionTitle}>Physics Materials</span>
            <span>{expandedSections.has('materials') ? '▼' : '▶'}</span>
          </div>

          {expandedSections.has('materials') && (
            <div style={phase3Styles.list}>
              {materials.map(mat => (
                <div
                  key={mat.id}
                  onClick={() => setSelectedMaterial(mat)}
                  style={{
                    ...phase3Styles.listItem,
                    ...(selectedMaterial?.id === mat.id ? phase3Styles.listItemSelected : {}),
                  }}
                >
                  <span style={{ marginRight: '10px' }}>🧱</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500 }}>{mat.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>
                      Friction: {mat.friction.toFixed(2)} • Bounce: {mat.bounciness.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
              <button
                style={{ ...phase3Styles.buttonSecondary, width: '100%', marginTop: '8px' }}
              >
                + Add Material
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

PhysicsPanel.displayName = 'PhysicsPanel';

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT 4: INPUT MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

interface InputManagerProps {
  onMappingChange?: (mapping: InputMapping) => void;
  onActionAdd?: (action: InputAction) => void;
}

const defaultActions: InputAction[] = [
  {
    id: 'action-1',
    name: 'Move',
    displayName: 'Movement',
    actionType: 'vector2',
    bindings: [
      { id: 'b1', device: 'keyboard', path: 'WASD', modifiers: [], processors: [] },
      { id: 'b2', device: 'gamepad', path: 'Left Stick', modifiers: [], processors: [] },
    ],
  },
  {
    id: 'action-2',
    name: 'Jump',
    displayName: 'Jump',
    actionType: 'button',
    bindings: [
      { id: 'b3', device: 'keyboard', path: 'Space', modifiers: [], processors: [] },
      { id: 'b4', device: 'gamepad', path: 'South Button', modifiers: [], processors: [] },
    ],
  },
  {
    id: 'action-3',
    name: 'Attack',
    displayName: 'Primary Attack',
    actionType: 'button',
    bindings: [
      { id: 'b5', device: 'mouse', path: 'Left Button', modifiers: [], processors: [] },
      { id: 'b6', device: 'gamepad', path: 'Right Trigger', modifiers: [], processors: [] },
    ],
  },
  {
    id: 'action-4',
    name: 'Interact',
    displayName: 'Interact',
    actionType: 'button',
    bindings: [
      { id: 'b7', device: 'keyboard', path: 'E', modifiers: [], processors: [] },
      { id: 'b8', device: 'gamepad', path: 'West Button', modifiers: [], processors: [] },
    ],
  },
  {
    id: 'action-5',
    name: 'Look',
    displayName: 'Camera Look',
    actionType: 'vector2',
    bindings: [
      { id: 'b9', device: 'mouse', path: 'Delta', modifiers: [], processors: ['sensitivity'] },
      { id: 'b10', device: 'gamepad', path: 'Right Stick', modifiers: [], processors: ['deadzone'] },
    ],
  },
  {
    id: 'action-6',
    name: 'Pause',
    displayName: 'Pause Menu',
    actionType: 'button',
    bindings: [
      { id: 'b11', device: 'keyboard', path: 'Escape', modifiers: [], processors: [] },
      { id: 'b12', device: 'gamepad', path: 'Start', modifiers: [], processors: [] },
    ],
  },
];

export const InputManager: React.FC<InputManagerProps> = memo(({
  onMappingChange,
  onActionAdd,
}) => {
  const [actions, setActions] = useState<InputAction[]>(defaultActions);
  const [selectedAction, setSelectedAction] = useState<InputAction | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [listeningBindingId, setListeningBindingId] = useState<string | null>(null);
  const [deviceFilter, setDeviceFilter] = useState<'all' | 'keyboard' | 'gamepad' | 'mouse'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredActions = useMemo(() => {
    return actions.filter(action => {
      const matchesSearch = action.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        action.displayName.toLowerCase().includes(searchQuery.toLowerCase());

      if (deviceFilter === 'all') return matchesSearch;

      const hasDeviceBinding = action.bindings.some(b => b.device === deviceFilter);
      return matchesSearch && hasDeviceBinding;
    });
  }, [actions, searchQuery, deviceFilter]);

  const handleActionSelect = useCallback((action: InputAction) => {
    setSelectedAction(action);
  }, []);

  const startListening = useCallback((bindingId: string) => {
    setIsListening(true);
    setListeningBindingId(bindingId);

    // Simulate listening for 3 seconds then stop
    setTimeout(() => {
      setIsListening(false);
      setListeningBindingId(null);
    }, 3000);
  }, []);

  const handleAddAction = useCallback(() => {
    const newAction: InputAction = {
      id: `action-${Date.now()}`,
      name: 'NewAction',
      displayName: 'New Action',
      actionType: 'button',
      bindings: [],
    };
    setActions(prev => [...prev, newAction]);
    setSelectedAction(newAction);
    onActionAdd?.(newAction);
  }, [onActionAdd]);

  const handleAddBinding = useCallback(() => {
    if (!selectedAction) return;

    const newBinding: InputBinding = {
      id: `binding-${Date.now()}`,
      device: 'keyboard',
      path: 'Unassigned',
      modifiers: [],
      processors: [],
    };

    setActions(prev => prev.map(action =>
      action.id === selectedAction.id
        ? { ...action, bindings: [...action.bindings, newBinding] }
        : action
    ));

    setSelectedAction(prev =>
      prev ? { ...prev, bindings: [...prev.bindings, newBinding] } : null
    );
  }, [selectedAction]);

  const deviceIcon = (device: InputBinding['device']) => {
    switch (device) {
      case 'keyboard': return '⌨️';
      case 'mouse': return '🖱️';
      case 'gamepad': return '🎮';
      case 'touch': return '👆';
      default: return '❓';
    }
  };

  const actionTypeIcon = (type: InputAction['actionType']) => {
    switch (type) {
      case 'button': return '🔘';
      case 'axis': return '↔️';
      case 'vector2': return '🕹️';
      default: return '❓';
    }
  };

  return (
    <div style={phase3Styles.panel}>
      {/* Header */}
      <div style={phase3Styles.header}>
        <div style={phase3Styles.title}>
          <span style={phase3Styles.icon}>🎮</span>
          <span>Input Manager</span>
        </div>
        <div style={phase3Styles.toolbar}>
          <button style={phase3Styles.button} onClick={handleAddAction}>
            + Add Action
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div style={{ padding: '10px 12px', borderBottom: '1px solid #3d3d3d' }}>
        <div style={{ marginBottom: '8px' }}>
          <input
            type="text"
            placeholder="Search actions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={phase3Styles.input}
          />
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {(['all', 'keyboard', 'gamepad', 'mouse'] as const).map(device => (
            <button
              key={device}
              onClick={() => setDeviceFilter(device)}
              style={{
                ...phase3Styles.buttonSecondary,
                backgroundColor: deviceFilter === device ? '#0e639c' : 'transparent',
                borderColor: deviceFilter === device ? '#0e639c' : '#3d3d3d',
              }}
            >
              {device === 'all' ? '🔲 All' : `${deviceIcon(device)} ${device.charAt(0).toUpperCase() + device.slice(1)}`}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={phase3Styles.content}>
        {/* Actions List */}
        <div style={phase3Styles.section}>
          <div style={phase3Styles.sectionHeader}>
            <span style={phase3Styles.sectionTitle}>Input Actions ({filteredActions.length})</span>
          </div>

          <div style={phase3Styles.list}>
            {filteredActions.map(action => (
              <div
                key={action.id}
                onClick={() => handleActionSelect(action)}
                style={{
                  ...phase3Styles.listItem,
                  ...(selectedAction?.id === action.id ? phase3Styles.listItemSelected : {}),
                }}
              >
                <span style={{ marginRight: '10px' }}>{actionTypeIcon(action.actionType)}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{action.displayName}</div>
                  <div style={{ fontSize: '11px', color: '#888' }}>
                    {action.bindings.map(b => b.path).join(', ') || 'No bindings'}
                  </div>
                </div>
                <span style={phase3Styles.badge}>{action.actionType}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Action Bindings */}
        {selectedAction && (
          <div style={phase3Styles.section}>
            <div style={phase3Styles.sectionHeader}>
              <span style={phase3Styles.sectionTitle}>Bindings for "{selectedAction.displayName}"</span>
              <button style={phase3Styles.button} onClick={handleAddBinding}>
                + Add Binding
              </button>
            </div>

            <div style={phase3Styles.list}>
              {selectedAction.bindings.map(binding => (
                <div
                  key={binding.id}
                  style={{
                    ...phase3Styles.listItem,
                    ...(listeningBindingId === binding.id ? { backgroundColor: '#1e3a5f', borderColor: '#0e639c' } : {}),
                  }}
                >
                  <span style={{ marginRight: '10px', fontSize: '18px' }}>{deviceIcon(binding.device)}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500 }}>
                      {listeningBindingId === binding.id ? 'Press any key...' : binding.path}
                    </div>
                    <div style={{ fontSize: '11px', color: '#888' }}>
                      {binding.device}
                      {binding.modifiers.length > 0 && ` + ${binding.modifiers.join(' + ')}`}
                    </div>
                  </div>
                  <button
                    style={{
                      ...phase3Styles.buttonSecondary,
                      padding: '4px 8px',
                      fontSize: '11px',
                      backgroundColor: listeningBindingId === binding.id ? '#d32f2f' : 'transparent',
                    }}
                    onClick={() => listeningBindingId === binding.id ? setListeningBindingId(null) : startListening(binding.id)}
                  >
                    {listeningBindingId === binding.id ? 'Cancel' : 'Rebind'}
                  </button>
                </div>
              ))}

              {selectedAction.bindings.length === 0 && (
                <div style={phase3Styles.empty}>
                  <div style={phase3Styles.emptyIcon}>🎮</div>
                  <div>No bindings configured</div>
                  <div style={{ fontSize: '12px', marginTop: '4px' }}>
                    Click "Add Binding" to create one
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Listening overlay indicator */}
        {isListening && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
          }}>
            <div style={{
              backgroundColor: '#2a2a2a',
              padding: '32px 48px',
              borderRadius: '8px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '24px', marginBottom: '16px' }}>🎮</div>
              <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>Listening for input...</div>
              <div style={{ fontSize: '12px', color: '#888' }}>Press any key, button, or move an axis</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

InputManager.displayName = 'InputManager';

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  PrefabManager,
  LightingEditor,
  PhysicsPanel,
  InputManager,
};
