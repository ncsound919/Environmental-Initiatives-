/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CHEETAH v3 PRO - PHASE 1: CORE EDITOR PANELS TEMPLATE
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Phase 1 Milestone: Full Editor Layout
 * Components: SceneHierarchyPanel, InspectorPanel, ConsolePanel, ToolbarPanel
 *
 * This template provides the foundational structure for core editor UI panels.
 * Each component follows a consistent pattern for rapid generation.
 *
 * Usage:
 *   - Copy the desired component template section
 *   - Replace {{COMPONENT_NAME}} placeholders
 *   - Customize state and handlers as needed
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useCallback, useMemo, memo } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// SHARED TYPES FOR PHASE 1
// ═══════════════════════════════════════════════════════════════════════════════

export interface GameObject {
  id: string;
  name: string;
  type: string;
  parentId: string | null;
  children: string[];
  components: GameComponent[];
  transform: Transform;
  isActive: boolean;
  isLocked: boolean;
  isVisible: boolean;
}

export interface GameComponent {
  id: string;
  type: string;
  name: string;
  enabled: boolean;
  properties: Record<string, unknown>;
}

export interface Transform {
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  scale: { x: number; y: number; z: number };
}

export interface ConsoleLog {
  id: string;
  type: 'log' | 'warn' | 'error' | 'info';
  message: string;
  timestamp: Date;
  stackTrace?: string;
  count: number;
}

export type EditorTool = 'select' | 'move' | 'rotate' | 'scale' | 'rect' | 'hand';

// ═══════════════════════════════════════════════════════════════════════════════
// SHARED STYLES FOR PHASE 1
// ═══════════════════════════════════════════════════════════════════════════════

const phase1BaseStyles = {
  panel: {
    display: 'flex',
    flexDirection: 'column' as const,
    backgroundColor: '#1e1e2e',
    borderRadius: '8px',
    border: '1px solid #313244',
    overflow: 'hidden',
    height: '100%',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 12px',
    backgroundColor: '#181825',
    borderBottom: '1px solid #313244',
    minHeight: '40px',
  },
  headerTitle: {
    margin: 0,
    fontSize: '13px',
    fontWeight: 600,
    color: '#cdd6f4',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  content: {
    flex: 1,
    padding: '8px',
    overflowY: 'auto' as const,
    overflowX: 'hidden' as const,
  },
  button: {
    padding: '4px 8px',
    backgroundColor: 'transparent',
    border: '1px solid #45475a',
    borderRadius: '4px',
    color: '#cdd6f4',
    cursor: 'pointer',
    fontSize: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    transition: 'all 0.15s ease',
  },
  buttonActive: {
    backgroundColor: '#89b4fa',
    borderColor: '#89b4fa',
    color: '#1e1e2e',
  },
  input: {
    width: '100%',
    padding: '6px 10px',
    backgroundColor: '#313244',
    border: '1px solid #45475a',
    borderRadius: '4px',
    color: '#cdd6f4',
    fontSize: '12px',
    outline: 'none',
  },
  listItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '6px 8px',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background 0.15s ease',
    gap: '8px',
  },
  listItemSelected: {
    backgroundColor: '#45475a',
  },
  divider: {
    height: '1px',
    backgroundColor: '#313244',
    margin: '8px 0',
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 1: SCENE HIERARCHY PANEL 🌳
// ═══════════════════════════════════════════════════════════════════════════════

interface SceneHierarchyPanelProps {
  sceneId: string;
  onObjectSelect?: (object: GameObject) => void;
  onObjectRename?: (id: string, name: string) => void;
  onObjectDelete?: (id: string) => void;
  onObjectDuplicate?: (id: string) => void;
}

export const SceneHierarchyPanelTemplate = memo<SceneHierarchyPanelProps>(({
  sceneId,
  onObjectSelect,
  onObjectRename,
  onObjectDelete,
  onObjectDuplicate,
}) => {
  // State
  const [objects, setObjects] = useState<GameObject[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedItem, setDraggedItem] = useState<string | null>(null);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; objectId: string } | null>(null);

  // Mock data initialization
  React.useEffect(() => {
    setObjects([
      {
        id: '1', name: 'Main Camera', type: 'camera', parentId: null, children: [],
        components: [], transform: { position: { x: 0, y: 0, z: -10 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
        isActive: true, isLocked: false, isVisible: true,
      },
      {
        id: '2', name: 'Player', type: 'gameobject', parentId: null, children: ['3'],
        components: [], transform: { position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
        isActive: true, isLocked: false, isVisible: true,
      },
      {
        id: '3', name: 'Sprite', type: 'sprite', parentId: '2', children: [],
        components: [], transform: { position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 } },
        isActive: true, isLocked: false, isVisible: true,
      },
    ]);
  }, [sceneId]);

  // Handlers
  const handleToggleExpand = useCallback((id: string) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const handleSelect = useCallback((object: GameObject) => {
    setSelectedId(object.id);
    onObjectSelect?.(object);
  }, [onObjectSelect]);

  const handleContextMenu = useCallback((e: React.MouseEvent, objectId: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, objectId });
  }, []);

  // Filtered objects
  const filteredObjects = useMemo(() => {
    if (!searchQuery) return objects.filter(o => !o.parentId);
    return objects.filter(o => o.name.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [objects, searchQuery]);

  // Render tree node
  const renderTreeNode = (object: GameObject, depth = 0) => {
    const hasChildren = object.children.length > 0;
    const isExpanded = expandedNodes.has(object.id);
    const isSelected = selectedId === object.id;
    const children = objects.filter(o => o.parentId === object.id);

    return (
      <div key={object.id}>
        <div
          style={{
            ...phase1BaseStyles.listItem,
            ...(isSelected ? phase1BaseStyles.listItemSelected : {}),
            paddingLeft: `${12 + depth * 16}px`,
          }}
          onClick={() => handleSelect(object)}
          onContextMenu={(e) => handleContextMenu(e, object.id)}
          draggable
          onDragStart={() => setDraggedItem(object.id)}
          onDragEnd={() => setDraggedItem(null)}
        >
          {hasChildren && (
            <span
              onClick={(e) => { e.stopPropagation(); handleToggleExpand(object.id); }}
              style={{ cursor: 'pointer', fontSize: '10px', width: '16px' }}
            >
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          {!hasChildren && <span style={{ width: '16px' }} />}
          <span style={{ fontSize: '14px' }}>
            {object.type === 'camera' ? '📷' : object.type === 'sprite' ? '🖼️' : '📦'}
          </span>
          <span style={{ flex: 1, fontSize: '12px', color: object.isActive ? '#cdd6f4' : '#6c7086' }}>
            {object.name}
          </span>
          {object.isLocked && <span style={{ fontSize: '10px' }}>🔒</span>}
          {!object.isVisible && <span style={{ fontSize: '10px' }}>👁️‍🗨️</span>}
        </div>
        {isExpanded && children.map(child => renderTreeNode(child, depth + 1))}
      </div>
    );
  };

  return (
    <div style={phase1BaseStyles.panel}>
      <div style={phase1BaseStyles.header}>
        <h3 style={phase1BaseStyles.headerTitle}>🌳 Hierarchy</h3>
        <button
          style={phase1BaseStyles.button}
          onClick={() => console.log('Add object')}
        >
          + Add
        </button>
      </div>
      <div style={{ padding: '8px', borderBottom: '1px solid #313244' }}>
        <input
          type="text"
          placeholder="Search objects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={phase1BaseStyles.input}
        />
      </div>
      <div style={phase1BaseStyles.content}>
        {filteredObjects.map(obj => renderTreeNode(obj))}
      </div>
      {contextMenu && (
        <div
          style={{
            position: 'fixed',
            left: contextMenu.x,
            top: contextMenu.y,
            backgroundColor: '#1e1e2e',
            border: '1px solid #313244',
            borderRadius: '4px',
            padding: '4px 0',
            zIndex: 1000,
          }}
          onClick={() => setContextMenu(null)}
        >
          <div style={{ ...phase1BaseStyles.listItem, padding: '6px 12px' }} onClick={() => onObjectRename?.(contextMenu.objectId, 'New Name')}>Rename</div>
          <div style={{ ...phase1BaseStyles.listItem, padding: '6px 12px' }} onClick={() => onObjectDuplicate?.(contextMenu.objectId)}>Duplicate</div>
          <div style={phase1BaseStyles.divider} />
          <div style={{ ...phase1BaseStyles.listItem, padding: '6px 12px', color: '#f38ba8' }} onClick={() => onObjectDelete?.(contextMenu.objectId)}>Delete</div>
        </div>
      )}
    </div>
  );
});

SceneHierarchyPanelTemplate.displayName = 'SceneHierarchyPanelTemplate';

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 2: INSPECTOR PANEL 🔍
// ═══════════════════════════════════════════════════════════════════════════════

interface InspectorPanelProps {
  selectedObject: GameObject | null;
  onPropertyChange?: (property: string, value: unknown) => void;
  onComponentAdd?: (componentType: string) => void;
  onComponentRemove?: (componentId: string) => void;
}

export const InspectorPanelTemplate = memo<InspectorPanelProps>(({
  selectedObject,
  onPropertyChange,
  onComponentAdd,
  onComponentRemove,
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['transform', 'components']));
  const [editingProperty, setEditingProperty] = useState<string | null>(null);

  const handleToggleSection = useCallback((section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  }, []);

  const renderVectorInput = (label: string, value: { x: number; y: number; z: number }, propertyPath: string) => (
    <div style={{ marginBottom: '8px' }}>
      <label style={{ fontSize: '11px', color: '#a6adc8', display: 'block', marginBottom: '4px' }}>{label}</label>
      <div style={{ display: 'flex', gap: '4px' }}>
        {(['x', 'y', 'z'] as const).map(axis => (
          <div key={axis} style={{ flex: 1 }}>
            <label style={{ fontSize: '10px', color: axis === 'x' ? '#f38ba8' : axis === 'y' ? '#a6e3a1' : '#89b4fa' }}>{axis.toUpperCase()}</label>
            <input
              type="number"
              value={value[axis]}
              onChange={(e) => onPropertyChange?.(`${propertyPath}.${axis}`, parseFloat(e.target.value))}
              style={{ ...phase1BaseStyles.input, padding: '4px 6px' }}
            />
          </div>
        ))}
      </div>
    </div>
  );

  const renderSection = (title: string, icon: string, sectionKey: string, content: React.ReactNode) => (
    <div style={{ marginBottom: '8px' }}>
      <div
        style={{
          ...phase1BaseStyles.listItem,
          backgroundColor: '#181825',
          borderRadius: '4px 4px 0 0',
          cursor: 'pointer',
        }}
        onClick={() => handleToggleSection(sectionKey)}
      >
        <span style={{ fontSize: '10px' }}>{expandedSections.has(sectionKey) ? '▼' : '▶'}</span>
        <span>{icon}</span>
        <span style={{ fontSize: '12px', fontWeight: 500 }}>{title}</span>
      </div>
      {expandedSections.has(sectionKey) && (
        <div style={{ padding: '8px', backgroundColor: '#11111b', borderRadius: '0 0 4px 4px' }}>
          {content}
        </div>
      )}
    </div>
  );

  if (!selectedObject) {
    return (
      <div style={phase1BaseStyles.panel}>
        <div style={phase1BaseStyles.header}>
          <h3 style={phase1BaseStyles.headerTitle}>🔍 Inspector</h3>
        </div>
        <div style={{ ...phase1BaseStyles.content, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6c7086' }}>
          <p>No object selected</p>
        </div>
      </div>
    );
  }

  return (
    <div style={phase1BaseStyles.panel}>
      <div style={phase1BaseStyles.header}>
        <h3 style={phase1BaseStyles.headerTitle}>🔍 Inspector</h3>
      </div>
      <div style={phase1BaseStyles.content}>
        {/* Object Info */}
        <div style={{ marginBottom: '12px' }}>
          <input
            type="text"
            value={selectedObject.name}
            onChange={(e) => onPropertyChange?.('name', e.target.value)}
            style={{ ...phase1BaseStyles.input, fontSize: '14px', fontWeight: 500 }}
          />
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#a6adc8' }}>
              <input type="checkbox" checked={selectedObject.isActive} onChange={(e) => onPropertyChange?.('isActive', e.target.checked)} />
              Active
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#a6adc8' }}>
              <input type="checkbox" checked={selectedObject.isLocked} onChange={(e) => onPropertyChange?.('isLocked', e.target.checked)} />
              Locked
            </label>
          </div>
        </div>

        {/* Transform Section */}
        {renderSection('Transform', '📐', 'transform', (
          <>
            {renderVectorInput('Position', selectedObject.transform.position, 'transform.position')}
            {renderVectorInput('Rotation', selectedObject.transform.rotation, 'transform.rotation')}
            {renderVectorInput('Scale', selectedObject.transform.scale, 'transform.scale')}
          </>
        ))}

        {/* Components Section */}
        {renderSection('Components', '🧩', 'components', (
          <>
            {selectedObject.components.map(comp => (
              <div key={comp.id} style={{ ...phase1BaseStyles.listItem, justifyContent: 'space-between', backgroundColor: '#1e1e2e', borderRadius: '4px', marginBottom: '4px' }}>
                <span style={{ fontSize: '12px' }}>{comp.name}</span>
                <button style={{ ...phase1BaseStyles.button, padding: '2px 6px', fontSize: '10px' }} onClick={() => onComponentRemove?.(comp.id)}>✕</button>
              </div>
            ))}
            <button
              style={{ ...phase1BaseStyles.button, width: '100%', justifyContent: 'center', marginTop: '8px' }}
              onClick={() => onComponentAdd?.('NewComponent')}
            >
              + Add Component
            </button>
          </>
        ))}
      </div>
    </div>
  );
});

InspectorPanelTemplate.displayName = 'InspectorPanelTemplate';

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 3: CONSOLE PANEL 📋
// ═══════════════════════════════════════════════════════════════════════════════

interface ConsolePanelProps {
  maxLines?: number;
  onClear?: () => void;
  onFilter?: (filter: string) => void;
}

export const ConsolePanelTemplate = memo<ConsolePanelProps>(({
  maxLines = 1000,
  onClear,
  onFilter,
}) => {
  const [logs, setLogs] = useState<ConsoleLog[]>([]);
  const [filter, setFilter] = useState<'all' | 'log' | 'warn' | 'error'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isPaused, setIsPaused] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Mock logs
  React.useEffect(() => {
    setLogs([
      { id: '1', type: 'log', message: 'Game initialized successfully', timestamp: new Date(), count: 1 },
      { id: '2', type: 'warn', message: 'Asset "player.png" not found, using placeholder', timestamp: new Date(), count: 1 },
      { id: '3', type: 'error', message: 'NullReferenceException: Object reference not set', timestamp: new Date(), stackTrace: 'at Player.Update() in Player.cs:42', count: 3 },
      { id: '4', type: 'info', message: 'Scene "MainMenu" loaded in 0.234s', timestamp: new Date(), count: 1 },
    ]);
  }, []);

  const handleClear = useCallback(() => {
    setLogs([]);
    onClear?.();
  }, [onClear]);

  const handleFilterChange = useCallback((newFilter: 'all' | 'log' | 'warn' | 'error') => {
    setFilter(newFilter);
    onFilter?.(newFilter);
  }, [onFilter]);

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filter !== 'all' && log.type !== filter) return false;
      if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [logs, filter, searchQuery]);

  const getLogStyles = (type: ConsoleLog['type']) => {
    const colors = {
      log: '#cdd6f4',
      info: '#89b4fa',
      warn: '#f9e2af',
      error: '#f38ba8',
    };
    return { color: colors[type] };
  };

  const getLogIcon = (type: ConsoleLog['type']) => {
    const icons = { log: '📝', info: 'ℹ️', warn: '⚠️', error: '❌' };
    return icons[type];
  };

  return (
    <div style={phase1BaseStyles.panel}>
      <div style={phase1BaseStyles.header}>
        <h3 style={phase1BaseStyles.headerTitle}>📋 Console</h3>
        <div style={{ display: 'flex', gap: '4px' }}>
          {(['all', 'log', 'warn', 'error'] as const).map(f => (
            <button
              key={f}
              style={{ ...phase1BaseStyles.button, ...(filter === f ? phase1BaseStyles.buttonActive : {}), padding: '2px 8px', fontSize: '10px' }}
              onClick={() => handleFilterChange(f)}
            >
              {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
          <button style={{ ...phase1BaseStyles.button, padding: '2px 8px' }} onClick={() => setIsPaused(!isPaused)}>
            {isPaused ? '▶' : '⏸'}
          </button>
          <button style={{ ...phase1BaseStyles.button, padding: '2px 8px' }} onClick={handleClear}>
            🗑️
          </button>
        </div>
      </div>
      <div style={{ padding: '8px', borderBottom: '1px solid #313244' }}>
        <input
          type="text"
          placeholder="Search logs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={phase1BaseStyles.input}
        />
      </div>
      <div style={{ ...phase1BaseStyles.content, fontFamily: 'monospace', fontSize: '11px' }}>
        {filteredLogs.map(log => (
          <div
            key={log.id}
            style={{
              ...phase1BaseStyles.listItem,
              ...getLogStyles(log.type),
              padding: '4px 8px',
              borderBottom: '1px solid #313244',
              flexDirection: 'column',
              alignItems: 'flex-start',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%' }}>
              <span>{getLogIcon(log.type)}</span>
              <span style={{ flex: 1 }}>{log.message}</span>
              {log.count > 1 && (
                <span style={{ backgroundColor: '#45475a', padding: '1px 6px', borderRadius: '10px', fontSize: '10px' }}>
                  {log.count}
                </span>
              )}
              <span style={{ fontSize: '9px', color: '#6c7086' }}>
                {log.timestamp.toLocaleTimeString()}
              </span>
            </div>
            {log.stackTrace && (
              <div style={{ marginTop: '4px', paddingLeft: '24px', color: '#6c7086', fontSize: '10px' }}>
                {log.stackTrace}
              </div>
            )}
          </div>
        ))}
        {filteredLogs.length === 0 && (
          <div style={{ textAlign: 'center', color: '#6c7086', padding: '20px' }}>
            No logs to display
          </div>
        )}
      </div>
    </div>
  );
});

ConsolePanelTemplate.displayName = 'ConsolePanelTemplate';

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 4: TOOLBAR PANEL 🔧
// ═══════════════════════════════════════════════════════════════════════════════

interface ToolbarPanelProps {
  currentTool: EditorTool;
  onToolChange: (tool: EditorTool) => void;
  isPlaying?: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  onStop?: () => void;
}

export const ToolbarPanelTemplate = memo<ToolbarPanelProps>(({
  currentTool,
  onToolChange,
  isPlaying = false,
  onPlay,
  onPause,
  onStop,
}) => {
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [gridSize, setGridSize] = useState(1);
  const [showGizmos, setShowGizmos] = useState(true);

  const tools: { id: EditorTool; icon: string; label: string; shortcut: string }[] = [
    { id: 'select', icon: '🖱️', label: 'Select', shortcut: 'Q' },
    { id: 'move', icon: '✥', label: 'Move', shortcut: 'W' },
    { id: 'rotate', icon: '🔄', label: 'Rotate', shortcut: 'E' },
    { id: 'scale', icon: '⤢', label: 'Scale', shortcut: 'R' },
    { id: 'rect', icon: '⬜', label: 'Rect', shortcut: 'T' },
    { id: 'hand', icon: '✋', label: 'Hand', shortcut: 'H' },
  ];

  const toolbarStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '8px 16px',
    backgroundColor: '#1e1e2e',
    borderBottom: '1px solid #313244',
    flexWrap: 'wrap',
  };

  const toolGroupStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    padding: '4px',
    backgroundColor: '#181825',
    borderRadius: '6px',
  };

  return (
    <div style={toolbarStyle}>
      {/* Tool Selection Group */}
      <div style={toolGroupStyle}>
        {tools.map(tool => (
          <button
            key={tool.id}
            title={`${tool.label} (${tool.shortcut})`}
            style={{
              ...phase1BaseStyles.button,
              ...(currentTool === tool.id ? phase1BaseStyles.buttonActive : {}),
              padding: '6px 10px',
              minWidth: '36px',
            }}
            onClick={() => onToolChange(tool.id)}
          >
            <span style={{ fontSize: '16px' }}>{tool.icon}</span>
          </button>
        ))}
      </div>

      {/* Divider */}
      <div style={{ width: '1px', height: '24px', backgroundColor: '#313244' }} />

      {/* Play Controls */}
      <div style={toolGroupStyle}>
        <button
          style={{
            ...phase1BaseStyles.button,
            ...(isPlaying ? { backgroundColor: '#a6e3a1', borderColor: '#a6e3a1', color: '#1e1e2e' } : {}),
            padding: '6px 12px',
          }}
          onClick={isPlaying ? onPause : onPlay}
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>
        <button
          style={{ ...phase1BaseStyles.button, padding: '6px 12px' }}
          onClick={onStop}
          disabled={!isPlaying}
        >
          ⏹️
        </button>
      </div>

      {/* Divider */}
      <div style={{ width: '1px', height: '24px', backgroundColor: '#313244' }} />

      {/* Grid Settings */}
      <div style={{ ...toolGroupStyle, gap: '8px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#a6adc8', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={snapToGrid}
            onChange={(e) => setSnapToGrid(e.target.checked)}
          />
          Snap
        </label>
        <input
          type="number"
          value={gridSize}
          onChange={(e) => setGridSize(parseFloat(e.target.value))}
          min={0.1}
          step={0.1}
          style={{ ...phase1BaseStyles.input, width: '50px', padding: '4px 6px' }}
          title="Grid Size"
        />
      </div>

      {/* View Options */}
      <div style={{ ...toolGroupStyle, gap: '8px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#a6adc8', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showGizmos}
            onChange={(e) => setShowGizmos(e.target.checked)}
          />
          Gizmos
        </label>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Right-side actions */}
      <div style={toolGroupStyle}>
        <button style={phase1BaseStyles.button} title="Save Scene (Ctrl+S)">
          💾
        </button>
        <button style={phase1BaseStyles.button} title="Settings">
          ⚙️
        </button>
      </div>
    </div>
  );
});

ToolbarPanelTemplate.displayName = 'ToolbarPanelTemplate';

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE 1 COMBINED LAYOUT TEMPLATE
// ═══════════════════════════════════════════════════════════════════════════════

interface Phase1EditorLayoutProps {
  sceneId: string;
}

export const Phase1EditorLayoutTemplate = memo<Phase1EditorLayoutProps>(({ sceneId }) => {
  const [currentTool, setCurrentTool] = useState<EditorTool>('select');
  const [selectedObject, setSelectedObject] = useState<GameObject | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const layoutStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateRows: 'auto 1fr auto',
    gridTemplateColumns: '250px 1fr 300px',
    gridTemplateAreas: `
      "toolbar toolbar toolbar"
      "hierarchy viewport inspector"
      "console console console"
    `,
    height: '100vh',
    backgroundColor: '#11111b',
    gap: '4px',
    padding: '4px',
  };

  return (
    <div style={layoutStyle}>
      {/* Toolbar */}
      <div style={{ gridArea: 'toolbar' }}>
        <ToolbarPanelTemplate
          currentTool={currentTool}
          onToolChange={setCurrentTool}
          isPlaying={isPlaying}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onStop={() => setIsPlaying(false)}
        />
      </div>

      {/* Hierarchy */}
      <div style={{ gridArea: 'hierarchy', minHeight: 0 }}>
        <SceneHierarchyPanelTemplate
          sceneId={sceneId}
          onObjectSelect={setSelectedObject}
        />
      </div>

      {/* Viewport placeholder */}
      <div style={{ gridArea: 'viewport', backgroundColor: '#1e1e2e', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6c7086' }}>
        <span style={{ fontSize: '48px' }}>🎮</span>
        <span style={{ marginLeft: '12px' }}>Scene Viewport</span>
      </div>

      {/* Inspector */}
      <div style={{ gridArea: 'inspector', minHeight: 0 }}>
        <InspectorPanelTemplate
          selectedObject={selectedObject}
          onPropertyChange={(prop, val) => console.log('Property changed:', prop, val)}
        />
      </div>

      {/* Console */}
      <div style={{ gridArea: 'console', height: '200px' }}>
        <ConsolePanelTemplate />
      </div>
    </div>
  );
});

Phase1EditorLayoutTemplate.displayName = 'Phase1EditorLayoutTemplate';

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  SceneHierarchyPanelTemplate,
  InspectorPanelTemplate,
  ConsolePanelTemplate,
  ToolbarPanelTemplate,
  Phase1EditorLayoutTemplate,
};
