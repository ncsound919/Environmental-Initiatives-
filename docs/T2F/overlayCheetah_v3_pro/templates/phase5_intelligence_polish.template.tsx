/**
 * ============================================================================
 * PHASE 5: INTELLIGENCE & POLISH TEMPLATES
 * ============================================================================
 * Milestone: AI-Enhanced Complete System
 *
 * Components in this phase:
 * - AIAssistantPanel: AI-powered code and asset generation assistant
 * - PerformanceMonitor: Real-time performance metrics and profiling
 * - TutorialOverlay: Interactive onboarding and tutorial system
 * - CommandPalette: Quick command and action search palette
 * ============================================================================
 */

import React, { useState, useCallback, useMemo, memo, useEffect, useRef } from 'react';

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

interface AIConversation {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'code' | 'asset' | 'dialog' | 'level';
}

interface AIResult {
  id: string;
  type: 'code' | 'asset' | 'dialog' | 'level';
  content: string;
  preview?: string;
  confidence: number;
}

interface PerformanceSnapshot {
  timestamp: number;
  fps: number;
  frameTime: number;
  memoryUsage: number;
  drawCalls: number;
  triangles: number;
}

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  target?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  action?: 'click' | 'input' | 'drag';
}

interface Command {
  id: string;
  name: string;
  category: string;
  shortcut?: string;
  icon?: string;
  action: () => void;
}

// =============================================================================
// SHARED STYLES
// =============================================================================

const phase5Styles = {
  panel: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
    backgroundColor: '#1e1e2e',
    color: '#cdd6f4',
    fontFamily: "'Segoe UI', system-ui, sans-serif",
    borderRadius: '8px',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    backgroundColor: '#181825',
    borderBottom: '1px solid #313244',
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
    padding: '16px',
    overflowY: 'auto' as const,
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
  button: {
    padding: '8px 16px',
    backgroundColor: '#89b4fa',
    border: 'none',
    borderRadius: '6px',
    color: '#1e1e2e',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  buttonSecondary: {
    padding: '8px 16px',
    backgroundColor: 'transparent',
    border: '1px solid #45475a',
    borderRadius: '6px',
    color: '#cdd6f4',
    fontSize: '13px',
    cursor: 'pointer',
  },
  badge: {
    padding: '2px 8px',
    backgroundColor: '#45475a',
    borderRadius: '10px',
    fontSize: '11px',
    color: '#a6adc8',
  },
  card: {
    backgroundColor: '#313244',
    borderRadius: '8px',
    padding: '12px',
    border: '1px solid #45475a',
  },
};

// =============================================================================
// AI ASSISTANT PANEL
// =============================================================================

interface AIAssistantPanelProps {
  onGenerate?: (prompt: string, type: string) => void;
  onApply?: (result: AIResult) => void;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = memo(({
  onGenerate,
  onApply,
}) => {
  const [prompt, setPrompt] = useState('');
  const [history, setHistory] = useState<AIConversation[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationType, setGenerationType] = useState<'code' | 'asset' | 'dialog' | 'level'>('code');
  const [suggestions] = useState<string[]>([
    'Generate a player movement script',
    'Create a health bar UI component',
    'Design a main menu layout',
    'Write enemy AI behavior',
  ]);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleSubmit = useCallback(() => {
    if (!prompt.trim() || isGenerating) return;

    const userMessage: AIConversation = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date(),
      type: generationType,
    };

    setHistory(prev => [...prev, userMessage]);
    setIsGenerating(true);
    onGenerate?.(prompt, generationType);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: AIConversation = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: `Here's a ${generationType} solution for "${prompt}":\n\n// Generated ${generationType}\nclass Example {\n  // Implementation here\n}`,
        timestamp: new Date(),
        type: generationType,
      };
      setHistory(prev => [...prev, aiResponse]);
      setIsGenerating(false);
    }, 1500);

    setPrompt('');
  }, [prompt, generationType, isGenerating, onGenerate]);

  const generationTypes = [
    { value: 'code', label: '💻 Code', color: '#89b4fa' },
    { value: 'asset', label: '🎨 Asset', color: '#f9e2af' },
    { value: 'dialog', label: '💬 Dialog', color: '#a6e3a1' },
    { value: 'level', label: '🗺️ Level', color: '#cba6f7' },
  ];

  return (
    <div style={phase5Styles.panel}>
      <div style={phase5Styles.header}>
        <div style={phase5Styles.title}>
          <span>🤖</span>
          <span>AI Assistant</span>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          {generationTypes.map(type => (
            <button
              key={type.value}
              onClick={() => setGenerationType(type.value as typeof generationType)}
              style={{
                padding: '4px 10px',
                backgroundColor: generationType === type.value ? type.color : 'transparent',
                border: `1px solid ${type.color}`,
                borderRadius: '4px',
                color: generationType === type.value ? '#1e1e2e' : type.color,
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ ...phase5Styles.content, display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Chat History */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {history.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px', color: '#6c7086' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
              <div style={{ fontSize: '14px', marginBottom: '8px' }}>How can I help you today?</div>
              <div style={{ fontSize: '12px' }}>Ask me to generate code, assets, dialogs, or levels</div>
            </div>
          ) : (
            history.map(msg => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: '80%',
                    padding: '10px 14px',
                    backgroundColor: msg.role === 'user' ? '#89b4fa' : '#313244',
                    color: msg.role === 'user' ? '#1e1e2e' : '#cdd6f4',
                    borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                    fontSize: '13px',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))
          )}
          {isGenerating && (
            <div style={{ display: 'flex', gap: '8px', color: '#6c7086', fontSize: '13px' }}>
              <span>🤖</span>
              <span>Generating...</span>
              <span style={{ animation: 'pulse 1s infinite' }}>●</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Suggestions */}
        {history.length === 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => setPrompt(suggestion)}
                style={{
                  ...phase5Styles.buttonSecondary,
                  padding: '6px 12px',
                  fontSize: '12px',
                }}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder={`Describe what you want to ${generationType === 'code' ? 'create' : 'generate'}...`}
            style={{ ...phase5Styles.input, flex: 1 }}
          />
          <button
            onClick={handleSubmit}
            disabled={isGenerating || !prompt.trim()}
            style={{
              ...phase5Styles.button,
              opacity: isGenerating || !prompt.trim() ? 0.5 : 1,
            }}
          >
            {isGenerating ? '...' : '✨ Generate'}
          </button>
        </div>
      </div>
    </div>
  );
});

AIAssistantPanel.displayName = 'AIAssistantPanel';

// =============================================================================
// PERFORMANCE MONITOR
// =============================================================================

interface PerformanceMonitorProps {
  isEnabled?: boolean;
  onWarning?: (metric: string, value: number) => void;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = memo(({
  isEnabled = true,
  onWarning,
}) => {
  const [fps, setFps] = useState(60);
  const [frameTime, setFrameTime] = useState(16.67);
  const [memoryUsage, setMemoryUsage] = useState(256);
  const [drawCalls, setDrawCalls] = useState(150);
  const [triangles, setTriangles] = useState(125000);
  const [history, setHistory] = useState<PerformanceSnapshot[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [viewMode, setViewMode] = useState<'live' | 'history'>('live');

  // Simulate performance updates
  useEffect(() => {
    if (!isEnabled) return;

    const interval = setInterval(() => {
      const newFps = 55 + Math.random() * 10;
      const newFrameTime = 1000 / newFps;
      const newMemory = 200 + Math.random() * 100;
      const newDrawCalls = 100 + Math.floor(Math.random() * 100);
      const newTriangles = 100000 + Math.floor(Math.random() * 50000);

      setFps(newFps);
      setFrameTime(newFrameTime);
      setMemoryUsage(newMemory);
      setDrawCalls(newDrawCalls);
      setTriangles(newTriangles);

      if (newFps < 30) {
        onWarning?.('fps', newFps);
      }

      if (isRecording) {
        setHistory(prev => [...prev.slice(-59), {
          timestamp: Date.now(),
          fps: newFps,
          frameTime: newFrameTime,
          memoryUsage: newMemory,
          drawCalls: newDrawCalls,
          triangles: newTriangles,
        }]);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isEnabled, isRecording, onWarning]);

  const getFpsColor = (value: number) => {
    if (value >= 55) return '#a6e3a1';
    if (value >= 30) return '#f9e2af';
    return '#f38ba8';
  };

  const metrics = [
    { label: 'FPS', value: fps.toFixed(0), unit: '', color: getFpsColor(fps), icon: '📊' },
    { label: 'Frame Time', value: frameTime.toFixed(2), unit: 'ms', color: frameTime < 20 ? '#a6e3a1' : '#f9e2af', icon: '⏱️' },
    { label: 'Memory', value: memoryUsage.toFixed(0), unit: 'MB', color: memoryUsage < 400 ? '#a6e3a1' : '#f38ba8', icon: '💾' },
    { label: 'Draw Calls', value: drawCalls.toString(), unit: '', color: drawCalls < 200 ? '#a6e3a1' : '#f9e2af', icon: '🖌️' },
    { label: 'Triangles', value: (triangles / 1000).toFixed(1), unit: 'K', color: triangles < 150000 ? '#a6e3a1' : '#f9e2af', icon: '📐' },
  ];

  return (
    <div style={phase5Styles.panel}>
      <div style={phase5Styles.header}>
        <div style={phase5Styles.title}>
          <span>📊</span>
          <span>Performance Monitor</span>
          <span style={{
            ...phase5Styles.badge,
            backgroundColor: isEnabled ? '#a6e3a1' : '#45475a',
            color: isEnabled ? '#1e1e2e' : '#a6adc8',
          }}>
            {isEnabled ? 'LIVE' : 'PAUSED'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setIsRecording(!isRecording)}
            style={{
              ...phase5Styles.buttonSecondary,
              padding: '4px 10px',
              backgroundColor: isRecording ? '#f38ba8' : 'transparent',
              borderColor: isRecording ? '#f38ba8' : '#45475a',
              color: isRecording ? '#1e1e2e' : '#cdd6f4',
            }}
          >
            {isRecording ? '⏹️ Stop' : '⏺️ Record'}
          </button>
          <button
            onClick={() => setViewMode(viewMode === 'live' ? 'history' : 'live')}
            style={phase5Styles.buttonSecondary}
          >
            {viewMode === 'live' ? '📈 History' : '📊 Live'}
          </button>
        </div>
      </div>

      <div style={phase5Styles.content}>
        {/* Main FPS Display */}
        <div style={{
          textAlign: 'center',
          padding: '24px',
          backgroundColor: '#181825',
          borderRadius: '12px',
          marginBottom: '16px',
        }}>
          <div style={{ fontSize: '48px', fontWeight: 700, color: getFpsColor(fps) }}>
            {fps.toFixed(0)}
          </div>
          <div style={{ fontSize: '12px', color: '#6c7086', textTransform: 'uppercase' }}>
            Frames Per Second
          </div>
        </div>

        {/* Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '16px',
        }}>
          {metrics.slice(1).map(metric => (
            <div key={metric.label} style={phase5Styles.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span>{metric.icon}</span>
                <span style={{ fontSize: '12px', color: '#6c7086' }}>{metric.label}</span>
              </div>
              <div style={{ fontSize: '20px', fontWeight: 600, color: metric.color }}>
                {metric.value}
                <span style={{ fontSize: '12px', color: '#6c7086', marginLeft: '4px' }}>
                  {metric.unit}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Mini Graph */}
        <div style={{
          ...phase5Styles.card,
          height: '100px',
          display: 'flex',
          alignItems: 'flex-end',
          gap: '2px',
          padding: '8px',
        }}>
          {history.slice(-60).map((snapshot, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                height: `${(snapshot.fps / 60) * 100}%`,
                backgroundColor: getFpsColor(snapshot.fps),
                borderRadius: '2px 2px 0 0',
                minWidth: '2px',
              }}
            />
          ))}
          {history.length === 0 && (
            <div style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#6c7086',
              fontSize: '12px',
            }}>
              Start recording to see history
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

PerformanceMonitor.displayName = 'PerformanceMonitor';

// =============================================================================
// TUTORIAL OVERLAY
// =============================================================================

interface TutorialOverlayProps {
  tutorialId?: string;
  onComplete?: (tutorialId: string) => void;
  onSkip?: () => void;
}

export const TutorialOverlay: React.FC<TutorialOverlayProps> = memo(({
  tutorialId = 'getting-started',
  onComplete,
  onSkip,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const [completedTutorials, setCompletedTutorials] = useState<Set<string>>(new Set());

  const steps: TutorialStep[] = useMemo(() => [
    {
      id: 'welcome',
      title: 'Welcome to Game Maker! 👋',
      description: 'Let\'s take a quick tour to help you get started with creating amazing games.',
      position: 'bottom',
    },
    {
      id: 'hierarchy',
      title: 'Scene Hierarchy',
      description: 'This panel shows all objects in your scene. You can organize them in a tree structure.',
      target: 'scene-hierarchy',
      position: 'right',
    },
    {
      id: 'inspector',
      title: 'Inspector Panel',
      description: 'Select any object to view and edit its properties here. Transform, components, and more!',
      target: 'inspector-panel',
      position: 'left',
    },
    {
      id: 'toolbar',
      title: 'Editor Toolbar',
      description: 'Use these tools to move, rotate, and scale objects. Press Play to test your game!',
      target: 'toolbar',
      position: 'bottom',
    },
    {
      id: 'complete',
      title: 'You\'re Ready! 🎉',
      description: 'That\'s the basics! Explore the editor and start creating. You can access more tutorials from the Help menu.',
      position: 'bottom',
    },
  ], []);

  const handleNext = useCallback(() => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setCompletedTutorials(prev => new Set([...prev, tutorialId]));
      setIsVisible(false);
      onComplete?.(tutorialId);
    }
  }, [currentStep, steps.length, tutorialId, onComplete]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const handleSkip = useCallback(() => {
    setIsVisible(false);
    onSkip?.();
  }, [onSkip]);

  if (!isVisible) return null;

  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        ...phase5Styles.panel,
        maxWidth: '480px',
        width: '90%',
        maxHeight: '80vh',
      }}>
        <div style={phase5Styles.header}>
          <div style={phase5Styles.title}>
            <span>📖</span>
            <span>Tutorial</span>
          </div>
          <button onClick={handleSkip} style={phase5Styles.buttonSecondary}>
            Skip Tutorial
          </button>
        </div>

        {/* Progress Bar */}
        <div style={{ padding: '0 16px', paddingTop: '16px' }}>
          <div style={{
            height: '4px',
            backgroundColor: '#313244',
            borderRadius: '2px',
            overflow: 'hidden',
          }}>
            <div style={{
              height: '100%',
              width: `${progress}%`,
              backgroundColor: '#89b4fa',
              transition: 'width 0.3s ease',
            }} />
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '8px',
            fontSize: '11px',
            color: '#6c7086',
          }}>
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
        </div>

        <div style={phase5Styles.content}>
          {/* Step Dots */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '8px',
            marginBottom: '24px',
          }}>
            {steps.map((_, i) => (
              <div
                key={i}
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: i === currentStep ? '#89b4fa' : i < currentStep ? '#a6e3a1' : '#45475a',
                  cursor: 'pointer',
                }}
                onClick={() => setCurrentStep(i)}
              />
            ))}
          </div>

          {/* Step Content */}
          <div style={{ textAlign: 'center', padding: '16px 0' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>
              {currentStep === 0 ? '👋' : currentStep === steps.length - 1 ? '🎉' : '💡'}
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: 600,
              color: '#cdd6f4',
              marginBottom: '12px',
            }}>
              {step.title}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#a6adc8',
              lineHeight: 1.6,
            }}>
              {step.description}
            </p>
          </div>
        </div>

        {/* Footer Navigation */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          padding: '16px',
          borderTop: '1px solid #313244',
        }}>
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            style={{
              ...phase5Styles.buttonSecondary,
              opacity: currentStep === 0 ? 0.5 : 1,
            }}
          >
            ← Previous
          </button>
          <button onClick={handleNext} style={phase5Styles.button}>
            {currentStep === steps.length - 1 ? 'Get Started! →' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
});

TutorialOverlay.displayName = 'TutorialOverlay';

// =============================================================================
// COMMAND PALETTE
// =============================================================================

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onCommandExecute?: (command: Command) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = memo(({
  isOpen,
  onClose,
  onCommandExecute,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentCommands, setRecentCommands] = useState<Command[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands: Command[] = useMemo(() => [
    { id: 'new-scene', name: 'New Scene', category: 'File', shortcut: 'Ctrl+N', icon: '📄', action: () => {} },
    { id: 'open-project', name: 'Open Project', category: 'File', shortcut: 'Ctrl+O', icon: '📂', action: () => {} },
    { id: 'save', name: 'Save', category: 'File', shortcut: 'Ctrl+S', icon: '💾', action: () => {} },
    { id: 'save-as', name: 'Save As...', category: 'File', shortcut: 'Ctrl+Shift+S', icon: '💾', action: () => {} },
    { id: 'undo', name: 'Undo', category: 'Edit', shortcut: 'Ctrl+Z', icon: '↩️', action: () => {} },
    { id: 'redo', name: 'Redo', category: 'Edit', shortcut: 'Ctrl+Y', icon: '↪️', action: () => {} },
    { id: 'cut', name: 'Cut', category: 'Edit', shortcut: 'Ctrl+X', icon: '✂️', action: () => {} },
    { id: 'copy', name: 'Copy', category: 'Edit', shortcut: 'Ctrl+C', icon: '📋', action: () => {} },
    { id: 'paste', name: 'Paste', category: 'Edit', shortcut: 'Ctrl+V', icon: '📌', action: () => {} },
    { id: 'duplicate', name: 'Duplicate', category: 'Edit', shortcut: 'Ctrl+D', icon: '📑', action: () => {} },
    { id: 'select-all', name: 'Select All', category: 'Edit', shortcut: 'Ctrl+A', icon: '⬚', action: () => {} },
    { id: 'play', name: 'Play', category: 'Game', shortcut: 'Ctrl+P', icon: '▶️', action: () => {} },
    { id: 'pause', name: 'Pause', category: 'Game', shortcut: 'Ctrl+Shift+P', icon: '⏸️', action: () => {} },
    { id: 'stop', name: 'Stop', category: 'Game', shortcut: 'Ctrl+.', icon: '⏹️', action: () => {} },
    { id: 'build', name: 'Build Project', category: 'Build', shortcut: 'Ctrl+B', icon: '🔨', action: () => {} },
    { id: 'run', name: 'Build & Run', category: 'Build', shortcut: 'Ctrl+Shift+B', icon: '🚀', action: () => {} },
    { id: 'settings', name: 'Settings', category: 'Preferences', shortcut: 'Ctrl+,', icon: '⚙️', action: () => {} },
    { id: 'theme', name: 'Change Theme', category: 'Preferences', icon: '🎨', action: () => {} },
    { id: 'docs', name: 'Documentation', category: 'Help', shortcut: 'F1', icon: '📚', action: () => {} },
    { id: 'shortcuts', name: 'Keyboard Shortcuts', category: 'Help', shortcut: 'Ctrl+K', icon: '⌨️', action: () => {} },
  ], []);

  const filteredCommands = useMemo(() => {
    if (!query) {
      return recentCommands.length > 0 ? recentCommands : commands.slice(0, 10);
    }
    const lower = query.toLowerCase();
    return commands.filter(cmd =>
      cmd.name.toLowerCase().includes(lower) ||
      cmd.category.toLowerCase().includes(lower)
    );
  }, [query, commands, recentCommands]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          const cmd = filteredCommands[selectedIndex];
          setRecentCommands(prev => [cmd, ...prev.filter(c => c.id !== cmd.id)].slice(0, 5));
          onCommandExecute?.(cmd);
          cmd.action();
          onClose();
        }
        break;
      case 'Escape':
        onClose();
        break;
    }
  }, [filteredCommands, selectedIndex, onCommandExecute, onClose]);

  if (!isOpen) return null;

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = [];
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, Command[]>);

  let flatIndex = 0;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '15vh',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          ...phase5Styles.panel,
          width: '560px',
          maxHeight: '60vh',
        }}
        onClick={e => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        {/* Search Input */}
        <div style={{ padding: '16px', borderBottom: '1px solid #313244' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '18px' }}>⌘</span>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(0);
              }}
              placeholder="Type a command or search..."
              style={{
                ...phase5Styles.input,
                border: 'none',
                backgroundColor: 'transparent',
                padding: 0,
                fontSize: '16px',
              }}
            />
            <span style={{
              ...phase5Styles.badge,
              fontSize: '10px',
            }}>
              ESC
            </span>
          </div>
        </div>

        {/* Commands List */}
        <div style={{ ...phase5Styles.content, padding: '8px' }}>
          {!query && recentCommands.length > 0 && (
            <div style={{ marginBottom: '8px' }}>
              <div style={{
                fontSize: '11px',
                color: '#6c7086',
                textTransform: 'uppercase',
                padding: '8px 12px',
                letterSpacing: '0.5px',
              }}>
                Recent
              </div>
            </div>
          )}

          {Object.entries(groupedCommands).map(([category, cmds]) => (
            <div key={category}>
              {query && (
                <div style={{
                  fontSize: '11px',
                  color: '#6c7086',
                  textTransform: 'uppercase',
                  padding: '8px 12px',
                  letterSpacing: '0.5px',
                }}>
                  {category}
                </div>
              )}
              {cmds.map((cmd) => {
                const isSelected = flatIndex === selectedIndex;
                const currentIndex = flatIndex;
                flatIndex++;

                return (
                  <div
                    key={cmd.id}
                    onClick={() => {
                      setRecentCommands(prev => [cmd, ...prev.filter(c => c.id !== cmd.id)].slice(0, 5));
                      onCommandExecute?.(cmd);
                      cmd.action();
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(currentIndex)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      backgroundColor: isSelected ? '#313244' : 'transparent',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '16px' }}>{cmd.icon}</span>
                      <span style={{ fontSize: '14px', color: '#cdd6f4' }}>{cmd.name}</span>
                    </div>
                    {cmd.shortcut && (
                      <span style={{
                        ...phase5Styles.badge,
                        fontFamily: 'monospace',
                      }}>
                        {cmd.shortcut}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          {filteredCommands.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '32px',
              color: '#6c7086',
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔍</div>
              <div>No commands found</div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          padding: '12px',
          borderTop: '1px solid #313244',
          fontSize: '11px',
          color: '#6c7086',
        }}>
          <span>↑↓ Navigate</span>
          <span>↵ Select</span>
          <span>ESC Close</span>
        </div>
      </div>
    </div>
  );
});

CommandPalette.displayName = 'CommandPalette';

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  AIAssistantPanel,
  PerformanceMonitor,
  TutorialOverlay,
  CommandPalette,
};
