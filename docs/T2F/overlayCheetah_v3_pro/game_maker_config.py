#!/usr/bin/env python3
"""
Game Maker UI Configuration for Cheetah v3 PRO
==============================================
Rapid UI component generation configuration for the Overlay Game Maker project.
Defines templates and settings for enterprise-grade game development interface.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base configuration for Game Maker UI components
GAME_MAKER_CONFIG = {
    "project_name": "Overlay Game Maker",
    "version": "1.0.0",
    "framework": "react-typescript",
    "styling": "css-modules",
    "performance_mode": "enterprise",
    # Project paths
    "paths": {
        "src": "src",
        "components": "src/ui/components",
        "pages": "src/ui/pages",
        "hooks": "src/hooks",
        "context": "src/context",
        "utils": "src/utils",
        "types": "src/types",
        "styles": "src/styles",
        "tests": "src/__tests__",
    },
    # Design system configuration
    "design_system": {
        "colors": {
            "primary": "#2563eb",
            "secondary": "#64748b",
            "success": "#16a34a",
            "warning": "#d97706",
            "error": "#dc2626",
            "surface": "#ffffff",
            "background": "#f8fafc",
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
            "border": "#e2e8f0",
        },
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
        },
        "typography": {
            "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "sizes": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
            },
        },
    },
}

# Game Maker specific UI components to generate
COMPONENT_CONFIGS = {
    "GameDashboard": {
        "component_name": "GameDashboard",
        "use_typescript": True,
        "performance_optimized": True,
        "needs_context": True,
        "needs_websocket": True,
        "props": [
            {"name": "projectId", "type": "string", "required": True},
            {
                "name": "onProjectLoad",
                "type": "(project: GameProject) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {
                "name": "activeProject",
                "type": "GameProject | null",
                "initial_value": "null",
            },
            {"name": "recentProjects", "type": "GameProject[]", "initial_value": "[]"},
            {"name": "isLoading", "type": "boolean", "initial_value": "false"},
            {"name": "error", "type": "Error | null", "initial_value": "null"},
        ],
        "has_header": True,
        "header_title": "Game Development Dashboard",
        "header_actions": [
            {
                "icon": "➕",
                "label": "New Project",
                "handler": "handleCreateProject",
                "class": "primary",
            },
            {"icon": "📂", "label": "Open Project", "handler": "handleOpenProject"},
            {"icon": "⚙️", "label": "Settings", "handler": "handleOpenSettings"},
        ],
        "has_content": True,
        "content_type": "grid",
        "grid_columns": "repeat(auto-fit, minmax(300px, 1fr))",
        "grid_items": [
            {
                "component": "ProjectCard",
                "props": [
                    {"name": "project", "value": "{project}"},
                    {"name": "onOpen", "value": "{handleProjectOpen}"},
                    {"name": "onDelete", "value": "{handleProjectDelete}"},
                ],
            }
        ],
        "event_handlers": [
            {
                "name": "handleCreateProject",
                "params": "",
                "param_types": "",
                "dependencies": ["onProjectLoad"],
                "body": """
try {
  setIsLoading(true);
  const newProject = await createNewProject();
  setActiveProject(newProject);
  onProjectLoad?.(newProject);
} catch (err) {
  setError(err as Error);
} finally {
  setIsLoading(false);
}
                """,
            },
            {
                "name": "handleOpenProject",
                "params": "projectId",
                "param_types": "string",
                "dependencies": ["onProjectLoad"],
                "body": """
try {
  setIsLoading(true);
  const project = await loadProject(projectId);
  setActiveProject(project);
  onProjectLoad?.(project);
} catch (err) {
  setError(err as Error);
} finally {
  setIsLoading(false);
}
                """,
            },
        ],
        "effects": [
            {
                "dependencies": [],
                "body": """
loadRecentProjects().then(setRecentProjects).catch(setError);
                """,
            }
        ],
        "has_loading_state": True,
        "has_error_state": True,
        "error_retry": True,
    },
    "VisualScriptingEditor": {
        "component_name": "VisualScriptingEditor",
        "use_typescript": True,
        "performance_optimized": True,
        "needs_context": True,
        "needs_engine": True,
        "has_drag_drop": True,
        "props": [
            {"name": "sceneId", "type": "string", "required": True},
            {
                "name": "onScriptChange",
                "type": "(script: GameScript) => void",
                "required": False,
            },
            {"name": "readonly", "type": "boolean", "required": False},
        ],
        "state_vars": [
            {"name": "nodes", "type": "ScriptNode[]", "initial_value": "[]"},
            {"name": "connections", "type": "NodeConnection[]", "initial_value": "[]"},
            {
                "name": "selectedNode",
                "type": "ScriptNode | null",
                "initial_value": "null",
            },
            {
                "name": "draggedNode",
                "type": "ScriptNode | null",
                "initial_value": "null",
            },
            {"name": "zoom", "type": "number", "initial_value": "1"},
        ],
        "has_header": True,
        "header_title": "Visual Script Editor",
        "header_actions": [
            {
                "icon": "▶️",
                "label": "Test Script",
                "handler": "handleTestScript",
                "class": "primary",
            },
            {"icon": "💾", "label": "Save", "handler": "handleSaveScript"},
            {
                "icon": "🗑️",
                "label": "Clear",
                "handler": "handleClearScript",
                "class": "danger",
            },
        ],
        "has_content": True,
        "content_type": "custom",
        "custom_content": """
<div className="script-editor-workspace">
  <div className="node-palette">
    <div className="palette-section">
      <h3>Logic Nodes</h3>
      {LOGIC_NODES.map(node => (
        <div
          key={node.type}
          className="palette-node"
          draggable
          onDragStart={(e) => handleNodeDragStart(e, node)}
        >
          {node.icon} {node.label}
        </div>
      ))}
    </div>
    <div className="palette-section">
      <h3>Action Nodes</h3>
      {ACTION_NODES.map(node => (
        <div
          key={node.type}
          className="palette-node"
          draggable
          onDragStart={(e) => handleNodeDragStart(e, node)}
        >
          {node.icon} {node.label}
        </div>
      ))}
    </div>
  </div>

  <div className="script-canvas">
    <svg className="connections-layer">
      {connections.map(connection => (
        <ConnectionLine
          key={connection.id}
          connection={connection}
          onDelete={handleDeleteConnection}
        />
      ))}
    </svg>

    <div className="nodes-layer">
      {nodes.map(node => (
        <ScriptNode
          key={node.id}
          node={node}
          selected={selectedNode?.id === node.id}
          onSelect={setSelectedNode}
          onMove={handleNodeMove}
          onDelete={handleDeleteNode}
          onConnect={handleNodeConnect}
        />
      ))}
    </div>
  </div>

  <div className="properties-panel">
    {selectedNode && (
      <NodeProperties
        node={selectedNode}
        onChange={handleNodePropertyChange}
        readonly={readonly}
      />
    )}
  </div>
</div>
        """,
        "event_handlers": [
            {
                "name": "handleNodeDragStart",
                "params": "e, nodeTemplate",
                "param_types": "React.DragEvent, NodeTemplate",
                "dependencies": [],
                "body": """
e.dataTransfer.setData('application/node', JSON.stringify(nodeTemplate));
                """,
            },
            {
                "name": "handleCanvasDrop",
                "params": "e",
                "param_types": "React.DragEvent",
                "dependencies": ["nodes"],
                "body": """
e.preventDefault();
const nodeData = JSON.parse(e.dataTransfer.getData('application/node'));
const rect = e.currentTarget.getBoundingClientRect();
const position = {
  x: (e.clientX - rect.left) / zoom,
  y: (e.clientY - rect.top) / zoom
};

const newNode = createNode(nodeData, position);
setNodes(prev => [...prev, newNode]);
                """,
            },
            {
                "name": "handleTestScript",
                "params": "",
                "param_types": "",
                "dependencies": ["nodes", "connections", "engineConnector"],
                "body": """
if (!engineConnector) return;

try {
  const compiledScript = compileNodesToScript(nodes, connections);
  engineConnector.executeScript(sceneId, compiledScript);
} catch (err) {
  console.error('Script compilation failed:', err);
}
                """,
            },
        ],
    },
    "AssetBrowser": {
        "component_name": "AssetBrowser",
        "use_typescript": True,
        "performance_optimized": True,
        "needs_context": True,
        "props": [
            {
                "name": "onAssetSelect",
                "type": "(asset: GameAsset) => void",
                "required": False,
            },
            {"name": "filterType", "type": "AssetType", "required": False},
            {"name": "multiSelect", "type": "boolean", "required": False},
        ],
        "state_vars": [
            {"name": "assets", "type": "GameAsset[]", "initial_value": "[]"},
            {"name": "selectedAssets", "type": "GameAsset[]", "initial_value": "[]"},
            {"name": "searchQuery", "type": "string", "initial_value": "''"},
            {"name": "viewMode", "type": "'grid' | 'list'", "initial_value": "'grid'"},
            {"name": "isUploading", "type": "boolean", "initial_value": "false"},
        ],
        "has_header": True,
        "header_title": "Asset Browser",
        "header_actions": [
            {
                "icon": "📤",
                "label": "Upload",
                "handler": "handleUploadAsset",
                "class": "primary",
            },
            {"icon": "🔍", "label": "Search", "handler": "handleToggleSearch"},
            {
                "icon": "⚡",
                "label": "Generate",
                "handler": "handleGenerateAsset",
                "class": "secondary",
            },
        ],
        "has_content": True,
        "content_type": "custom",
        "custom_content": """
<div className="asset-browser-toolbar">
  <div className="search-section">
    <input
      type="text"
      placeholder="Search assets..."
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      className="search-input"
    />
    <div className="filter-section">
      <select onChange={handleFilterChange} className="filter-select">
        <option value="">All Types</option>
        <option value="model">3D Models</option>
        <option value="texture">Textures</option>
        <option value="audio">Audio</option>
        <option value="script">Scripts</option>
      </select>
    </div>
  </div>

  <div className="view-controls">
    <button
      className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
      onClick={() => setViewMode('grid')}
    >
      ⊞
    </button>
    <button
      className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
      onClick={() => setViewMode('list')}
    >
      ☰
    </button>
  </div>
</div>

<div className={`asset-grid ${viewMode}`}>
  {filteredAssets.map(asset => (
    <AssetCard
      key={asset.id}
      asset={asset}
      selected={selectedAssets.includes(asset)}
      onSelect={handleAssetSelect}
      onPreview={handleAssetPreview}
      onDelete={handleAssetDelete}
      viewMode={viewMode}
    />
  ))}
</div>

{isUploading && (
  <div className="upload-progress">
    <ProgressBar />
    <span>Uploading assets...</span>
  </div>
)}
        """,
        "computed_values": [
            {
                "name": "filteredAssets",
                "dependencies": ["assets", "searchQuery", "filterType"],
                "body": """
return assets.filter(asset => {
  const matchesSearch = !searchQuery ||
    asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    asset.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

  const matchesType = !filterType || asset.type === filterType;

  return matchesSearch && matchesType;
});
                """,
            }
        ],
    },
    "RealTimePreview": {
        "component_name": "RealTimePreview",
        "use_typescript": True,
        "performance_optimized": True,
        "needs_context": True,
        "needs_engine": True,
        "needs_websocket": True,
        "props": [
            {"name": "sceneId", "type": "string", "required": True},
            {"name": "quality", "type": "'low' | 'medium' | 'high'", "required": False},
        ],
        "state_vars": [
            {"name": "isPlaying", "type": "boolean", "initial_value": "false"},
            {
                "name": "previewData",
                "type": "PreviewFrame | null",
                "initial_value": "null",
            },
            {"name": "stats", "type": "PerformanceStats", "initial_value": "{}"},
            {
                "name": "cameraPosition",
                "type": "Vector3",
                "initial_value": "{x: 0, y: 0, z: 5}",
            },
        ],
        "has_header": True,
        "header_title": "Live Preview",
        "header_actions": [
            {"icon": "▶️", "label": "Play", "handler": "handlePlay", "class": "primary"},
            {"icon": "⏸️", "label": "Pause", "handler": "handlePause"},
            {"icon": "⏹️", "label": "Stop", "handler": "handleStop"},
            {"icon": "📷", "label": "Screenshot", "handler": "handleScreenshot"},
        ],
        "has_content": True,
        "content_type": "custom",
        "custom_content": """
<div className="preview-container">
  <div className="preview-viewport" ref={viewportRef}>
    <canvas
      ref={canvasRef}
      className="preview-canvas"
      width={800}
      height={600}
      onMouseMove={handleMouseMove}
      onWheel={handleZoom}
    />

    <div className="preview-overlay">
      <div className="stats-panel">
        <div className="stat-item">
          <span>FPS: {stats.fps || 0}</span>
        </div>
        <div className="stat-item">
          <span>Triangles: {stats.triangles || 0}</span>
        </div>
        <div className="stat-item">
          <span>Draw Calls: {stats.drawCalls || 0}</span>
        </div>
      </div>

      {!isPlaying && (
        <div className="play-button-overlay">
          <button
            className="large-play-btn"
            onClick={handlePlay}
          >
            ▶️ Start Preview
          </button>
        </div>
      )}
    </div>
  </div>

  <div className="preview-controls">
    <div className="camera-controls">
      <h4>Camera</h4>
      <div className="control-group">
        <label>Position:</label>
        <input
          type="range"
          min="-10"
          max="10"
          step="0.1"
          value={cameraPosition.x}
          onChange={(e) => updateCameraPosition('x', parseFloat(e.target.value))}
        />
        <span>{cameraPosition.x.toFixed(1)}</span>
      </div>
    </div>

    <div className="quality-controls">
      <h4>Quality</h4>
      <select value={quality} onChange={handleQualityChange}>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
    </div>
  </div>
</div>
        """,
    },
    "CollaborationPanel": {
        "component_name": "CollaborationPanel",
        "use_typescript": True,
        "performance_optimized": True,
        "needs_context": True,
        "needs_websocket": True,
        "state_vars": [
            {"name": "activeUsers", "type": "User[]", "initial_value": "[]"},
            {"name": "chatMessages", "type": "ChatMessage[]", "initial_value": "[]"},
            {"name": "newMessage", "type": "string", "initial_value": "''"},
            {"name": "showUserList", "type": "boolean", "initial_value": "true"},
        ],
        "has_header": True,
        "header_title": "Team Collaboration",
        "header_actions": [
            {"icon": "👥", "label": "Users", "handler": "handleToggleUsers"},
            {"icon": "🔗", "label": "Share Link", "handler": "handleShareLink"},
            {"icon": "📞", "label": "Voice Chat", "handler": "handleVoiceChat"},
        ],
        "has_content": True,
        "content_type": "custom",
        "custom_content": """
<div className="collaboration-layout">
  {showUserList && (
    <div className="users-panel">
      <h4>Online Users ({activeUsers.length})</h4>
      <div className="user-list">
        {activeUsers.map(user => (
          <div key={user.id} className="user-item">
            <div className="user-avatar" style={{backgroundColor: user.color}}>
              {user.name[0].toUpperCase()}
            </div>
            <span className="user-name">{user.name}</span>
            <div className={`user-status ${user.status}`} />
          </div>
        ))}
      </div>
    </div>
  )}

  <div className="chat-panel">
    <div className="chat-messages" ref={messagesRef}>
      {chatMessages.map(message => (
        <div key={message.id} className={`message ${message.type}`}>
          <div className="message-header">
            <span className="message-author">{message.author}</span>
            <span className="message-time">{formatTime(message.timestamp)}</span>
          </div>
          <div className="message-content">{message.content}</div>
        </div>
      ))}
    </div>

    <div className="chat-input">
      <input
        type="text"
        placeholder="Type a message..."
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        className="message-input"
      />
      <button
        onClick={handleSendMessage}
        disabled={!newMessage.trim()}
        className="send-btn"
      >
        Send
      </button>
    </div>
  </div>
</div>
        """,
    },
}

# Global styles and theme
GLOBAL_STYLES = """
:root {
  /* Colors */
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --secondary-color: #64748b;
  --secondary-hover: #475569;
  --success-color: #16a34a;
  --warning-color: #d97706;
  --error-color: #dc2626;
  --error-hover: #b91c1c;

  /* Surfaces */
  --surface-color: #ffffff;
  --background-color: #f8fafc;
  --header-bg: #f1f5f9;
  --footer-bg: #f8fafc;
  --hover-bg: #f1f5f9;
  --border-color: #e2e8f0;

  /* Text */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border radius */
  --border-radius: 8px;
  --border-radius-sm: 4px;
  --border-radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;

  /* Animation */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --surface-color: #1e293b;
    --background-color: #0f172a;
    --header-bg: #1e293b;
    --footer-bg: #1e293b;
    --hover-bg: #334155;
    --border-color: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
  }
}
"""


# Export configuration for Cheetah v3 PRO
def get_component_config(component_name: str) -> Dict[str, Any]:
    """Get configuration for a specific component"""
    return COMPONENT_CONFIGS.get(component_name, {})


def get_all_components() -> List[str]:
    """Get list of all available component names"""
    return list(COMPONENT_CONFIGS.keys())


def get_base_config() -> Dict[str, Any]:
    """Get base game maker configuration"""
    return GAME_MAKER_CONFIG


# Generate multiple components
def generate_components_batch(components: List[str]) -> Dict[str, Dict[str, Any]]:
    """Generate configuration for multiple components"""
    return {name: get_component_config(name) for name in components}


# Quick presets for common UI patterns
QUICK_PRESETS = {
    "dashboard": ["GameDashboard", "AssetBrowser", "RealTimePreview"],
    "editor": ["VisualScriptingEditor", "AssetBrowser", "RealTimePreview"],
    "collaboration": ["CollaborationPanel", "GameDashboard"],
    "full_suite": list(COMPONENT_CONFIGS.keys()),
}


def get_preset_config(preset_name: str) -> Dict[str, Dict[str, Any]]:
    """Get configuration for a preset collection of components"""
    components = QUICK_PRESETS.get(preset_name, [])
    return generate_components_batch(components)


if __name__ == "__main__":
    # Example usage
    print("Available Game Maker Components:")
    for component in get_all_components():
        print(f"  - {component}")

    print("\nAvailable Presets:")
    for preset in QUICK_PRESETS.keys():
        print(f"  - {preset}: {', '.join(QUICK_PRESETS[preset])}")
