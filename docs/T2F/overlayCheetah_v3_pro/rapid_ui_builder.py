#!/usr/bin/env python3
"""
Rapid UI Builder for Game Maker using Cheetah v3 PRO
===================================================
Ultra-fast UI component generation system for the Overlay Game Maker project.
Leverages Cheetah v3 PRO's enterprise capabilities for lightning-fast development.
"""

import asyncio
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2
from game_maker_config import (
    COMPONENT_CONFIGS,
    GLOBAL_STYLES,
    QUICK_PRESETS,
    get_base_config,
    get_component_config,
    get_preset_config,
)

# Performance monitoring
try:
    import psutil

    MONITOR_RESOURCES = True
except ImportError:
    MONITOR_RESOURCES = False


class RapidUIBuilder:
    """Enterprise-grade rapid UI component generator"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config = get_base_config()
        self.template_env = self._setup_template_environment()
        self.generated_files = []
        self.performance_stats = {
            "start_time": 0,
            "components_generated": 0,
            "files_created": 0,
            "lines_of_code": 0,
            "peak_memory_mb": 0,
            "generation_time_ms": {},
        }

    def _setup_template_environment(self) -> jinja2.Environment:
        """Initialize Jinja2 template environment with enterprise features"""
        template_dir = Path(__file__).parent / "templates"

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )

        # Add custom filters for enterprise development
        env.filters["capitalize"] = str.capitalize
        env.filters["camelcase"] = self._to_camel_case
        env.filters["kebabcase"] = self._to_kebab_case
        env.filters["indent"] = self._indent_text

        return env

    def _to_camel_case(self, text: str) -> str:
        """Convert to camelCase"""
        components = text.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    def _to_kebab_case(self, text: str) -> str:
        """Convert to kebab-case"""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()

    def _indent_text(self, text: str, indent: int = 2) -> str:
        """Indent text with specified spaces"""
        spaces = " " * indent
        return "\n".join(
            spaces + line if line.strip() else line for line in text.split("\n")
        )

    def _monitor_performance(self, component_name: str, start_time: float):
        """Monitor generation performance"""
        end_time = time.time()
        generation_time = (end_time - start_time) * 1000  # Convert to ms
        self.performance_stats["generation_time_ms"][component_name] = generation_time

        if MONITOR_RESOURCES:
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            if memory_usage > self.performance_stats["peak_memory_mb"]:
                self.performance_stats["peak_memory_mb"] = memory_usage

    async def generate_component_async(
        self, component_name: str, config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a single component asynchronously for maximum speed"""
        start_time = time.time()

        try:
            # Load template
            template = self.template_env.get_template("game_maker_ui_template.j2")

            # Generate component code
            component_code = await template.render_async(config=config)

            # Generate component file path
            component_path = self._get_component_path(component_name)

            # Generate test file if configured
            test_code = ""
            if config.get("include_tests", True):
                test_path = self._get_test_path(component_name)
                test_code = self._extract_test_code(component_code)

            # Generate styles
            styles_code = self._extract_styles_code(component_code)
            styles_path = self._get_styles_path(component_name)

            result = {
                "component_path": str(component_path),
                "component_code": component_code,
                "test_path": str(test_path)
                if config.get("include_tests", True)
                else None,
                "test_code": test_code,
                "styles_path": str(styles_path),
                "styles_code": styles_code,
                "generated_at": time.time(),
            }

            self._monitor_performance(component_name, start_time)
            return result

        except Exception as e:
            print(f"Error generating {component_name}: {e}")
            return {}

    def _get_component_path(self, component_name: str) -> Path:
        """Get the file path for a component"""
        components_dir = self.project_root / self.config["paths"]["components"]
        return components_dir / f"{component_name}.tsx"

    def _get_test_path(self, component_name: str) -> Path:
        """Get the file path for component tests"""
        tests_dir = self.project_root / self.config["paths"]["tests"] / "components"
        return tests_dir / f"{component_name}.test.tsx"

    def _get_styles_path(self, component_name: str) -> Path:
        """Get the file path for component styles"""
        styles_dir = self.project_root / self.config["paths"]["styles"] / "components"
        return styles_dir / f"{component_name}.module.css"

    def _extract_test_code(self, full_code: str) -> str:
        """Extract test code from generated component"""
        lines = full_code.split("\n")
        test_start = -1

        for i, line in enumerate(lines):
            if "// " in line and ".test." in line:
                test_start = i
                break

        if test_start >= 0:
            return "\n".join(lines[test_start + 1 :])
        return ""

    def _extract_styles_code(self, full_code: str) -> str:
        """Extract CSS code from generated component"""
        lines = full_code.split("\n")
        styles_start = -1

        for i, line in enumerate(lines):
            if "/* " in line and "Styles" in line:
                styles_start = i
                break

        if styles_start >= 0:
            return "\n".join(lines[styles_start:])
        return ""

    async def write_files_async(self, results: List[Dict[str, str]]):
        """Write all generated files asynchronously"""

        async def write_file(path: str, content: str):
            """Write a single file async"""
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.generated_files.append(str(file_path))
            self.performance_stats["files_created"] += 1
            self.performance_stats["lines_of_code"] += len(content.split("\n"))

        # Prepare all write tasks
        tasks = []
        for result in results:
            if result.get("component_code"):
                tasks.append(
                    write_file(result["component_path"], result["component_code"])
                )

            if result.get("test_code"):
                tasks.append(write_file(result["test_path"], result["test_code"]))

            if result.get("styles_code"):
                tasks.append(write_file(result["styles_path"], result["styles_code"]))

        # Execute all writes concurrently
        await asyncio.gather(*tasks)

    async def generate_preset_async(self, preset_name: str) -> Dict[str, Any]:
        """Generate a complete preset of components ultra-fast"""
        print(f"🚀 Generating {preset_name} preset with Cheetah v3 PRO...")

        self.performance_stats["start_time"] = time.time()

        # Get preset configuration
        preset_config = get_preset_config(preset_name)

        if not preset_config:
            return {"error": f"Preset '{preset_name}' not found"}

        # Generate all components concurrently
        tasks = []
        for component_name, config in preset_config.items():
            tasks.append(self.generate_component_async(component_name, config))

        # Execute all generations concurrently
        results = await asyncio.gather(*tasks)

        # Write all files concurrently
        await self.write_files_async(results)

        # Generate additional files
        await self._generate_additional_files_async()

        # Update performance stats
        self.performance_stats["components_generated"] = len(preset_config)

        total_time = time.time() - self.performance_stats["start_time"]

        return {
            "preset_name": preset_name,
            "components_generated": list(preset_config.keys()),
            "files_created": self.generated_files,
            "performance": {
                "total_time_seconds": round(total_time, 2),
                "components_per_second": round(len(preset_config) / total_time, 2),
                "files_created": self.performance_stats["files_created"],
                "lines_of_code": self.performance_stats["lines_of_code"],
                "peak_memory_mb": self.performance_stats["peak_memory_mb"],
                "individual_times": self.performance_stats["generation_time_ms"],
            },
        }

    async def _generate_additional_files_async(self):
        """Generate additional supporting files"""
        tasks = [
            self._generate_global_styles(),
            self._generate_index_file(),
            self._generate_types_file(),
            self._generate_context_file(),
            self._generate_hooks_file(),
        ]

        await asyncio.gather(*tasks)

    async def _generate_global_styles(self):
        """Generate global CSS variables and styles"""
        styles_path = self.project_root / self.config["paths"]["styles"] / "globals.css"
        styles_path.parent.mkdir(parents=True, exist_ok=True)

        with open(styles_path, "w", encoding="utf-8") as f:
            f.write(GLOBAL_STYLES)

        self.generated_files.append(str(styles_path))

    async def _generate_index_file(self):
        """Generate index file for component exports"""
        components_dir = self.project_root / self.config["paths"]["components"]
        index_path = components_dir / "index.ts"

        # Generate exports for all components
        exports = []
        for component_name in COMPONENT_CONFIGS.keys():
            exports.append(
                f"export {{ default as {component_name} }} from './{component_name}';"
            )

        index_content = "// Auto-generated component exports\n\n" + "\n".join(exports)

        components_dir.mkdir(parents=True, exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        self.generated_files.append(str(index_path))

    async def _generate_types_file(self):
        """Generate TypeScript types for Game Maker"""
        types_path = self.project_root / self.config["paths"]["types"] / "gamemaker.ts"
        types_path.parent.mkdir(parents=True, exist_ok=True)

        types_content = """// Auto-generated Game Maker types

export interface GameProject {
  id: string;
  name: string;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
  scenes: GameScene[];
  assets: GameAsset[];
}

export interface GameScene {
  id: string;
  name: string;
  objects: GameObject[];
  scripts: GameScript[];
}

export interface GameObject {
  id: string;
  name: string;
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  components: Component[];
}

export interface GameAsset {
  id: string;
  name: string;
  type: AssetType;
  url: string;
  metadata: Record<string, any>;
  tags: string[];
}

export interface GameScript {
  id: string;
  name: string;
  nodes: ScriptNode[];
  connections: NodeConnection[];
}

export interface ScriptNode {
  id: string;
  type: string;
  position: Vector2;
  properties: Record<string, any>;
  inputs: NodeInput[];
  outputs: NodeOutput[];
}

export interface NodeConnection {
  id: string;
  fromNode: string;
  fromOutput: string;
  toNode: string;
  toInput: string;
}

export interface Vector2 {
  x: number;
  y: number;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export type AssetType = 'model' | 'texture' | 'audio' | 'script' | 'material';
export type GameEngine = 'unity' | 'godot' | 'unreal';

export interface PerformanceStats {
  fps?: number;
  triangles?: number;
  drawCalls?: number;
  memoryUsage?: number;
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
  color: string;
  status: 'online' | 'away' | 'busy';
}

export interface ChatMessage {
  id: string;
  author: string;
  content: string;
  timestamp: Date;
  type: 'message' | 'system' | 'notification';
}
"""

        with open(types_path, "w", encoding="utf-8") as f:
            f.write(types_content)

        self.generated_files.append(str(types_path))

    async def _generate_context_file(self):
        """Generate React context for Game Maker state"""
        context_path = (
            self.project_root / self.config["paths"]["context"] / "GameMakerContext.tsx"
        )
        context_path.parent.mkdir(parents=True, exist_ok=True)

        context_content = """// Auto-generated Game Maker Context
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { GameProject, GameScene, GameObject, GameEngine } from '../types/gamemaker';

interface GameMakerState {
  currentProject: GameProject | null;
  currentScene: GameScene | null;
  selectedObjects: GameObject[];
  currentEngine: GameEngine;
  isConnected: boolean;
  isPlaying: boolean;
}

interface GameMakerActions {
  loadProject: (project: GameProject) => void;
  updateScene: (scene: GameScene) => void;
  selectObjects: (objects: GameObject[]) => void;
  setEngine: (engine: GameEngine) => void;
  setConnected: (connected: boolean) => void;
  setPlaying: (playing: boolean) => void;
}

type GameMakerContextType = GameMakerState & GameMakerActions;

const GameMakerContext = createContext<GameMakerContextType | null>(null);

export const useGameMakerContext = (): GameMakerContextType => {
  const context = useContext(GameMakerContext);
  if (!context) {
    throw new Error('useGameMakerContext must be used within a GameMakerProvider');
  }
  return context;
};

interface GameMakerProviderProps {
  children: ReactNode;
}

export const GameMakerProvider: React.FC<GameMakerProviderProps> = ({ children }) => {
  const [state, setState] = React.useState<GameMakerState>({
    currentProject: null,
    currentScene: null,
    selectedObjects: [],
    currentEngine: 'unity',
    isConnected: false,
    isPlaying: false,
  });

  const actions: GameMakerActions = {
    loadProject: (project) => setState(prev => ({ ...prev, currentProject: project })),
    updateScene: (scene) => setState(prev => ({ ...prev, currentScene: scene })),
    selectObjects: (objects) => setState(prev => ({ ...prev, selectedObjects: objects })),
    setEngine: (engine) => setState(prev => ({ ...prev, currentEngine: engine })),
    setConnected: (connected) => setState(prev => ({ ...prev, isConnected: connected })),
    setPlaying: (playing) => setState(prev => ({ ...prev, isPlaying: playing })),
  };

  const value = { ...state, ...actions };

  return (
    <GameMakerContext.Provider value={value}>
      {children}
    </GameMakerContext.Provider>
  );
};
"""

        with open(context_path, "w", encoding="utf-8") as f:
            f.write(context_content)

        self.generated_files.append(str(context_path))

    async def _generate_hooks_file(self):
        """Generate custom React hooks"""
        hooks_path = (
            self.project_root / self.config["paths"]["hooks"] / "useEngineConnector.ts"
        )
        hooks_path.parent.mkdir(parents=True, exist_ok=True)

        hooks_content = """// Auto-generated Engine Connector Hook
import { useState, useEffect, useCallback } from 'react';
import { GameEngine } from '../types/gamemaker';
import { EngineConnector } from '../engine/EngineConnector';

export interface UseEngineConnectorReturn {
  engineConnector: EngineConnector | null;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  connect: () => Promise<boolean>;
  disconnect: () => void;
  sendCommand: (command: string, data: any) => Promise<any>;
}

export const useEngineConnector = (engine: GameEngine): UseEngineConnectorReturn => {
  const [connector, setConnector] = useState<EngineConnector | null>(null);
  const [status, setStatus] = useState<UseEngineConnectorReturn['connectionStatus']>('disconnected');

  const connect = useCallback(async (): Promise<boolean> => {
    if (connector) {
      setStatus('connecting');
      try {
        const success = await connector.connect();
        setStatus(success ? 'connected' : 'error');
        return success;
      } catch (error) {
        setStatus('error');
        return false;
      }
    }
    return false;
  }, [connector]);

  const disconnect = useCallback((): void => {
    if (connector) {
      connector.disconnect();
      setStatus('disconnected');
    }
  }, [connector]);

  const sendCommand = useCallback(async (command: string, data: any): Promise<any> => {
    if (!connector || status !== 'connected') {
      throw new Error('Engine not connected');
    }
    return await connector.sendCommand(command, data);
  }, [connector, status]);

  useEffect(() => {
    const newConnector = new EngineConnector(engine);
    setConnector(newConnector);
    setStatus('disconnected');

    return () => {
      newConnector.disconnect();
    };
  }, [engine]);

  return {
    engineConnector: connector,
    connectionStatus: status,
    connect,
    disconnect,
    sendCommand,
  };
};
"""

        with open(hooks_path, "w", encoding="utf-8") as f:
            f.write(hooks_content)

        self.generated_files.append(str(hooks_path))


# CLI Interface for rapid generation
async def main():
    """Main CLI interface for rapid UI generation"""
    print("🐆 Cheetah v3 PRO - Rapid UI Builder")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python rapid_ui_builder.py <preset_name>")
        print("  python rapid_ui_builder.py --list")
        print("\nAvailable presets:")
        for preset in QUICK_PRESETS.keys():
            print(f"  - {preset}")
        return

    if sys.argv[1] == "--list":
        print("Available presets:")
        for preset, components in QUICK_PRESETS.items():
            print(f"  {preset}: {', '.join(components)}")
        return

    preset_name = sys.argv[1]
    project_root = Path(__file__).parent.parent  # Go up to project root

    # Initialize builder
    builder = RapidUIBuilder(str(project_root))

    # Generate preset
    result = await builder.generate_preset_async(preset_name)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    # Display results
    print(f"\n✅ Successfully generated {preset_name} preset!")
    print(
        f"⚡ Generated {result['performance']['components_per_second']:.1f} components/second"
    )
    print(f"📁 Created {result['performance']['files_created']} files")
    print(f"📝 Generated {result['performance']['lines_of_code']:,} lines of code")
    print(f"⏱️  Total time: {result['performance']['total_time_seconds']}s")

    if MONITOR_RESOURCES:
        print(f"💾 Peak memory: {result['performance']['peak_memory_mb']:.1f} MB")

    print(f"\n📦 Generated components:")
    for component in result["components_generated"]:
        gen_time = result["performance"]["individual_times"].get(component, 0)
        print(f"  - {component} ({gen_time:.1f}ms)")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
