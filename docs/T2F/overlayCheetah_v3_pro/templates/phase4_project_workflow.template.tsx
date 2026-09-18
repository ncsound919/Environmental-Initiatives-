/**
 * ============================================================================
 * PHASE 4: PROJECT & WORKFLOW TEMPLATES
 * ============================================================================
 * Milestone: Production Ready
 * Description: Production workflow and project management tools
 *
 * Components in this phase:
 * - BuildPanel: Build and export settings for multiple platforms
 * - VersionControlPanel: Git integration and version history
 * - PluginManager: Install and manage editor plugins/extensions
 * - LocalizationPanel: Multi-language text and asset management
 * ============================================================================
 */

import React, { useState, useCallback, useMemo, memo } from 'react';

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

// Build Panel Types
interface BuildConfig {
  outputPath: string;
  compressionLevel: 'none' | 'low' | 'medium' | 'high';
  debugMode: boolean;
  includeSourceMaps: boolean;
  minify: boolean;
  splitChunks: boolean;
}

interface BuildResult {
  success: boolean;
  outputPath: string;
  size: number;
  duration: number;
  errors: string[];
  warnings: string[];
}

interface BuildPanelProps {
  projectId: string;
  onBuild?: (platform: string, config: BuildConfig) => void;
  onBuildComplete?: (result: BuildResult) => void;
}

// Version Control Types
interface FileChange {
  path: string;
  status: 'added' | 'modified' | 'deleted' | 'renamed';
  additions: number;
  deletions: number;
}

interface Commit {
  sha: string;
  message: string;
  author: string;
  date: string;
  files: string[];
}

interface VersionControlPanelProps {
  projectId: string;
  onCommit?: (message: string, files: string[]) => void;
  onPush?: () => void;
  onPull?: () => void;
}

// Plugin Manager Types
interface Plugin {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  category: string;
  enabled: boolean;
  installed: boolean;
  updateAvailable?: boolean;
  icon?: string;
  downloads?: number;
  rating?: number;
}

interface PluginManagerProps {
  onPluginInstall?: (pluginId: string) => void;
  onPluginUninstall?: (pluginId: string) => void;
  onPluginToggle?: (pluginId: string, enabled: boolean) => void;
}

// Localization Types
interface LocalizationString {
  key: string;
  values: Record<string, string>;
  description?: string;
  context?: string;
}

interface LocalizationPanelProps {
  projectId: string;
  onLocaleChange?: (locale: string) => void;
  onStringUpdate?: (key: string, locale: string, value: string) => void;
}

// =============================================================================
// SHARED STYLES
// =============================================================================

const phase4Styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
    backgroundColor: '#1e1e2e',
    color: '#cdd6f4',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: '13px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    backgroundColor: '#313244',
    borderBottom: '1px solid #45475a',
  },
  headerTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    margin: 0,
    fontSize: '14px',
    fontWeight: 600,
    color: '#cdd6f4',
  },
  headerIcon: {
    fontSize: '16px',
  },
  content: {
    flex: 1,
    overflow: 'auto',
    padding: '16px',
  },
  section: {
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#a6adc8',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    marginBottom: '12px',
  },
  button: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    padding: '8px 16px',
    backgroundColor: '#89b4fa',
    color: '#1e1e2e',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  buttonSecondary: {
    backgroundColor: '#45475a',
    color: '#cdd6f4',
  },
  buttonDanger: {
    backgroundColor: '#f38ba8',
    color: '#1e1e2e',
  },
  buttonSuccess: {
    backgroundColor: '#a6e3a1',
    color: '#1e1e2e',
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: '#313244',
    border: '1px solid #45475a',
    borderRadius: '6px',
    color: '#cdd6f4',
    fontSize: '13px',
    outline: 'none',
  },
  select: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: '#313244',
    border: '1px solid #45475a',
    borderRadius: '6px',
    color: '#cdd6f4',
    fontSize: '13px',
    outline: 'none',
    cursor: 'pointer',
  },
  card: {
    backgroundColor: '#313244',
    borderRadius: '8px',
    border: '1px solid #45475a',
    overflow: 'hidden',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    backgroundColor: '#45475a',
    borderBottom: '1px solid #585b70',
  },
  cardContent: {
    padding: '16px',
  },
  grid: {
    display: 'grid',
    gap: '12px',
  },
  flexRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  flexColumn: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 8px',
    backgroundColor: '#45475a',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 500,
  },
  badgeSuccess: {
    backgroundColor: 'rgba(166, 227, 161, 0.2)',
    color: '#a6e3a1',
  },
  badgeWarning: {
    backgroundColor: 'rgba(249, 226, 175, 0.2)',
    color: '#f9e2af',
  },
  badgeDanger: {
    backgroundColor: 'rgba(243, 139, 168, 0.2)',
    color: '#f38ba8',
  },
  badgeInfo: {
    backgroundColor: 'rgba(137, 180, 250, 0.2)',
    color: '#89b4fa',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#45475a',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#89b4fa',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
  },
  tableHeader: {
    textAlign: 'left' as const,
    padding: '10px 12px',
    backgroundColor: '#45475a',
    fontSize: '12px',
    fontWeight: 600,
    color: '#a6adc8',
    borderBottom: '1px solid #585b70',
  },
  tableCell: {
    padding: '10px 12px',
    borderBottom: '1px solid #45475a',
  },
  checkbox: {
    width: '16px',
    height: '16px',
    accentColor: '#89b4fa',
    cursor: 'pointer',
  },
  toggle: {
    position: 'relative' as const,
    width: '40px',
    height: '20px',
    backgroundColor: '#45475a',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  },
  toggleActive: {
    backgroundColor: '#89b4fa',
  },
  toggleKnob: {
    position: 'absolute' as const,
    top: '2px',
    left: '2px',
    width: '16px',
    height: '16px',
    backgroundColor: '#cdd6f4',
    borderRadius: '50%',
    transition: 'transform 0.2s ease',
  },
  toggleKnobActive: {
    transform: 'translateX(20px)',
  },
};

// =============================================================================
// BUILD PANEL COMPONENT
// =============================================================================

const PLATFORMS = [
  { id: 'windows', name: 'Windows', icon: '🪟' },
  { id: 'macos', name: 'macOS', icon: '🍎' },
  { id: 'linux', name: 'Linux', icon: '🐧' },
  { id: 'web', name: 'Web (HTML5)', icon: '🌐' },
  { id: 'android', name: 'Android', icon: '🤖' },
  { id: 'ios', name: 'iOS', icon: '📱' },
];

export const BuildPanel: React.FC<BuildPanelProps> = memo(({ projectId, onBuild, onBuildComplete }) => {
  const [selectedPlatform, setSelectedPlatform] = useState('windows');
  const [buildConfig, setBuildConfig] = useState<BuildConfig>({
    outputPath: './build',
    compressionLevel: 'medium',
    debugMode: false,
    includeSourceMaps: false,
    minify: true,
    splitChunks: true,
  });
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [buildLogs, setBuildLogs] = useState<string[]>([]);

  const handleBuild = useCallback(() => {
    setIsBuilding(true);
    setBuildProgress(0);
    setBuildLogs(['Starting build process...']);

    // Simulate build progress
    const stages = [
      'Compiling scripts...',
      'Processing assets...',
      'Optimizing textures...',
      'Bundling modules...',
      'Generating output...',
      'Build complete!',
    ];

    stages.forEach((stage, index) => {
      setTimeout(() => {
        setBuildLogs(prev => [...prev, stage]);
        setBuildProgress(((index + 1) / stages.length) * 100);

        if (index === stages.length - 1) {
          setIsBuilding(false);
          onBuild?.(selectedPlatform, buildConfig);
          onBuildComplete?.({
            success: true,
            outputPath: buildConfig.outputPath,
            size: 45.2 * 1024 * 1024,
            duration: 12500,
            errors: [],
            warnings: ['Consider enabling tree shaking for smaller builds'],
          });
        }
      }, (index + 1) * 800);
    });
  }, [selectedPlatform, buildConfig, onBuild, onBuildComplete]);

  const updateConfig = useCallback((key: keyof BuildConfig, value: any) => {
    setBuildConfig(prev => ({ ...prev, [key]: value }));
  }, []);

  return (
    <div style={phase4Styles.container}>
      <div style={phase4Styles.header}>
        <h3 style={phase4Styles.headerTitle}>
          <span style={phase4Styles.headerIcon}>🔨</span>
          Build Settings
        </h3>
        <button
          style={{
            ...phase4Styles.button,
            ...(isBuilding ? phase4Styles.buttonSecondary : phase4Styles.buttonSuccess),
          }}
          onClick={handleBuild}
          disabled={isBuilding}
        >
          {isBuilding ? '⏳ Building...' : '▶️ Build'}
        </button>
      </div>

      <div style={phase4Styles.content}>
        {/* Platform Selection */}
        <div style={phase4Styles.section}>
          <div style={phase4Styles.sectionTitle}>Target Platform</div>
          <div style={{ ...phase4Styles.grid, gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {PLATFORMS.map(platform => (
              <div
                key={platform.id}
                onClick={() => setSelectedPlatform(platform.id)}
                style={{
                  ...phase4Styles.card,
                  cursor: 'pointer',
                  padding: '16px',
                  textAlign: 'center' as const,
                  borderColor: selectedPlatform === platform.id ? '#89b4fa' : '#45475a',
                  backgroundColor: selectedPlatform === platform.id ? 'rgba(137, 180, 250, 0.1)' : '#313244',
                }}
              >
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>{platform.icon}</div>
                <div style={{ fontWeight: 500 }}>{platform.name}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Build Configuration */}
        <div style={phase4Styles.section}>
          <div style={phase4Styles.sectionTitle}>Configuration</div>
          <div style={phase4Styles.card}>
            <div style={phase4Styles.cardContent}>
              <div style={{ ...phase4Styles.flexColumn, gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', color: '#a6adc8' }}>
                    Output Path
                  </label>
                  <input
                    type="text"
                    value={buildConfig.outputPath}
                    onChange={(e) => updateConfig('outputPath', e.target.value)}
                    style={phase4Styles.input}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '6px', color: '#a6adc8' }}>
                    Compression Level
                  </label>
                  <select
                    value={buildConfig.compressionLevel}
                    onChange={(e) => updateConfig('compressionLevel', e.target.value)}
                    style={phase4Styles.select}
                  >
                    <option value="none">None (Fastest)</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium (Recommended)</option>
                    <option value="high">High (Smallest)</option>
                  </select>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  {[
                    { key: 'debugMode', label: 'Debug Mode' },
                    { key: 'includeSourceMaps', label: 'Source Maps' },
                    { key: 'minify', label: 'Minify Code' },
                    { key: 'splitChunks', label: 'Split Chunks' },
                  ].map(({ key, label }) => (
                    <label key={key} style={{ ...phase4Styles.flexRow, cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={buildConfig[key as keyof BuildConfig] as boolean}
                        onChange={(e) => updateConfig(key as keyof BuildConfig, e.target.checked)}
                        style={phase4Styles.checkbox}
                      />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Build Progress */}
        {(isBuilding || buildLogs.length > 0) && (
          <div style={phase4Styles.section}>
            <div style={phase4Styles.sectionTitle}>Build Progress</div>
            <div style={phase4Styles.card}>
              <div style={phase4Styles.cardContent}>
                <div style={phase4Styles.progressBar}>
                  <div
                    style={{
                      ...phase4Styles.progressFill,
                      width: `${buildProgress}%`,
                      backgroundColor: buildProgress === 100 ? '#a6e3a1' : '#89b4fa',
                    }}
                  />
                </div>
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#a6adc8' }}>
                  {buildProgress.toFixed(0)}% Complete
                </div>
                <div
                  style={{
                    marginTop: '12px',
                    padding: '12px',
                    backgroundColor: '#1e1e2e',
                    borderRadius: '4px',
                    maxHeight: '150px',
                    overflow: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '11px',
                  }}
                >
                  {buildLogs.map((log, index) => (
                    <div key={index} style={{ color: log.includes('complete') ? '#a6e3a1' : '#cdd6f4' }}>
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

BuildPanel.displayName = 'BuildPanel';

// =============================================================================
// VERSION CONTROL PANEL COMPONENT
// =============================================================================

const MOCK_CHANGES: FileChange[] = [
  { path: 'src/scenes/MainMenu.ts', status: 'modified', additions: 45, deletions: 12 },
  { path: 'src/entities/Player.ts', status: 'modified', additions: 23, deletions: 8 },
  { path: 'src/components/HealthBar.ts', status: 'added', additions: 87, deletions: 0 },
  { path: 'assets/sprites/enemy.png', status: 'added', additions: 0, deletions: 0 },
  { path: 'src/utils/deprecated.ts', status: 'deleted', additions: 0, deletions: 156 },
];

const MOCK_COMMITS: Commit[] = [
  { sha: 'a1b2c3d', message: 'Add health bar component', author: 'developer', date: '2024-01-15 14:32', files: ['src/components/HealthBar.ts'] },
  { sha: 'e4f5g6h', message: 'Fix player movement bug', author: 'developer', date: '2024-01-15 12:15', files: ['src/entities/Player.ts'] },
  { sha: 'i7j8k9l', message: 'Update main menu layout', author: 'developer', date: '2024-01-14 18:45', files: ['src/scenes/MainMenu.ts'] },
  { sha: 'm0n1o2p', message: 'Initial commit', author: 'developer', date: '2024-01-14 10:00', files: ['README.md', 'package.json'] },
];

export const VersionControlPanel: React.FC<VersionControlPanelProps> = memo(({
  projectId,
  onCommit,
  onPush,
  onPull
}) => {
  const [changes] = useState<FileChange[]>(MOCK_CHANGES);
  const [commits] = useState<Commit[]>(MOCK_COMMITS);
  const [currentBranch, setCurrentBranch] = useState('main');
  const [branches] = useState(['main', 'develop', 'feature/new-ui']);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [commitMessage, setCommitMessage] = useState('');
  const [activeTab, setActiveTab] = useState<'changes' | 'history'>('changes');

  const toggleFileSelection = useCallback((path: string) => {
    setSelectedFiles(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const selectAllFiles = useCallback(() => {
    if (selectedFiles.size === changes.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(changes.map(c => c.path)));
    }
  }, [changes, selectedFiles.size]);

  const handleCommit = useCallback(() => {
    if (commitMessage.trim() && selectedFiles.size > 0) {
      onCommit?.(commitMessage, Array.from(selectedFiles));
      setCommitMessage('');
      setSelectedFiles(new Set());
    }
  }, [commitMessage, selectedFiles, onCommit]);

  const getStatusColor = (status: FileChange['status']) => {
    switch (status) {
      case 'added': return '#a6e3a1';
      case 'modified': return '#f9e2af';
      case 'deleted': return '#f38ba8';
      case 'renamed': return '#89b4fa';
      default: return '#cdd6f4';
    }
  };

  const getStatusIcon = (status: FileChange['status']) => {
    switch (status) {
      case 'added': return '+';
      case 'modified': return '~';
      case 'deleted': return '-';
      case 'renamed': return '→';
      default: return '?';
    }
  };

  return (
    <div style={phase4Styles.container}>
      <div style={phase4Styles.header}>
        <h3 style={phase4Styles.headerTitle}>
          <span style={phase4Styles.headerIcon}>📚</span>
          Version Control
        </h3>
        <div style={phase4Styles.flexRow}>
          <select
            value={currentBranch}
            onChange={(e) => setCurrentBranch(e.target.value)}
            style={{ ...phase4Styles.select, width: 'auto', padding: '6px 12px' }}
          >
            {branches.map(branch => (
              <option key={branch} value={branch}>{branch}</option>
            ))}
          </select>
          <button style={{ ...phase4Styles.button, ...phase4Styles.buttonSecondary, padding: '6px 12px' }} onClick={onPull}>
            ⬇️ Pull
          </button>
          <button style={{ ...phase4Styles.button, padding: '6px 12px' }} onClick={onPush}>
            ⬆️ Push
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #45475a' }}>
        {(['changes', 'history'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '12px',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #89b4fa' : '2px solid transparent',
              color: activeTab === tab ? '#89b4fa' : '#a6adc8',
              cursor: 'pointer',
              fontWeight: 500,
              textTransform: 'capitalize',
            }}
          >
            {tab === 'changes' ? `Changes (${changes.length})` : 'History'}
          </button>
        ))}
      </div>

      <div style={phase4Styles.content}>
        {activeTab === 'changes' ? (
          <>
            {/* Staged Files */}
            <div style={phase4Styles.section}>
              <div style={{ ...phase4Styles.flexRow, justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={phase4Styles.sectionTitle}>Changed Files</div>
                <button
                  onClick={selectAllFiles}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#89b4fa',
                    cursor: 'pointer',
                    fontSize: '12px',
                  }}
                >
                  {selectedFiles.size === changes.length ? 'Deselect All' : 'Select All'}
                </button>
              </div>

              <div style={phase4Styles.card}>
                {changes.map(change => (
                  <div
                    key={change.path}
                    onClick={() => toggleFileSelection(change.path)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '10px 12px',
                      borderBottom: '1px solid #45475a',
                      cursor: 'pointer',
                      backgroundColor: selectedFiles.has(change.path) ? 'rgba(137, 180, 250, 0.1)' : 'transparent',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedFiles.has(change.path)}
                      onChange={() => {}}
                      style={phase4Styles.checkbox}
                    />
                    <span
                      style={{
                        width: '20px',
                        textAlign: 'center',
                        fontWeight: 'bold',
                        color: getStatusColor(change.status),
                      }}
                    >
                      {getStatusIcon(change.status)}
                    </span>
                    <span style={{ flex: 1, fontFamily: 'monospace', fontSize: '12px' }}>
                      {change.path}
                    </span>
                    <span style={{ fontSize: '11px', color: '#a6adc8' }}>
                      {change.additions > 0 && <span style={{ color: '#a6e3a1' }}>+{change.additions}</span>}
                      {change.additions > 0 && change.deletions > 0 && ' / '}
                      {change.deletions > 0 && <span style={{ color: '#f38ba8' }}>-{change.deletions}</span>}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Commit Form */}
            <div style={phase4Styles.section}>
              <div style={phase4Styles.sectionTitle}>Commit</div>
              <div style={phase4Styles.card}>
                <div style={phase4Styles.cardContent}>
                  <textarea
                    value={commitMessage}
                    onChange={(e) => setCommitMessage(e.target.value)}
                    placeholder="Enter commit message..."
                    style={{
                      ...phase4Styles.input,
                      minHeight: '80px',
                      resize: 'vertical' as const,
                    }}
                  />
                  <button
                    onClick={handleCommit}
                    disabled={!commitMessage.trim() || selectedFiles.size === 0}
                    style={{
                      ...phase4Styles.button,
                      ...phase4Styles.buttonSuccess,
                      marginTop: '12px',
                      width: '100%',
                      opacity: (!commitMessage.trim() || selectedFiles.size === 0) ? 0.5 : 1,
                    }}
                  >
                    ✓ Commit {selectedFiles.size > 0 ? `(${selectedFiles.size} files)` : ''}
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* History */
          <div style={phase4Styles.section}>
            <div style={phase4Styles.sectionTitle}>Commit History</div>
            <div style={phase4Styles.card}>
              {commits.map((commit, index) => (
                <div
                  key={commit.sha}
                  style={{
                    padding: '12px 16px',
                    borderBottom: index < commits.length - 1 ? '1px solid #45475a' : 'none',
                  }}
                >
                  <div style={{ ...phase4Styles.flexRow, justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 500 }}>{commit.message}</span>
                    <code style={{ fontSize: '11px', color: '#89b4fa' }}>{commit.sha}</code>
                  </div>
                  <div style={{ fontSize: '11px', color: '#a6adc8' }}>
                    {commit.author} • {commit.date}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

VersionControlPanel.displayName = 'VersionControlPanel';

// =============================================================================
// PLUGIN MANAGER COMPONENT
// =============================================================================

const MOCK_INSTALLED_PLUGINS: Plugin[] = [
  { id: 'terrain-editor', name: 'Terrain Editor Pro', version: '2.1.0', author: 'GameDev Tools', description: 'Advanced terrain sculpting and painting', category: 'Tools', enabled: true, installed: true, icon: '🏔️' },
  { id: 'dialogue-system', name: 'Dialogue System', version: '1.5.2', author: 'StoryWorks', description: 'Visual dialogue tree editor', category: 'Narrative', enabled: true, installed: true, updateAvailable: true, icon: '💬' },
  { id: 'shader-graph', name: 'Visual Shader Graph', version: '3.0.0', author: 'VFX Masters', description: 'Node-based shader creation', category: 'Graphics', enabled: false, installed: true, icon: '✨' },
];

const MOCK_AVAILABLE_PLUGINS: Plugin[] = [
  { id: 'ai-nav', name: 'AI Navigation', version: '1.0.0', author: 'PathFinders', description: 'Automatic navmesh generation and pathfinding', category: 'AI', enabled: false, installed: false, downloads: 15420, rating: 4.8, icon: '🧭' },
  { id: 'cutscene-editor', name: 'Cutscene Director', version: '2.2.1', author: 'CinematicPro', description: 'Timeline-based cutscene creation', category: 'Narrative', enabled: false, installed: false, downloads: 8930, rating: 4.5, icon: '🎬' },
  { id: 'procedural-gen', name: 'Procedural Generator', version: '1.3.0', author: 'RandomWorks', description: 'Procedural level and content generation', category: 'Tools', enabled: false, installed: false, downloads: 12100, rating: 4.6, icon: '🎲' },
];

export const PluginManager: React.FC<PluginManagerProps> = memo(({
  onPluginInstall,
  onPluginUninstall,
  onPluginToggle
}) => {
  const [installedPlugins, setInstalledPlugins] = useState<Plugin[]>(MOCK_INSTALLED_PLUGINS);
  const [availablePlugins] = useState<Plugin[]>(MOCK_AVAILABLE_PLUGINS);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [activeTab, setActiveTab] = useState<'installed' | 'browse'>('installed');

  const categories = useMemo(() => {
    const cats = new Set<string>();
    [...installedPlugins, ...availablePlugins].forEach(p => cats.add(p.category));
    return ['all', ...Array.from(cats)];
  }, [installedPlugins, availablePlugins]);

  const filteredPlugins = useMemo(() => {
    const plugins = activeTab === 'installed' ? installedPlugins : availablePlugins;
    return plugins.filter(plugin => {
      const matchesSearch = plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           plugin.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || plugin.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [activeTab, installedPlugins, availablePlugins, searchQuery, categoryFilter]);

  const handleToggle = useCallback((pluginId: string) => {
    setInstalledPlugins(prev => prev.map(p =>
      p.id === pluginId ? { ...p, enabled: !p.enabled } : p
    ));
    const plugin = installedPlugins.find(p => p.id === pluginId);
    if (plugin) {
      onPluginToggle?.(pluginId, !plugin.enabled);
    }
  }, [installedPlugins, onPluginToggle]);

  const handleInstall = useCallback((pluginId: string) => {
    const plugin = availablePlugins.find(p => p.id === pluginId);
    if (plugin) {
      setInstalledPlugins(prev => [...prev, { ...plugin, installed: true, enabled: true }]);
      onPluginInstall?.(pluginId);
    }
  }, [availablePlugins, onPluginInstall]);

  const handleUninstall = useCallback((pluginId: string) => {
    setInstalledPlugins(prev => prev.filter(p => p.id !== pluginId));
    onPluginUninstall?.(pluginId);
  }, [onPluginUninstall]);

  return (
    <div style={phase4Styles.container}>
      <div style={phase4Styles.header}>
        <h3 style={phase4Styles.headerTitle}>
          <span style={phase4Styles.headerIcon}>🧩</span>
          Plugin Manager
        </h3>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #45475a' }}>
        {(['installed', 'browse'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '12px',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #89b4fa' : '2px solid transparent',
              color: activeTab === tab ? '#89b4fa' : '#a6adc8',
              cursor: 'pointer',
              fontWeight: 500,
              textTransform: 'capitalize',
            }}
          >
            {tab === 'installed' ? `Installed (${installedPlugins.length})` : 'Browse'}
          </button>
        ))}
      </div>

      {/* Search and Filter */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #45475a' }}>
        <div style={{ ...phase4Styles.flexRow, gap: '12px' }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search plugins..."
            style={{ ...phase4Styles.input, flex: 1 }}
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ ...phase4Styles.select, width: 'auto' }}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div style={phase4Styles.content}>
        <div style={{ ...phase4Styles.grid, gap: '16px' }}>
          {filteredPlugins.map(plugin => (
            <div key={plugin.id} style={phase4Styles.card}>
              <div style={{ padding: '16px' }}>
                <div style={{ ...phase4Styles.flexRow, justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={phase4Styles.flexRow}>
                    <span style={{ fontSize: '24px' }}>{plugin.icon}</span>
                    <div>
                      <div style={{ fontWeight: 600 }}>{plugin.name}</div>
                      <div style={{ fontSize: '11px', color: '#a6adc8' }}>
                        v{plugin.version} • {plugin.author}
                      </div>
                    </div>
                  </div>
                  <span style={{ ...phase4Styles.badge, ...phase4Styles.badgeInfo }}>
                    {plugin.category}
                  </span>
                </div>

                <p style={{ margin: '12px 0', fontSize: '12px', color: '#a6adc8' }}>
                  {plugin.description}
                </p>

                {/* Stats for available plugins */}
                {!plugin.installed && plugin.downloads && (
                  <div style={{ ...phase4Styles.flexRow, gap: '16px', marginBottom: '12px', fontSize: '11px', color: '#a6adc8' }}>
                    <span>⬇️ {plugin.downloads.toLocaleString()}</span>
                    <span>⭐ {plugin.rating}</span>
                  </div>
                )}

                <div style={{ ...phase4Styles.flexRow, justifyContent: 'space-between' }}>
                  {plugin.installed ? (
                    <>
                      <div
                        onClick={() => handleToggle(plugin.id)}
                        style={{
                          ...phase4Styles.toggle,
                          ...(plugin.enabled ? phase4Styles.toggleActive : {}),
                        }}
                      >
                        <div
                          style={{
                            ...phase4Styles.toggleKnob,
                            ...(plugin.enabled ? phase4Styles.toggleKnobActive : {}),
                          }}
                        />
                      </div>
                      <div style={phase4Styles.flexRow}>
                        {plugin.updateAvailable && (
                          <button style={{ ...phase4Styles.button, ...phase4Styles.buttonSuccess, padding: '6px 12px', fontSize: '11px' }}>
                            ⬆️ Update
                          </button>
                        )}
                        <button
                          onClick={() => handleUninstall(plugin.id)}
                          style={{ ...phase4Styles.button, ...phase4Styles.buttonDanger, padding: '6px 12px', fontSize: '11px' }}
                        >
                          🗑️ Uninstall
                        </button>
                      </div>
                    </>
                  ) : (
                    <button
                      onClick={() => handleInstall(plugin.id)}
                      style={{ ...phase4Styles.button, width: '100%' }}
                    >
                      ⬇️ Install
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

PluginManager.displayName = 'PluginManager';

// =============================================================================
// LOCALIZATION PANEL COMPONENT
// =============================================================================

const MOCK_STRINGS: LocalizationString[] = [
  { key: 'ui.menu.start', values: { en: 'Start Game', es: 'Iniciar Juego', fr: 'Démarrer', de: 'Spiel Starten', ja: 'ゲーム開始' }, description: 'Main menu start button' },
  { key: 'ui.menu.options', values: { en: 'Options', es: 'Opciones', fr: 'Options', de: 'Optionen', ja: 'オプション' }, description: 'Main menu options button' },
  { key: 'ui.menu.quit', values: { en: 'Quit', es: 'Salir', fr: 'Quitter', de: 'Beenden', ja: '終了' }, description: 'Main menu quit button' },
  { key: 'game.player.health', values: { en: 'Health', es: 'Salud', fr: 'Santé', de: 'Gesundheit', ja: '体力' }, description: 'Player health label' },
  { key: 'game.player.score', values: { en: 'Score', es: 'Puntuación', fr: 'Score', de: 'Punktzahl', ja: 'スコア' }, description: 'Player score label' },
  { key: 'dialog.npc.greeting', values: { en: 'Hello, traveler!', es: '¡Hola, viajero!', fr: 'Bonjour, voyageur!', de: 'Hallo, Reisender!', ja: '' }, description: 'NPC greeting dialogue' },
];

const LOCALE_FLAGS: Record<string, string> = {
  en: '🇺🇸',
  es: '🇪🇸',
  fr: '🇫🇷',
  de: '🇩🇪',
  ja: '🇯🇵',
};

export const LocalizationPanel: React.FC<LocalizationPanelProps> = memo(({
  projectId,
  onLocaleChange,
  onStringUpdate
}) => {
  const [locales] = useState(['en', 'es', 'fr', 'de', 'ja']);
  const [currentLocale, setCurrentLocale] = useState('en');
  const [strings, setStrings] = useState<LocalizationString[]>(MOCK_STRINGS);
  const [searchQuery, setSearchQuery] = useState('');
  const [missingOnly, setMissingOnly] = useState(false);
  const [editingCell, setEditingCell] = useState<{ key: string; locale: string } | null>(null);
  const [editValue, setEditValue] = useState('');

  const filteredStrings = useMemo(() => {
    return strings.filter(str => {
      const matchesSearch = str.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           Object.values(str.values).some(v => v.toLowerCase().includes(searchQuery.toLowerCase()));
      const hasMissing = missingOnly ? locales.some(l => !str.values[l] || str.values[l].trim() === '') : true;
      return matchesSearch && hasMissing;
    });
  }, [strings, searchQuery, missingOnly, locales]);

  const stats = useMemo(() => {
    const total = strings.length * locales.length;
    const filled = strings.reduce((acc, str) =>
      acc + locales.filter(l => str.values[l] && str.values[l].trim() !== '').length, 0
    );
    return { total, filled, percentage: Math.round((filled / total) * 100) };
  }, [strings, locales]);

  const handleLocaleChange = useCallback((locale: string) => {
    setCurrentLocale(locale);
    onLocaleChange?.(locale);
  }, [onLocaleChange]);

  const startEditing = useCallback((key: string, locale: string, value: string) => {
    setEditingCell({ key, locale });
    setEditValue(value || '');
  }, []);

  const saveEdit = useCallback(() => {
    if (editingCell) {
      setStrings(prev => prev.map(str =>
        str.key === editingCell.key
          ? { ...str, values: { ...str.values, [editingCell.locale]: editValue } }
          : str
      ));
      onStringUpdate?.(editingCell.key, editingCell.locale, editValue);
      setEditingCell(null);
      setEditValue('');
    }
  }, [editingCell, editValue, onStringUpdate]);

  const cancelEdit = useCallback(() => {
    setEditingCell(null);
    setEditValue('');
  }, []);

  return (
    <div style={phase4Styles.container}>
      <div style={phase4Styles.header}>
        <h3 style={phase4Styles.headerTitle}>
          <span style={phase4Styles.headerIcon}>🌍</span>
          Localization
        </h3>
        <div style={phase4Styles.flexRow}>
          <span style={{ ...phase4Styles.badge, ...phase4Styles.badgeSuccess }}>
            {stats.percentage}% Complete
          </span>
          <button style={{ ...phase4Styles.button, ...phase4Styles.buttonSecondary, padding: '6px 12px' }}>
            📥 Import
          </button>
          <button style={{ ...phase4Styles.button, padding: '6px 12px' }}>
            📤 Export
          </button>
        </div>
      </div>

      {/* Locale Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #45475a', overflow: 'auto' }}>
        {locales.map(locale => (
          <button
            key={locale}
            onClick={() => handleLocaleChange(locale)}
            style={{
              padding: '12px 20px',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: currentLocale === locale ? '2px solid #89b4fa' : '2px solid transparent',
              color: currentLocale === locale ? '#89b4fa' : '#a6adc8',
              cursor: 'pointer',
              fontWeight: 500,
              whiteSpace: 'nowrap',
            }}
          >
            {LOCALE_FLAGS[locale]} {locale.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Search and Filter */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #45475a' }}>
        <div style={{ ...phase4Styles.flexRow, gap: '12px' }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search keys or values..."
            style={{ ...phase4Styles.input, flex: 1 }}
          />
          <label style={{ ...phase4Styles.flexRow, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={missingOnly}
              onChange={(e) => setMissingOnly(e.target.checked)}
              style={phase4Styles.checkbox}
            />
            <span>Missing only</span>
          </label>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #45475a' }}>
        <div style={{ ...phase4Styles.flexRow, justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '12px', color: '#a6adc8' }}>Translation Progress</span>
          <span style={{ fontSize: '12px', color: '#a6adc8' }}>{stats.filled} / {stats.total}</span>
        </div>
        <div style={phase4Styles.progressBar}>
          <div style={{ ...phase4Styles.progressFill, width: `${stats.percentage}%` }} />
        </div>
      </div>

      <div style={{ ...phase4Styles.content, padding: 0 }}>
        <table style={phase4Styles.table}>
          <thead>
            <tr>
              <th style={{ ...phase4Styles.tableHeader, width: '250px' }}>Key</th>
              {locales.map(locale => (
                <th key={locale} style={phase4Styles.tableHeader}>
                  {LOCALE_FLAGS[locale]} {locale.toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredStrings.map(str => (
              <tr key={str.key}>
                <td style={{ ...phase4Styles.tableCell, fontFamily: 'monospace', fontSize: '11px' }}>
                  <div>{str.key}</div>
                  {str.description && (
                    <div style={{ fontSize: '10px', color: '#6c7086', marginTop: '4px' }}>
                      {str.description}
                    </div>
                  )}
                </td>
                {locales.map(locale => {
                  const value = str.values[locale] || '';
                  const isEmpty = !value.trim();
                  const isEditing = editingCell?.key === str.key && editingCell?.locale === locale;

                  return (
                    <td key={locale} style={phase4Styles.tableCell}>
                      {isEditing ? (
                        <div style={phase4Styles.flexRow}>
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') saveEdit();
                              if (e.key === 'Escape') cancelEdit();
                            }}
                            autoFocus
                            style={{ ...phase4Styles.input, padding: '6px 8px' }}
                          />
                          <button onClick={saveEdit} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>✓</button>
                          <button onClick={cancelEdit} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>✕</button>
                        </div>
                      ) : (
                        <div
                          onClick={() => startEditing(str.key, locale, value)}
                          style={{
                            padding: '6px 8px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            backgroundColor: isEmpty ? 'rgba(243, 139, 168, 0.1)' : 'transparent',
                            color: isEmpty ? '#f38ba8' : '#cdd6f4',
                            minHeight: '32px',
                          }}
                        >
                          {isEmpty ? '⚠️ Missing' : value}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});

LocalizationPanel.displayName = 'LocalizationPanel';

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  BuildPanel,
  VersionControlPanel,
  PluginManager,
  LocalizationPanel,
};
