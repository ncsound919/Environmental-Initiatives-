/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CHEETAH v3 PRO - PHASE TEMPLATES INDEX
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Master index for all phase templates in the Overlay Game Maker UI system.
 *
 * Phases Overview:
 * - Phase 1: Core Editor Panels (Full Editor Layout)
 * - Phase 2: Creative Tools (Full Creative Suite)
 * - Phase 3: Advanced Systems (Professional Features)
 * - Phase 4: Project & Workflow (Production Ready)
 * - Phase 5: Intelligence & Polish (AI-Enhanced Complete System)
 *
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// Phase 1: Core Editor Panels
export {
  SceneHierarchyPanelTemplate,
  InspectorPanelTemplate,
  ConsolePanelTemplate,
  ToolbarPanelTemplate,
  Phase1EditorLayoutTemplate,
} from './phase1_core_editor.template';

// Phase 2: Creative Tools
export {
  TimelineEditor,
  MaterialEditor,
  ParticleEditor,
  AudioMixerPanel,
} from './phase2_creative_tools.template';

// Phase 3: Advanced Systems
export {
  PrefabManager,
  LightingEditor,
  PhysicsPanel,
  InputManager,
} from './phase3_advanced_systems.template';

// Phase 4: Project & Workflow
export {
  BuildPanel,
  VersionControlPanel,
  PluginManager,
  LocalizationPanel,
} from './phase4_project_workflow.template';

// Phase 5: Intelligence & Polish
export {
  AIAssistantPanel,
  PerformanceMonitor,
  TutorialOverlay,
  CommandPalette,
} from './phase5_intelligence_polish.template';

// Type exports from each phase
export type {
  // Phase 1 Types
  GameObject,
  GameComponent,
  Transform,
  ConsoleLog,
  EditorTool,
} from './phase1_core_editor.template';

export type {
  // Phase 2 Types
  Keyframe,
  AnimationTrack,
  Material,
  ParticleModule,
  ParticleSystem,
  AudioChannel,
} from './phase2_creative_tools.template';

export type {
  // Phase 3 Types
  Prefab,
  PrefabVariant,
  Light,
  LightingSettings,
  Vector3,
  PhysicsSettings,
  PhysicsLayer,
  PhysicsMaterial,
  InputAction,
  InputBinding,
  InputMapping,
} from './phase3_advanced_systems.template';

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE METADATA
// ═══════════════════════════════════════════════════════════════════════════════

export const PHASE_METADATA = {
  phase1: {
    name: 'Core Editor Panels',
    milestone: 'Full Editor Layout',
    components: ['SceneHierarchyPanel', 'InspectorPanel', 'ConsolePanel', 'ToolbarPanel'],
    description: 'Essential panels for the editor interface',
    icon: '🎯',
  },
  phase2: {
    name: 'Creative Tools',
    milestone: 'Full Creative Suite',
    components: ['TimelineEditor', 'MaterialEditor', 'ParticleEditor', 'AudioMixerPanel'],
    description: 'Tools for creating animations, materials, particles, and audio',
    icon: '🎨',
  },
  phase3: {
    name: 'Advanced Systems',
    milestone: 'Professional Features',
    components: ['PrefabManager', 'LightingEditor', 'PhysicsPanel', 'InputManager'],
    description: 'Professional-grade features for serious development',
    icon: '⚙️',
  },
  phase4: {
    name: 'Project & Workflow',
    milestone: 'Production Ready',
    components: ['BuildPanel', 'VersionControlPanel', 'PluginManager', 'LocalizationPanel'],
    description: 'Production workflow and project management tools',
    icon: '🚀',
  },
  phase5: {
    name: 'Intelligence & Polish',
    milestone: 'AI-Enhanced Complete System',
    components: ['AIAssistantPanel', 'PerformanceMonitor', 'TutorialOverlay', 'CommandPalette'],
    description: 'AI assistance, performance monitoring, and polish',
    icon: '🤖',
  },
} as const;

export const TOTAL_COMPONENTS = Object.values(PHASE_METADATA).reduce(
  (sum, phase) => sum + phase.components.length,
  0
);

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get phase information by phase number
 */
export function getPhaseInfo(phaseNumber: 1 | 2 | 3 | 4 | 5) {
  const key = `phase${phaseNumber}` as keyof typeof PHASE_METADATA;
  return PHASE_METADATA[key];
}

/**
 * Get all component names across all phases
 */
export function getAllComponentNames(): string[] {
  return Object.values(PHASE_METADATA).flatMap(phase => phase.components);
}

/**
 * Find which phase a component belongs to
 */
export function getComponentPhase(componentName: string): number | null {
  for (let i = 1; i <= 5; i++) {
    const phase = PHASE_METADATA[`phase${i}` as keyof typeof PHASE_METADATA];
    if (phase.components.includes(componentName)) {
      return i;
    }
  }
  return null;
}

// Default export with all phases
export default {
  PHASE_METADATA,
  TOTAL_COMPONENTS,
  getPhaseInfo,
  getAllComponentNames,
  getComponentPhase,
};
