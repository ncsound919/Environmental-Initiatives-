/**
 * ============================================================================
 * PHASE 2: CREATIVE TOOLS TEMPLATE
 * ============================================================================
 * Milestone: Full Creative Suite
 * Components: TimelineEditor, MaterialEditor, ParticleEditor, AudioMixerPanel
 *
 * This template provides the blueprint for generating creative tool components
 * for the Overlay Game Maker UI system.
 * ============================================================================
 */

import React, { useState, useCallback, useMemo, memo, useRef, useEffect } from 'react';

// =============================================================================
// SHARED TYPES FOR CREATIVE TOOLS
// =============================================================================

export interface Keyframe {
  id: string;
  time: number;
  value: number;
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'bezier';
  property: string;
}

export interface AnimationTrack {
  id: string;
  name: string;
  property: string;
  keyframes: Keyframe[];
  color: string;
  locked: boolean;
  visible: boolean;
  expanded: boolean;
}

export interface Material {
  id: string;
  name: string;
  shaderType: 'standard' | 'unlit' | 'toon' | 'pbr' | 'custom';
  color: string;
  metallic: number;
  roughness: number;
  emission: string;
  emissionIntensity: number;
  textures: {
    albedo?: string;
    normal?: string;
    roughness?: string;
    metallic?: string;
    ao?: string;
    emission?: string;
  };
}

export interface ParticleModule {
  id: string;
  name: string;
  enabled: boolean;
  properties: Record<string, number | string | boolean>;
}

export interface ParticleSystem {
  id: string;
  name: string;
  duration: number;
  looping: boolean;
  startDelay: number;
  maxParticles: number;
  emissionRate: number;
  modules: ParticleModule[];
}

export interface AudioChannel {
  id: string;
  name: string;
  volume: number;
  pan: number;
  muted: boolean;
  solo: boolean;
  effects: string[];
  color: string;
}

// =============================================================================
// SHARED STYLES
// =============================================================================

const sharedStyles = {
  panel: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
    backgroundColor: '#1e1e2e',
    color: '#cdd6f4',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '13px',
    overflow: 'hidden',
    borderRadius: '8px',
    border: '1px solid #313244',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 14px',
    backgroundColor: '#181825',
    borderBottom: '1px solid #313244',
    minHeight: '44px',
  },
  title: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    fontWeight: 600,
    color: '#cdd6f4',
  },
  content: {
    flex: 1,
    overflow: 'auto',
    padding: '12px',
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '8px 12px',
    backgroundColor: '#11111b',
    borderBottom: '1px solid #313244',
  },
  button: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '4px',
    padding: '6px 10px',
    backgroundColor: '#313244',
    color: '#cdd6f4',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    transition: 'all 0.15s ease',
  },
  buttonPrimary: {
    backgroundColor: '#89b4fa',
    color: '#1e1e2e',
  },
  buttonActive: {
    backgroundColor: '#a6e3a1',
    color: '#1e1e2e',
  },
  input: {
    padding: '6px 10px',
    backgroundColor: '#313244',
    color: '#cdd6f4',
    border: '1px solid #45475a',
    borderRadius: '4px',
    fontSize: '12px',
    outline: 'none',
  },
  label: {
    fontSize: '11px',
    color: '#a6adc8',
    marginBottom: '4px',
  },
  slider: {
    width: '100%',
    height: '4px',
    backgroundColor: '#313244',
    borderRadius: '2px',
    appearance: 'none' as const,
    cursor: 'pointer',
  },
  iconButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '28px',
    height: '28px',
    backgroundColor: 'transparent',
    color: '#a6adc8',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
};

// =============================================================================
// TIMELINE EDITOR COMPONENT
// =============================================================================

export interface TimelineEditorProps {
  animationId?: string;
  duration?: number;
  onKeyframeAdd?: (time: number, property: string, value: number) => void;
  onKeyframeDelete?: (keyframeId: string) => void;
  onPlaybackChange?: (time: number) => void;
}

export const TimelineEditor: React.FC<TimelineEditorProps> = memo(({
  duration = 10,
  onKeyframeAdd,
  onKeyframeDelete,
  onPlaybackChange,
}) => {
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [selectedKeyframes, setSelectedKeyframes] = useState<string[]>([]);
  const [tracks, setTracks] = useState<AnimationTrack[]>([
    { id: '1', name: 'Position X', property: 'position.x', keyframes: [], color: '#f38ba8', locked: false, visible: true, expanded: true },
    { id: '2', name: 'Position Y', property: 'position.y', keyframes: [], color: '#a6e3a1', locked: false, visible: true, expanded: true },
    { id: '3', name: 'Rotation', property: 'rotation.z', keyframes: [], color: '#89b4fa', locked: false, visible: true, expanded: true },
    { id: '4', name: 'Scale', property: 'scale', keyframes: [], color: '#f9e2af', locked: false, visible: true, expanded: true },
  ]);

  const timelineRef = useRef<HTMLDivElement>(null);

  const handlePlay = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleStop = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    onPlaybackChange?.(0);
  }, [onPlaybackChange]);

  const handleTimeChange = useCallback((time: number) => {
    setCurrentTime(time);
    onPlaybackChange?.(time);
  }, [onPlaybackChange]);

  const handleAddKeyframe = useCallback((trackId: string, time: number) => {
    setTracks(prev => prev.map(track => {
      if (track.id === trackId) {
        const newKeyframe: Keyframe = {
          id: `kf_${Date.now()}`,
          time,
          value: 0,
          easing: 'ease-in-out',
          property: track.property,
        };
        onKeyframeAdd?.(time, track.property, 0);
        return { ...track, keyframes: [...track.keyframes, newKeyframe].sort((a, b) => a.time - b.time) };
      }
      return track;
    }));
  }, [onKeyframeAdd]);

  const timeMarkers = useMemo(() => {
    const markers = [];
    const step = zoom > 0.5 ? 1 : 2;
    for (let i = 0; i <= duration; i += step) {
      markers.push(i);
    }
    return markers;
  }, [duration, zoom]);

  return (
    <div style={sharedStyles.panel}>
      <div style={sharedStyles.header}>
        <div style={sharedStyles.title}>
          <span>⏱️</span>
          <span>Timeline Editor</span>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <span style={{ fontSize: '11px', color: '#a6adc8' }}>
            {currentTime.toFixed(2)}s / {duration}s
          </span>
        </div>
      </div>

      <div style={sharedStyles.toolbar}>
        <button
          style={{ ...sharedStyles.iconButton, ...(isPlaying ? sharedStyles.buttonActive : {}) }}
          onClick={handlePlay}
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>
        <button style={sharedStyles.iconButton} onClick={handleStop} title="Stop">
          ⏹️
        </button>
        <div style={{ width: '1px', height: '20px', backgroundColor: '#313244', margin: '0 8px' }} />
        <button style={sharedStyles.iconButton} title="First Frame">⏮️</button>
        <button style={sharedStyles.iconButton} title="Previous Frame">◀️</button>
        <button style={sharedStyles.iconButton} title="Next Frame">▶️</button>
        <button style={sharedStyles.iconButton} title="Last Frame">⏭️</button>
        <div style={{ width: '1px', height: '20px', backgroundColor: '#313244', margin: '0 8px' }} />
        <span style={{ fontSize: '11px', color: '#a6adc8' }}>Zoom:</span>
        <input
          type="range"
          min="0.25"
          max="4"
          step="0.25"
          value={zoom}
          onChange={(e) => setZoom(parseFloat(e.target.value))}
          style={{ ...sharedStyles.slider, width: '80px' }}
        />
        <span style={{ fontSize: '11px', color: '#a6adc8' }}>{(zoom * 100).toFixed(0)}%</span>
      </div>

      <div style={{ ...sharedStyles.content, padding: 0 }}>
        {/* Time ruler */}
        <div style={{ display: 'flex', borderBottom: '1px solid #313244' }}>
          <div style={{ width: '150px', minWidth: '150px', padding: '8px', backgroundColor: '#11111b' }}>
            <span style={{ fontSize: '11px', color: '#a6adc8' }}>Tracks</span>
          </div>
          <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
            <div style={{ display: 'flex', height: '28px', alignItems: 'flex-end', paddingBottom: '4px' }}>
              {timeMarkers.map(time => (
                <div
                  key={time}
                  style={{
                    position: 'absolute',
                    left: `${(time / duration) * 100 * zoom}%`,
                    fontSize: '10px',
                    color: '#6c7086',
                    transform: 'translateX(-50%)',
                  }}
                >
                  {time}s
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Tracks */}
        {tracks.map(track => (
          <div key={track.id} style={{ display: 'flex', borderBottom: '1px solid #313244' }}>
            <div
              style={{
                width: '150px',
                minWidth: '150px',
                padding: '8px',
                backgroundColor: '#181825',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: track.color }} />
              <span style={{ flex: 1, fontSize: '12px' }}>{track.name}</span>
              <button style={{ ...sharedStyles.iconButton, width: '20px', height: '20px', fontSize: '10px' }}>
                {track.visible ? '👁️' : '👁️‍🗨️'}
              </button>
              <button style={{ ...sharedStyles.iconButton, width: '20px', height: '20px', fontSize: '10px' }}>
                {track.locked ? '🔒' : '🔓'}
              </button>
            </div>
            <div
              ref={timelineRef}
              style={{
                flex: 1,
                height: '36px',
                position: 'relative',
                backgroundColor: '#1e1e2e',
                cursor: 'pointer',
              }}
              onDoubleClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const time = (x / rect.width) * duration / zoom;
                handleAddKeyframe(track.id, Math.max(0, Math.min(duration, time)));
              }}
            >
              {/* Playhead indicator */}
              <div
                style={{
                  position: 'absolute',
                  left: `${(currentTime / duration) * 100 * zoom}%`,
                  top: 0,
                  bottom: 0,
                  width: '2px',
                  backgroundColor: '#f38ba8',
                  zIndex: 10,
                }}
              />
              {/* Keyframes */}
              {track.keyframes.map(kf => (
                <div
                  key={kf.id}
                  style={{
                    position: 'absolute',
                    left: `${(kf.time / duration) * 100 * zoom}%`,
                    top: '50%',
                    transform: 'translate(-50%, -50%) rotate(45deg)',
                    width: '10px',
                    height: '10px',
                    backgroundColor: selectedKeyframes.includes(kf.id) ? '#f9e2af' : track.color,
                    cursor: 'pointer',
                    border: selectedKeyframes.includes(kf.id) ? '2px solid #fab387' : 'none',
                  }}
                  onClick={() => setSelectedKeyframes(prev =>
                    prev.includes(kf.id) ? prev.filter(id => id !== kf.id) : [...prev, kf.id]
                  )}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Add track button */}
        <div style={{ padding: '12px' }}>
          <button style={{ ...sharedStyles.button, width: '100%', justifyContent: 'center' }}>
            ➕ Add Track
          </button>
        </div>
      </div>
    </div>
  );
});

TimelineEditor.displayName = 'TimelineEditor';

// =============================================================================
// MATERIAL EDITOR COMPONENT
// =============================================================================

export interface MaterialEditorProps {
  materialId?: string;
  onMaterialChange?: (material: Material) => void;
  onTextureSelect?: (slot: string) => void;
}

export const MaterialEditor: React.FC<MaterialEditorProps> = memo(({
  onMaterialChange,
  onTextureSelect,
}) => {
  const [material, setMaterial] = useState<Material>({
    id: 'mat_default',
    name: 'Default Material',
    shaderType: 'standard',
    color: '#89b4fa',
    metallic: 0,
    roughness: 0.5,
    emission: '#000000',
    emissionIntensity: 0,
    textures: {},
  });
  const [previewMode, setPreviewMode] = useState<'sphere' | 'cube' | 'plane'>('sphere');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['base', 'textures']));

  const handlePropertyChange = useCallback((property: keyof Material, value: string | number) => {
    setMaterial(prev => {
      const updated = { ...prev, [property]: value };
      onMaterialChange?.(updated);
      return updated;
    });
  }, [onMaterialChange]);

  const toggleGroup = useCallback((group: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(group)) next.delete(group);
      else next.add(group);
      return next;
    });
  }, []);

  const textureSlots = [
    { key: 'albedo', label: 'Albedo', icon: '🎨' },
    { key: 'normal', label: 'Normal', icon: '🗺️' },
    { key: 'roughness', label: 'Roughness', icon: '📊' },
    { key: 'metallic', label: 'Metallic', icon: '⚙️' },
    { key: 'ao', label: 'Ambient Occlusion', icon: '🌑' },
    { key: 'emission', label: 'Emission', icon: '💡' },
  ];

  return (
    <div style={sharedStyles.panel}>
      <div style={sharedStyles.header}>
        <div style={sharedStyles.title}>
          <span>🎨</span>
          <span>Material Editor</span>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button style={sharedStyles.iconButton} title="Save">💾</button>
          <button style={sharedStyles.iconButton} title="Reset">🔄</button>
        </div>
      </div>

      <div style={sharedStyles.content}>
        {/* Preview */}
        <div style={{
          height: '150px',
          backgroundColor: '#11111b',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px',
          border: '1px solid #313244',
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: previewMode === 'sphere' ? '50%' : '8px',
            background: `linear-gradient(135deg, ${material.color} 0%, ${material.color}88 100%)`,
            boxShadow: `0 4px 20px ${material.color}44`,
          }} />
        </div>

        {/* Preview mode selector */}
        <div style={{ display: 'flex', gap: '4px', marginBottom: '16px' }}>
          {(['sphere', 'cube', 'plane'] as const).map(mode => (
            <button
              key={mode}
              style={{
                ...sharedStyles.button,
                flex: 1,
                ...(previewMode === mode ? sharedStyles.buttonActive : {}),
              }}
              onClick={() => setPreviewMode(mode)}
            >
              {mode === 'sphere' ? '⚪' : mode === 'cube' ? '🔲' : '⬜'} {mode}
            </button>
          ))}
        </div>

        {/* Base Properties */}
        <div style={{ marginBottom: '12px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 0',
              cursor: 'pointer',
            }}
            onClick={() => toggleGroup('base')}
          >
            <span>{expandedGroups.has('base') ? '▼' : '▶'}</span>
            <span style={{ fontWeight: 600 }}>Base Properties</span>
          </div>
          {expandedGroups.has('base') && (
            <div style={{ paddingLeft: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={sharedStyles.label}>Name</label>
                <input
                  style={{ ...sharedStyles.input, width: '100%' }}
                  value={material.name}
                  onChange={(e) => handlePropertyChange('name', e.target.value)}
                />
              </div>
              <div>
                <label style={sharedStyles.label}>Shader Type</label>
                <select
                  style={{ ...sharedStyles.input, width: '100%' }}
                  value={material.shaderType}
                  onChange={(e) => handlePropertyChange('shaderType', e.target.value)}
                >
                  <option value="standard">Standard</option>
                  <option value="unlit">Unlit</option>
                  <option value="toon">Toon</option>
                  <option value="pbr">PBR</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label style={sharedStyles.label}>Color</label>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={material.color}
                    onChange={(e) => handlePropertyChange('color', e.target.value)}
                    style={{ width: '40px', height: '32px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    style={{ ...sharedStyles.input, flex: 1 }}
                    value={material.color}
                    onChange={(e) => handlePropertyChange('color', e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label style={sharedStyles.label}>Metallic: {material.metallic.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={material.metallic}
                  onChange={(e) => handlePropertyChange('metallic', parseFloat(e.target.value))}
                  style={{ ...sharedStyles.slider, width: '100%' }}
                />
              </div>
              <div>
                <label style={sharedStyles.label}>Roughness: {material.roughness.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={material.roughness}
                  onChange={(e) => handlePropertyChange('roughness', parseFloat(e.target.value))}
                  style={{ ...sharedStyles.slider, width: '100%' }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Textures */}
        <div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 0',
              cursor: 'pointer',
            }}
            onClick={() => toggleGroup('textures')}
          >
            <span>{expandedGroups.has('textures') ? '▼' : '▶'}</span>
            <span style={{ fontWeight: 600 }}>Texture Maps</span>
          </div>
          {expandedGroups.has('textures') && (
            <div style={{ paddingLeft: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {textureSlots.map(slot => (
                <div
                  key={slot.key}
                  style={{
                    padding: '12px',
                    backgroundColor: '#181825',
                    borderRadius: '6px',
                    border: '1px dashed #45475a',
                    cursor: 'pointer',
                    textAlign: 'center',
                  }}
                  onClick={() => onTextureSelect?.(slot.key)}
                >
                  <div style={{ fontSize: '20px', marginBottom: '4px' }}>{slot.icon}</div>
                  <div style={{ fontSize: '11px', color: '#a6adc8' }}>{slot.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

MaterialEditor.displayName = 'MaterialEditor';

// =============================================================================
// PARTICLE EDITOR COMPONENT
// =============================================================================

export interface ParticleEditorProps {
  particleSystemId?: string;
  onSystemChange?: (system: ParticleSystem) => void;
}

export const ParticleEditor: React.FC<ParticleEditorProps> = memo(({
  onSystemChange,
}) => {
  const [system, setSystem] = useState<ParticleSystem>({
    id: 'ps_default',
    name: 'Particle System',
    duration: 5,
    looping: true,
    startDelay: 0,
    maxParticles: 1000,
    emissionRate: 50,
    modules: [
      { id: 'emission', name: 'Emission', enabled: true, properties: { rate: 50, bursts: 0 } },
      { id: 'shape', name: 'Shape', enabled: true, properties: { type: 'cone', angle: 25, radius: 1 } },
      { id: 'velocity', name: 'Velocity over Lifetime', enabled: false, properties: { x: 0, y: 1, z: 0 } },
      { id: 'color', name: 'Color over Lifetime', enabled: true, properties: { start: '#f38ba8', end: '#f9e2af' } },
      { id: 'size', name: 'Size over Lifetime', enabled: true, properties: { start: 1, end: 0 } },
      { id: 'rotation', name: 'Rotation over Lifetime', enabled: false, properties: { speed: 0 } },
      { id: 'noise', name: 'Noise', enabled: false, properties: { strength: 0.5, frequency: 1 } },
      { id: 'collision', name: 'Collision', enabled: false, properties: { bounce: 0.5, lifetime_loss: 0.1 } },
    ],
  });
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedModule, setSelectedModule] = useState('emission');
  const [particleCount, setParticleCount] = useState(0);

  useEffect(() => {
    if (isSimulating) {
      const interval = setInterval(() => {
        setParticleCount(prev => Math.min(prev + Math.floor(Math.random() * 10), system.maxParticles));
      }, 100);
      return () => clearInterval(interval);
    } else {
      setParticleCount(0);
    }
  }, [isSimulating, system.maxParticles]);

  const toggleModule = useCallback((moduleId: string) => {
    setSystem(prev => {
      const updated = {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId ? { ...m, enabled: !m.enabled } : m
        ),
      };
      onSystemChange?.(updated);
      return updated;
    });
  }, [onSystemChange]);

  const selectedModuleData = system.modules.find(m => m.id === selectedModule);

  return (
    <div style={sharedStyles.panel}>
      <div style={sharedStyles.header}>
        <div style={sharedStyles.title}>
          <span>✨</span>
          <span>Particle Editor</span>
        </div>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: '#a6adc8' }}>
            Particles: {particleCount} / {system.maxParticles}
          </span>
        </div>
      </div>

      <div style={sharedStyles.toolbar}>
        <button
          style={{ ...sharedStyles.button, ...(isSimulating ? sharedStyles.buttonActive : {}) }}
          onClick={() => setIsSimulating(!isSimulating)}
        >
          {isSimulating ? '⏹️ Stop' : '▶️ Simulate'}
        </button>
        <button style={sharedStyles.button} onClick={() => setParticleCount(0)}>
          🔄 Restart
        </button>
        <div style={{ flex: 1 }} />
        <button style={sharedStyles.iconButton} title="Save Preset">💾</button>
        <button style={sharedStyles.iconButton} title="Load Preset">📂</button>
      </div>

      <div style={{ ...sharedStyles.content, padding: 0, display: 'flex' }}>
        {/* Preview */}
        <div style={{
          width: '40%',
          minWidth: '150px',
          backgroundColor: '#11111b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRight: '1px solid #313244',
          position: 'relative',
        }}>
          {/* Simulated particles */}
          {isSimulating && Array.from({ length: Math.min(particleCount, 50) }).map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                width: `${4 + Math.random() * 4}px`,
                height: `${4 + Math.random() * 4}px`,
                borderRadius: '50%',
                backgroundColor: '#f38ba8',
                opacity: Math.random() * 0.8 + 0.2,
                left: `${40 + (Math.random() - 0.5) * 60}%`,
                top: `${70 - Math.random() * 50}%`,
                animation: 'float 1s ease-out infinite',
              }}
            />
          ))}
          {!isSimulating && (
            <span style={{ color: '#6c7086' }}>Click Simulate to preview</span>
          )}
        </div>

        {/* Modules list */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          <div style={{ padding: '12px' }}>
            <div style={{ marginBottom: '16px' }}>
              <label style={sharedStyles.label}>System Name</label>
              <input
                style={{ ...sharedStyles.input, width: '100%' }}
                value={system.name}
                onChange={(e) => setSystem(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
              <div style={{ flex: 1 }}>
                <label style={sharedStyles.label}>Duration</label>
                <input
                  type="number"
                  style={{ ...sharedStyles.input, width: '100%' }}
                  value={system.duration}
                  onChange={(e) => setSystem(prev => ({ ...prev, duration: parseFloat(e.target.value) }))}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={sharedStyles.label}>Max Particles</label>
                <input
                  type="number"
                  style={{ ...sharedStyles.input, width: '100%' }}
                  value={system.maxParticles}
                  onChange={(e) => setSystem(prev => ({ ...prev, maxParticles: parseInt(e.target.value) }))}
                />
              </div>
            </div>

            <div style={{ marginBottom: '8px' }}>
              <label style={{ ...sharedStyles.label, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={system.looping}
                  onChange={(e) => setSystem(prev => ({ ...prev, looping: e.target.checked }))}
                />
                Looping
              </label>
            </div>

            <div style={{ borderTop: '1px solid #313244', paddingTop: '12px', marginTop: '12px' }}>
              <span style={{ fontWeight: 600, marginBottom: '8px', display: 'block' }}>Modules</span>
              {system.modules.map(module => (
                <div
                  key={module.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px',
                    backgroundColor: selectedModule === module.id ? '#313244' : 'transparent',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginBottom: '4px',
                  }}
                  onClick={() => setSelectedModule(module.id)}
                >
                  <input
                    type="checkbox"
                    checked={module.enabled}
                    onChange={() => toggleModule(module.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span style={{ flex: 1, opacity: module.enabled ? 1 : 0.5 }}>{module.name}</span>
                  <span style={{ fontSize: '10px', color: '#6c7086' }}>▶</span>
                </div>
              ))}
            </div>

            {/* Module Properties */}
            {selectedModuleData && (
              <div style={{ borderTop: '1px solid #313244', paddingTop: '12px', marginTop: '12px' }}>
                <span style={{ fontWeight: 600, marginBottom: '8px', display: 'block' }}>
                  {selectedModuleData.name} Properties
                </span>
                {Object.entries(selectedModuleData.properties).map(([key, value]) => (
                  <div key={key} style={{ marginBottom: '8px' }}>
                    <label style={sharedStyles.label}>{key}</label>
                    {typeof value === 'number' ? (
                      <input
                        type="number"
                        style={{ ...sharedStyles.input, width: '100%' }}
                        value={value}
                        onChange={() => {}}
                      />
                    ) : typeof value === 'string' && value.startsWith('#') ? (
                      <input
                        type="color"
                        value={value}
                        onChange={() => {}}
                        style={{ width: '100%', height: '32px' }}
                      />
                    ) : (
                      <input
                        style={{ ...sharedStyles.input, width: '100%' }}
                        value={String(value)}
                        onChange={() => {}}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

ParticleEditor.displayName = 'ParticleEditor';

// =============================================================================
// AUDIO MIXER PANEL COMPONENT
// =============================================================================

export interface AudioMixerPanelProps {
  onVolumeChange?: (channel: string, volume: number) => void;
  onMute?: (channel: string) => void;
  onSolo?: (channel: string) => void;
}

export const AudioMixerPanel: React.FC<AudioMixerPanelProps> = memo(({
  onVolumeChange,
  onMute,
  onSolo,
}) => {
  const [channels, setChannels] = useState<AudioChannel[]>([
    { id: 'master', name: 'Master', volume: 0.8, pan: 0, muted: false, solo: false, effects: [], color: '#f38ba8' },
    { id: 'music', name: 'Music', volume: 0.7, pan: 0, muted: false, solo: false, effects: ['EQ', 'Compressor'], color: '#89b4fa' },
    { id: 'sfx', name: 'SFX', volume: 0.9, pan: 0, muted: false, solo: false, effects: ['Reverb'], color: '#a6e3a1' },
    { id: 'voice', name: 'Voice', volume: 0.85, pan: 0, muted: false, solo: false, effects: ['EQ', 'Limiter'], color: '#f9e2af' },
    { id: 'ambient', name: 'Ambient', volume: 0.5, pan: 0, muted: false, solo: false, effects: ['Reverb', 'Delay'], color: '#cba6f7' },
  ]);
  const [masterVolume, setMasterVolume] = useState(1);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleVolumeChange = useCallback((channelId: string, volume: number) => {
    setChannels(prev => prev.map(ch =>
      ch.id === channelId ? { ...ch, volume } : ch
    ));
    onVolumeChange?.(channelId, volume);
  }, [onVolumeChange]);

  const handleMute = useCallback((channelId: string) => {
    setChannels(prev => prev.map(ch =>
      ch.id === channelId ? { ...ch, muted: !ch.muted } : ch
    ));
    onMute?.(channelId);
  }, [onMute]);

  const handleSolo = useCallback((channelId: string) => {
    setChannels(prev => prev.map(ch =>
      ch.id === channelId ? { ...ch, solo: !ch.solo } : ch
    ));
    onSolo?.(channelId);
  }, [onSolo]);

  const volumeToDb = (volume: number): string => {
    if (volume === 0) return '-∞';
    const db = 20 * Math.log10(volume);
    return db.toFixed(1);
  };

  return (
    <div style={sharedStyles.panel}>
      <div style={sharedStyles.header}>
        <div style={sharedStyles.title}>
          <span>🎵</span>
          <span>Audio Mixer</span>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            style={{ ...sharedStyles.iconButton, ...(isPlaying ? sharedStyles.buttonActive : {}) }}
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? '⏹️' : '▶️'}
          </button>
        </div>
      </div>

      <div style={sharedStyles.toolbar}>
        <span style={{ fontSize: '11px', color: '#a6adc8' }}>Master:</span>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={masterVolume}
          onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
          style={{ ...sharedStyles.slider, width: '100px' }}
        />
        <span style={{ fontSize: '11px', color: '#a6adc8', minWidth: '45px' }}>
          {volumeToDb(masterVolume)} dB
        </span>
        <div style={{ flex: 1 }} />
        <button style={sharedStyles.button}>➕ Add Channel</button>
      </div>

      <div style={{ ...sharedStyles.content, display: 'flex', gap: '8px', overflowX: 'auto' }}>
        {channels.map(channel => (
          <div
            key={channel.id}
            style={{
              width: '80px',
              minWidth: '80px',
              backgroundColor: selectedChannel === channel.id ? '#313244' : '#181825',
              borderRadius: '8px',
              padding: '12px 8px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              border: `1px solid ${selectedChannel === channel.id ? channel.color : '#313244'}`,
            }}
            onClick={() => setSelectedChannel(channel.id)}
          >
            {/* Channel name */}
            <span style={{ fontSize: '11px', fontWeight: 600, color: channel.color }}>
              {channel.name}
            </span>

            {/* Level meter (simulated) */}
            <div style={{
              width: '20px',
              height: '120px',
              backgroundColor: '#11111b',
              borderRadius: '4px',
              position: 'relative',
              overflow: 'hidden',
            }}>
              <div style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: `${channel.volume * 100 * (isPlaying ? (0.7 + Math.random() * 0.3) : 1)}%`,
                background: `linear-gradient(to top, ${channel.color}, ${channel.color}88)`,
                transition: 'height 0.1s',
                opacity: channel.muted ? 0.3 : 1,
              }} />
            </div>

            {/* Fader */}
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={channel.volume}
              onChange={(e) => handleVolumeChange(channel.id, parseFloat(e.target.value))}
              style={{
                ...sharedStyles.slider,
                width: '60px',
                writingMode: 'vertical-lr',
                direction: 'rtl',
                height: '80px',
              }}
            />

            {/* Volume display */}
            <span style={{ fontSize: '10px', color: '#a6adc8' }}>
              {volumeToDb(channel.volume)} dB
            </span>

            {/* Pan control */}
            <input
              type="range"
              min="-1"
              max="1"
              step="0.1"
              value={channel.pan}
              onChange={(e) => setChannels(prev => prev.map(ch =>
                ch.id === channel.id ? { ...ch, pan: parseFloat(e.target.value) } : ch
              ))}
              style={{ ...sharedStyles.slider, width: '60px' }}
            />
            <span style={{ fontSize: '9px', color: '#6c7086' }}>
              {channel.pan === 0 ? 'C' : channel.pan < 0 ? `L${Math.abs(channel.pan * 100).toFixed(0)}` : `R${(channel.pan * 100).toFixed(0)}`}
            </span>

            {/* Mute/Solo buttons */}
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                style={{
                  ...sharedStyles.iconButton,
                  width: '24px',
                  height: '24px',
                  fontSize: '10px',
                  backgroundColor: channel.muted ? '#f38ba8' : 'transparent',
                  color: channel.muted ? '#1e1e2e' : '#a6adc8',
                }}
                onClick={(e) => { e.stopPropagation(); handleMute(channel.id); }}
                title="Mute"
              >
                M
              </button>
              <button
                style={{
                  ...sharedStyles.iconButton,
                  width: '24px',
                  height: '24px',
                  fontSize: '10px',
                  backgroundColor: channel.solo ? '#f9e2af' : 'transparent',
                  color: channel.solo ? '#1e1e2e' : '#a6adc8',
                }}
                onClick={(e) => { e.stopPropagation(); handleSolo(channel.id); }}
                title="Solo"
              >
                S
              </button>
            </div>

            {/* Effects indicator */}
            {channel.effects.length > 0 && (
              <div style={{ fontSize: '9px', color: '#6c7086', textAlign: 'center' }}>
                {channel.effects.length} FX
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Selected channel details */}
      {selectedChannel && (
        <div style={{
          padding: '12px',
          backgroundColor: '#181825',
          borderTop: '1px solid #313244',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontWeight: 600 }}>
              {channels.find(c => c.id === selectedChannel)?.name} Effects
            </span>
            <button style={sharedStyles.button}>➕ Add Effect</button>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {channels.find(c => c.id === selectedChannel)?.effects.map((effect, i) => (
              <div
                key={i}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#313244',
                  borderRadius: '4px',
                  fontSize: '11px',
                }}
              >
                {effect}
              </div>
            ))}
            {channels.find(c => c.id === selectedChannel)?.effects.length === 0 && (
              <span style={{ fontSize: '11px', color: '#6c7086' }}>No effects</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

AudioMixerPanel.displayName = 'AudioMixerPanel';

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  TimelineEditor,
  MaterialEditor,
  ParticleEditor,
  AudioMixerPanel,
};
