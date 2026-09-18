#!/usr/bin/env python3
"""
Marathon Configuration for Cheetah v3 PRO
=========================================
Comprehensive component definitions for building the complete Game Maker system.
Organized into 5 phases with visible milestones.
"""

from typing import Any, Dict, List

# =============================================================================
# PHASE 1: CORE EDITOR PANELS
# Milestone: Full Editor Layout
# =============================================================================

PHASE_1_COMPONENTS = {
    "SceneHierarchyPanel": {
        "component_name": "SceneHierarchyPanel",
        "description": "Tree view of all objects in the current scene",
        "phase": 1,
        "props": [
            {"name": "sceneId", "type": "string", "required": True},
            {
                "name": "onObjectSelect",
                "type": "(object: GameObject) => void",
                "required": False,
            },
            {
                "name": "onObjectRename",
                "type": "(id: string, name: string) => void",
                "required": False,
            },
            {
                "name": "onObjectDelete",
                "type": "(id: string) => void",
                "required": False,
            },
            {
                "name": "onObjectDuplicate",
                "type": "(id: string) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "objects", "type": "GameObject[]", "initial": "[]"},
            {"name": "expandedNodes", "type": "Set<string>", "initial": "new Set()"},
            {"name": "selectedId", "type": "string | null", "initial": "null"},
            {"name": "searchQuery", "type": "string", "initial": "''"},
            {"name": "draggedItem", "type": "string | null", "initial": "null"},
        ],
        "features": [
            "tree_view",
            "drag_drop",
            "context_menu",
            "search",
            "multi_select",
        ],
        "icon": "🌳",
    },
    "InspectorPanel": {
        "component_name": "InspectorPanel",
        "description": "Property editor for selected game objects",
        "phase": 1,
        "props": [
            {"name": "selectedObject", "type": "GameObject | null", "required": True},
            {
                "name": "onPropertyChange",
                "type": "(property: string, value: any) => void",
                "required": False,
            },
            {
                "name": "onComponentAdd",
                "type": "(componentType: string) => void",
                "required": False,
            },
            {
                "name": "onComponentRemove",
                "type": "(componentId: string) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {
                "name": "expandedSections",
                "type": "Set<string>",
                "initial": "new Set(['transform'])",
            },
            {"name": "editingProperty", "type": "string | null", "initial": "null"},
            {"name": "localValues", "type": "Record<string, any>", "initial": "{}"},
        ],
        "features": [
            "property_grid",
            "vector_inputs",
            "color_picker",
            "component_list",
        ],
        "icon": "🔍",
    },
    "ConsolePanel": {
        "component_name": "ConsolePanel",
        "description": "Debug console for logs, warnings, and errors",
        "phase": 1,
        "props": [
            {"name": "maxLines", "type": "number", "required": False, "default": 1000},
            {"name": "onClear", "type": "() => void", "required": False},
            {"name": "onFilter", "type": "(filter: string) => void", "required": False},
        ],
        "state_vars": [
            {"name": "logs", "type": "ConsoleLog[]", "initial": "[]"},
            {
                "name": "filter",
                "type": "'all' | 'log' | 'warn' | 'error'",
                "initial": "'all'",
            },
            {"name": "searchQuery", "type": "string", "initial": "''"},
            {"name": "isPaused", "type": "boolean", "initial": "false"},
            {"name": "isCollapsed", "type": "boolean", "initial": "false"},
        ],
        "features": [
            "log_levels",
            "search",
            "copy",
            "clear",
            "pause",
            "collapse_similar",
        ],
        "icon": "📋",
    },
    "ToolbarPanel": {
        "component_name": "ToolbarPanel",
        "description": "Main toolbar with editor tools and actions",
        "phase": 1,
        "props": [
            {"name": "currentTool", "type": "string", "required": True},
            {
                "name": "onToolChange",
                "type": "(tool: string) => void",
                "required": True,
            },
            {"name": "isPlaying", "type": "boolean", "required": False},
            {"name": "onPlay", "type": "() => void", "required": False},
            {"name": "onPause", "type": "() => void", "required": False},
            {"name": "onStop", "type": "() => void", "required": False},
        ],
        "state_vars": [
            {"name": "selectedTool", "type": "string", "initial": "'select'"},
            {"name": "snapToGrid", "type": "boolean", "initial": "true"},
            {"name": "gridSize", "type": "number", "initial": "1"},
            {"name": "showGizmos", "type": "boolean", "initial": "true"},
        ],
        "features": [
            "tool_selection",
            "play_controls",
            "snap_settings",
            "view_options",
        ],
        "icon": "🔧",
    },
}

# =============================================================================
# PHASE 2: CREATIVE TOOLS
# Milestone: Full Creative Suite
# =============================================================================

PHASE_2_COMPONENTS = {
    "TimelineEditor": {
        "component_name": "TimelineEditor",
        "description": "Animation timeline with keyframe editing",
        "phase": 2,
        "props": [
            {"name": "animationId", "type": "string", "required": False},
            {"name": "duration", "type": "number", "required": False, "default": 10},
            {
                "name": "onKeyframeAdd",
                "type": "(time: number, property: string, value: any) => void",
                "required": False,
            },
            {
                "name": "onKeyframeDelete",
                "type": "(keyframeId: string) => void",
                "required": False,
            },
            {
                "name": "onPlaybackChange",
                "type": "(time: number) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "currentTime", "type": "number", "initial": "0"},
            {"name": "isPlaying", "type": "boolean", "initial": "false"},
            {"name": "zoom", "type": "number", "initial": "1"},
            {"name": "tracks", "type": "AnimationTrack[]", "initial": "[]"},
            {"name": "selectedKeyframes", "type": "string[]", "initial": "[]"},
            {"name": "scrollOffset", "type": "number", "initial": "0"},
        ],
        "features": [
            "keyframes",
            "tracks",
            "playback",
            "zoom",
            "scrubbing",
            "curve_editor",
        ],
        "icon": "⏱️",
    },
    "MaterialEditor": {
        "component_name": "MaterialEditor",
        "description": "Material and shader property editor",
        "phase": 2,
        "props": [
            {"name": "materialId", "type": "string", "required": False},
            {
                "name": "onMaterialChange",
                "type": "(material: Material) => void",
                "required": False,
            },
            {
                "name": "onTextureSelect",
                "type": "(slot: string) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "material", "type": "Material | null", "initial": "null"},
            {
                "name": "previewMode",
                "type": "'sphere' | 'cube' | 'plane'",
                "initial": "'sphere'",
            },
            {
                "name": "expandedGroups",
                "type": "Set<string>",
                "initial": "new Set(['base'])",
            },
            {"name": "shaderType", "type": "string", "initial": "'standard'"},
        ],
        "features": [
            "texture_slots",
            "color_picker",
            "slider_inputs",
            "preview_3d",
            "shader_select",
        ],
        "icon": "🎨",
    },
    "ParticleEditor": {
        "component_name": "ParticleEditor",
        "description": "Particle system designer and editor",
        "phase": 2,
        "props": [
            {"name": "particleSystemId", "type": "string", "required": False},
            {
                "name": "onSystemChange",
                "type": "(system: ParticleSystem) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "system", "type": "ParticleSystem | null", "initial": "null"},
            {"name": "isSimulating", "type": "boolean", "initial": "false"},
            {"name": "selectedModule", "type": "string", "initial": "'emission'"},
            {"name": "previewBackground", "type": "string", "initial": "'dark'"},
        ],
        "features": ["modules", "curves", "gradients", "preview", "presets"],
        "icon": "✨",
    },
    "AudioMixerPanel": {
        "component_name": "AudioMixerPanel",
        "description": "Audio mixing and sound design panel",
        "phase": 2,
        "props": [
            {
                "name": "onVolumeChange",
                "type": "(channel: string, volume: number) => void",
                "required": False,
            },
            {"name": "onMute", "type": "(channel: string) => void", "required": False},
            {"name": "onSolo", "type": "(channel: string) => void", "required": False},
        ],
        "state_vars": [
            {"name": "channels", "type": "AudioChannel[]", "initial": "[]"},
            {"name": "masterVolume", "type": "number", "initial": "1"},
            {"name": "selectedChannel", "type": "string | null", "initial": "null"},
            {"name": "isPlaying", "type": "boolean", "initial": "false"},
        ],
        "features": [
            "mixer_channels",
            "volume_faders",
            "mute_solo",
            "effects",
            "metering",
        ],
        "icon": "🎵",
    },
}

# =============================================================================
# PHASE 3: ADVANCED SYSTEMS
# Milestone: Professional Features
# =============================================================================

PHASE_3_COMPONENTS = {
    "PrefabManager": {
        "component_name": "PrefabManager",
        "description": "Manage reusable object templates (prefabs)",
        "phase": 3,
        "props": [
            {
                "name": "onPrefabSelect",
                "type": "(prefab: Prefab) => void",
                "required": False,
            },
            {
                "name": "onPrefabInstantiate",
                "type": "(prefabId: string) => void",
                "required": False,
            },
            {
                "name": "onPrefabCreate",
                "type": "(object: GameObject) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "prefabs", "type": "Prefab[]", "initial": "[]"},
            {"name": "selectedPrefab", "type": "Prefab | null", "initial": "null"},
            {"name": "searchQuery", "type": "string", "initial": "''"},
            {"name": "viewMode", "type": "'grid' | 'list'", "initial": "'grid'"},
            {"name": "categoryFilter", "type": "string", "initial": "'all'"},
        ],
        "features": [
            "prefab_library",
            "preview",
            "instantiate",
            "variants",
            "categories",
        ],
        "icon": "📦",
    },
    "LightingEditor": {
        "component_name": "LightingEditor",
        "description": "Scene lighting and environment settings",
        "phase": 3,
        "props": [
            {"name": "sceneId", "type": "string", "required": True},
            {
                "name": "onLightingChange",
                "type": "(settings: LightingSettings) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "lights", "type": "Light[]", "initial": "[]"},
            {"name": "selectedLight", "type": "Light | null", "initial": "null"},
            {"name": "ambientColor", "type": "string", "initial": "'#404040'"},
            {"name": "skyboxType", "type": "string", "initial": "'gradient'"},
            {
                "name": "shadowQuality",
                "type": "'low' | 'medium' | 'high'",
                "initial": "'medium'",
            },
        ],
        "features": [
            "light_list",
            "properties",
            "shadows",
            "skybox",
            "fog",
            "post_processing",
        ],
        "icon": "💡",
    },
    "PhysicsPanel": {
        "component_name": "PhysicsPanel",
        "description": "Physics configuration and simulation settings",
        "phase": 3,
        "props": [
            {
                "name": "onSettingsChange",
                "type": "(settings: PhysicsSettings) => void",
                "required": False,
            },
            {"name": "onSimulate", "type": "() => void", "required": False},
        ],
        "state_vars": [
            {
                "name": "gravity",
                "type": "Vector3",
                "initial": "{ x: 0, y: -9.81, z: 0 }",
            },
            {"name": "layers", "type": "PhysicsLayer[]", "initial": "[]"},
            {"name": "selectedLayer", "type": "number", "initial": "0"},
            {"name": "isSimulating", "type": "boolean", "initial": "false"},
            {"name": "collisionMatrix", "type": "boolean[][]", "initial": "[]"},
        ],
        "features": [
            "gravity",
            "layers",
            "collision_matrix",
            "materials",
            "simulation",
        ],
        "icon": "⚡",
    },
    "InputManager": {
        "component_name": "InputManager",
        "description": "Input mapping and control configuration",
        "phase": 3,
        "props": [
            {
                "name": "onMappingChange",
                "type": "(mapping: InputMapping) => void",
                "required": False,
            },
            {
                "name": "onActionAdd",
                "type": "(action: InputAction) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "actions", "type": "InputAction[]", "initial": "[]"},
            {"name": "selectedAction", "type": "InputAction | null", "initial": "null"},
            {"name": "isListening", "type": "boolean", "initial": "false"},
            {
                "name": "deviceFilter",
                "type": "'all' | 'keyboard' | 'gamepad' | 'mouse'",
                "initial": "'all'",
            },
        ],
        "features": ["action_map", "key_binding", "gamepad", "touch", "rebinding"],
        "icon": "🎮",
    },
}

# =============================================================================
# PHASE 4: PROJECT & WORKFLOW
# Milestone: Production Ready
# =============================================================================

PHASE_4_COMPONENTS = {
    "BuildPanel": {
        "component_name": "BuildPanel",
        "description": "Build and export settings for multiple platforms",
        "phase": 4,
        "props": [
            {"name": "projectId", "type": "string", "required": True},
            {
                "name": "onBuild",
                "type": "(platform: string, config: BuildConfig) => void",
                "required": False,
            },
            {
                "name": "onBuildComplete",
                "type": "(result: BuildResult) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "selectedPlatform", "type": "string", "initial": "'windows'"},
            {"name": "buildConfig", "type": "BuildConfig", "initial": "{}"},
            {"name": "isBuilding", "type": "boolean", "initial": "false"},
            {"name": "buildProgress", "type": "number", "initial": "0"},
            {"name": "buildLogs", "type": "string[]", "initial": "[]"},
        ],
        "features": ["platform_select", "config", "progress", "logs", "output_path"],
        "icon": "🔨",
    },
    "VersionControlPanel": {
        "component_name": "VersionControlPanel",
        "description": "Git integration and version history",
        "phase": 4,
        "props": [
            {"name": "projectId", "type": "string", "required": True},
            {
                "name": "onCommit",
                "type": "(message: string, files: string[]) => void",
                "required": False,
            },
            {"name": "onPush", "type": "() => void", "required": False},
            {"name": "onPull", "type": "() => void", "required": False},
        ],
        "state_vars": [
            {"name": "changes", "type": "FileChange[]", "initial": "[]"},
            {"name": "commits", "type": "Commit[]", "initial": "[]"},
            {"name": "currentBranch", "type": "string", "initial": "'main'"},
            {"name": "branches", "type": "string[]", "initial": "['main']"},
            {"name": "selectedFiles", "type": "Set<string>", "initial": "new Set()"},
            {"name": "commitMessage", "type": "string", "initial": "''"},
        ],
        "features": [
            "changes",
            "staging",
            "commit",
            "branches",
            "history",
            "diff_view",
        ],
        "icon": "📚",
    },
    "PluginManager": {
        "component_name": "PluginManager",
        "description": "Install and manage editor plugins/extensions",
        "phase": 4,
        "props": [
            {
                "name": "onPluginInstall",
                "type": "(pluginId: string) => void",
                "required": False,
            },
            {
                "name": "onPluginUninstall",
                "type": "(pluginId: string) => void",
                "required": False,
            },
            {
                "name": "onPluginToggle",
                "type": "(pluginId: string, enabled: boolean) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "installedPlugins", "type": "Plugin[]", "initial": "[]"},
            {"name": "availablePlugins", "type": "Plugin[]", "initial": "[]"},
            {"name": "searchQuery", "type": "string", "initial": "''"},
            {"name": "categoryFilter", "type": "string", "initial": "'all'"},
            {"name": "isLoading", "type": "boolean", "initial": "false"},
        ],
        "features": [
            "browse",
            "install",
            "uninstall",
            "enable_disable",
            "settings",
            "updates",
        ],
        "icon": "🧩",
    },
    "LocalizationPanel": {
        "component_name": "LocalizationPanel",
        "description": "Multi-language text and asset management",
        "phase": 4,
        "props": [
            {"name": "projectId", "type": "string", "required": True},
            {
                "name": "onLocaleChange",
                "type": "(locale: string) => void",
                "required": False,
            },
            {
                "name": "onStringUpdate",
                "type": "(key: string, locale: string, value: string) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {
                "name": "locales",
                "type": "string[]",
                "initial": "['en', 'es', 'fr', 'de', 'ja']",
            },
            {"name": "currentLocale", "type": "string", "initial": "'en'"},
            {
                "name": "strings",
                "type": "Record<string, Record<string, string>>",
                "initial": "{}",
            },
            {"name": "searchQuery", "type": "string", "initial": "''"},
            {"name": "missingOnly", "type": "boolean", "initial": "false"},
        ],
        "features": [
            "string_table",
            "import_export",
            "auto_translate",
            "validation",
            "preview",
        ],
        "icon": "🌍",
    },
}

# =============================================================================
# PHASE 5: INTELLIGENCE & POLISH
# Milestone: AI-Enhanced Complete System
# =============================================================================

PHASE_5_COMPONENTS = {
    "AIAssistantPanel": {
        "component_name": "AIAssistantPanel",
        "description": "AI-powered code and asset generation assistant",
        "phase": 5,
        "props": [
            {
                "name": "onGenerate",
                "type": "(prompt: string, type: string) => void",
                "required": False,
            },
            {
                "name": "onApply",
                "type": "(result: AIResult) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "prompt", "type": "string", "initial": "''"},
            {"name": "history", "type": "AIConversation[]", "initial": "[]"},
            {"name": "isGenerating", "type": "boolean", "initial": "false"},
            {
                "name": "generationType",
                "type": "'code' | 'asset' | 'dialog' | 'level'",
                "initial": "'code'",
            },
            {"name": "suggestions", "type": "string[]", "initial": "[]"},
        ],
        "features": [
            "chat",
            "code_gen",
            "asset_gen",
            "suggestions",
            "history",
            "templates",
        ],
        "icon": "🤖",
    },
    "PerformanceMonitor": {
        "component_name": "PerformanceMonitor",
        "description": "Real-time performance metrics and profiling",
        "phase": 5,
        "props": [
            {
                "name": "isEnabled",
                "type": "boolean",
                "required": False,
                "default": True,
            },
            {
                "name": "onWarning",
                "type": "(metric: string, value: number) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "fps", "type": "number", "initial": "60"},
            {"name": "frameTime", "type": "number", "initial": "16.67"},
            {"name": "memoryUsage", "type": "number", "initial": "0"},
            {"name": "drawCalls", "type": "number", "initial": "0"},
            {"name": "triangles", "type": "number", "initial": "0"},
            {"name": "history", "type": "PerformanceSnapshot[]", "initial": "[]"},
            {"name": "isRecording", "type": "boolean", "initial": "false"},
        ],
        "features": [
            "fps_graph",
            "memory",
            "draw_calls",
            "profiler",
            "warnings",
            "export",
        ],
        "icon": "📊",
    },
    "TutorialOverlay": {
        "component_name": "TutorialOverlay",
        "description": "Interactive onboarding and tutorial system",
        "phase": 5,
        "props": [
            {"name": "tutorialId", "type": "string", "required": False},
            {
                "name": "onComplete",
                "type": "(tutorialId: string) => void",
                "required": False,
            },
            {"name": "onSkip", "type": "() => void", "required": False},
        ],
        "state_vars": [
            {"name": "currentStep", "type": "number", "initial": "0"},
            {"name": "steps", "type": "TutorialStep[]", "initial": "[]"},
            {"name": "isVisible", "type": "boolean", "initial": "false"},
            {
                "name": "completedTutorials",
                "type": "Set<string>",
                "initial": "new Set()",
            },
            {"name": "highlightedElement", "type": "string | null", "initial": "null"},
        ],
        "features": ["steps", "highlights", "tooltips", "progress", "skip", "replay"],
        "icon": "📖",
    },
    "CommandPalette": {
        "component_name": "CommandPalette",
        "description": "Quick command and action search palette",
        "phase": 5,
        "props": [
            {"name": "isOpen", "type": "boolean", "required": True},
            {"name": "onClose", "type": "() => void", "required": True},
            {
                "name": "onCommandExecute",
                "type": "(command: Command) => void",
                "required": False,
            },
        ],
        "state_vars": [
            {"name": "query", "type": "string", "initial": "''"},
            {"name": "commands", "type": "Command[]", "initial": "[]"},
            {"name": "filteredCommands", "type": "Command[]", "initial": "[]"},
            {"name": "selectedIndex", "type": "number", "initial": "0"},
            {"name": "recentCommands", "type": "Command[]", "initial": "[]"},
        ],
        "features": ["search", "categories", "shortcuts", "recent", "fuzzy_match"],
        "icon": "⌘",
    },
}

# =============================================================================
# MARATHON PRESETS
# =============================================================================

MARATHON_PHASES = {
    1: {
        "name": "Core Editor Panels",
        "milestone": "Full Editor Layout",
        "components": PHASE_1_COMPONENTS,
        "description": "Essential panels for the editor interface",
    },
    2: {
        "name": "Creative Tools",
        "milestone": "Full Creative Suite",
        "components": PHASE_2_COMPONENTS,
        "description": "Tools for creating animations, materials, particles, and audio",
    },
    3: {
        "name": "Advanced Systems",
        "milestone": "Professional Features",
        "components": PHASE_3_COMPONENTS,
        "description": "Professional-grade features for serious development",
    },
    4: {
        "name": "Project & Workflow",
        "milestone": "Production Ready",
        "components": PHASE_4_COMPONENTS,
        "description": "Production workflow and project management tools",
    },
    5: {
        "name": "Intelligence & Polish",
        "milestone": "AI-Enhanced Complete System",
        "components": PHASE_5_COMPONENTS,
        "description": "AI assistance, performance monitoring, and polish",
    },
}

# All components combined
ALL_MARATHON_COMPONENTS = {
    **PHASE_1_COMPONENTS,
    **PHASE_2_COMPONENTS,
    **PHASE_3_COMPONENTS,
    **PHASE_4_COMPONENTS,
    **PHASE_5_COMPONENTS,
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_phase_components(phase: int) -> Dict[str, Any]:
    """Get all components for a specific phase"""
    return MARATHON_PHASES.get(phase, {}).get("components", {})


def get_phase_info(phase: int) -> Dict[str, Any]:
    """Get phase metadata"""
    return MARATHON_PHASES.get(phase, {})


def get_all_components() -> Dict[str, Any]:
    """Get all marathon components"""
    return ALL_MARATHON_COMPONENTS


def get_component_count_by_phase() -> Dict[int, int]:
    """Get component count for each phase"""
    return {phase: len(info["components"]) for phase, info in MARATHON_PHASES.items()}


def get_total_component_count() -> int:
    """Get total number of components"""
    return sum(get_component_count_by_phase().values())


def print_marathon_summary():
    """Print a summary of the marathon plan"""
    print("=" * 60)
    print("🐆 CHEETAH V3 PRO - MARATHON RUN PLAN")
    print("=" * 60)

    total = 0
    for phase, info in MARATHON_PHASES.items():
        count = len(info["components"])
        total += count
        print(f"\n📍 PHASE {phase}: {info['name']}")
        print(f"   Milestone: {info['milestone']}")
        print(f"   Components: {count}")
        print(f"   {info['description']}")
        print(f"   Components:")
        for comp_name, comp_info in info["components"].items():
            print(f"      {comp_info['icon']} {comp_name}")

    print(f"\n{'=' * 60}")
    print(f"📊 TOTAL COMPONENTS TO BUILD: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    print_marathon_summary()
