#!/usr/bin/env python3
"""
Marathon Runner for Cheetah v3 PRO
==================================
Orchestrates phased component generation with visible milestones.
Builds the complete Game Maker UI system incrementally.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from marathon_config import (
    ALL_MARATHON_COMPONENTS,
    MARATHON_PHASES,
    get_phase_components,
    get_phase_info,
    get_total_component_count,
    print_marathon_summary,
)


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class MarathonRunner:
    """Orchestrates the marathon build process"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.components_dir = self.project_root / "src" / "ui" / "components"
        self.types_dir = self.project_root / "src" / "types"
        self.generated_components: List[str] = []
        self.phase_results: Dict[int, Dict[str, Any]] = {}
        self.start_time: float = 0
        self.total_lines: int = 0

    def print_banner(self):
        """Print the marathon banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐆 CHEETAH V3 PRO - MARATHON RUN                            ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                     ║
║   Building the Complete Game Maker UI System                   ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
        print(banner)

    def print_phase_header(self, phase: int):
        """Print phase header"""
        info = get_phase_info(phase)
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'═' * 60}{Colors.ENDC}")
        print(
            f"{Colors.BOLD}{Colors.YELLOW}📍 PHASE {phase}: {info['name'].upper()}{Colors.ENDC}"
        )
        print(f"{Colors.CYAN}   Milestone: {info['milestone']}{Colors.ENDC}")
        print(f"{Colors.CYAN}   {info['description']}{Colors.ENDC}")
        print(f"{Colors.YELLOW}{'═' * 60}{Colors.ENDC}\n")

    def print_milestone_complete(
        self, phase: int, components_built: int, time_taken: float
    ):
        """Print milestone completion"""
        info = get_phase_info(phase)
        print(f"\n{Colors.GREEN}{'━' * 60}{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ MILESTONE COMPLETE: {info['milestone']}{Colors.ENDC}")
        print(f"{Colors.GREEN}   Components built: {components_built}{Colors.ENDC}")
        print(f"{Colors.GREEN}   Time taken: {time_taken:.2f}s{Colors.ENDC}")
        print(f"{Colors.GREEN}{'━' * 60}{Colors.ENDC}\n")

    def print_progress_bar(self, current: int, total: int, width: int = 40):
        """Print a progress bar"""
        percent = current / total if total > 0 else 0
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        print(
            f"\r{Colors.CYAN}Progress: [{bar}] {current}/{total} ({percent * 100:.1f}%){Colors.ENDC}",
            end="",
        )

    def generate_component_code(self, name: str, config: Dict[str, Any]) -> str:
        """Generate React TypeScript component code"""
        props = config.get("props", [])
        state_vars = config.get("state_vars", [])
        features = config.get("features", [])
        icon = config.get("icon", "📦")
        description = config.get("description", "")

        # Generate props interface
        props_interface = self._generate_props_interface(name, props)

        # Generate state interface
        state_interface = self._generate_state_interface(name, state_vars)

        # Generate component
        component_code = self._generate_component_body(
            name, config, props, state_vars, features, icon, description
        )

        return f"""import React, {{ useState, useCallback, useEffect, useMemo }} from "react";

{props_interface}

{state_interface}

{component_code}

export default {name};
"""

    def _generate_props_interface(self, name: str, props: List[Dict]) -> str:
        """Generate TypeScript props interface"""
        if not props:
            return f"interface {name}Props {{}}"

        lines = [f"interface {name}Props {{"]
        for prop in props:
            required = "" if prop.get("required", False) else "?"
            lines.append(f"  {prop['name']}{required}: {prop['type']};")
        lines.append("}")
        return "\n".join(lines)

    def _generate_state_interface(self, name: str, state_vars: List[Dict]) -> str:
        """Generate state type comments (using useState hooks)"""
        if not state_vars:
            return "// No additional state types needed"
        return f"// State managed via useState hooks for {name}"

    def _generate_component_body(
        self,
        name: str,
        config: Dict,
        props: List[Dict],
        state_vars: List[Dict],
        features: List[str],
        icon: str,
        description: str,
    ) -> str:
        """Generate the full component body"""

        # Generate useState declarations
        state_declarations = []
        for sv in state_vars:
            state_name = sv["name"]
            state_type = sv["type"]
            initial = sv.get("initial", "null")
            # Handle special initializations
            if "Set<" in state_type:
                state_declarations.append(
                    f"  const [{state_name}, set{state_name[0].upper()}{state_name[1:]}] = useState<{state_type}>({initial});"
                )
            else:
                state_declarations.append(
                    f"  const [{state_name}, set{state_name[0].upper()}{state_name[1:]}] = useState<{state_type}>({initial});"
                )

        state_code = (
            "\n".join(state_declarations)
            if state_declarations
            else "  // No state needed"
        )

        # Generate props destructuring
        props_destructure = ", ".join([p["name"] for p in props]) if props else ""
        props_line = (
            f"  const {{ {props_destructure} }} = props;" if props_destructure else ""
        )

        # Generate feature sections
        feature_sections = self._generate_feature_sections(name, features, icon)

        # Generate styles
        styles_code = self._generate_styles(name, features)

        return f'''const {name}: React.FC<{name}Props> = (props) => {{
{props_line}

  // State
{state_code}

  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize component
  useEffect(() => {{
    // Component initialization logic
    console.log("{name} mounted");
    return () => {{
      console.log("{name} unmounted");
    }};
  }}, []);

{styles_code}

  if (isLoading) {{
    return (
      <div style={{{name.lower()}Styles.container}}>
        <div style={{{name.lower()}Styles.loadingState}}>
          <div style={{{name.lower()}Styles.spinner}}>⏳</div>
          <span>Loading...</span>
        </div>
      </div>
    );
  }}

  if (error) {{
    return (
      <div style={{{name.lower()}Styles.container}}>
        <div style={{{name.lower()}Styles.errorState}}>
          <span style={{{name.lower()}Styles.errorIcon}}>⚠️</span>
          <span>{{error}}</span>
          <button
            style={{{name.lower()}Styles.retryBtn}}
            onClick={{() => setError(null)}}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }}

  return (
    <div style={{{name.lower()}Styles.container}}>
      {{/* Header */}}
      <div style={{{name.lower()}Styles.header}}>
        <div style={{{name.lower()}Styles.titleSection}}>
          <span style={{{name.lower()}Styles.icon}}>{icon}</span>
          <h3 style={{{name.lower()}Styles.title}}>{{name}}.replace(/([A-Z])/g, ' $1').trim()</h3>
        </div>
        <div style={{{name.lower()}Styles.headerActions}}>
          <button style={{{name.lower()}Styles.actionBtn}} title="Refresh">🔄</button>
          <button style={{{name.lower()}Styles.actionBtn}} title="Settings">⚙️</button>
        </div>
      </div>

      {{/* Content */}}
      <div style={{{name.lower()}Styles.content}}>
{feature_sections}
      </div>

      {{/* Footer */}}
      <div style={{{name.lower()}Styles.footer}}>
        <span style={{{name.lower()}Styles.footerText}}>{description}</span>
      </div>
    </div>
  );
}};'''

    def _generate_feature_sections(
        self, name: str, features: List[str], icon: str
    ) -> str:
        """Generate UI sections based on features"""
        sections = []

        # Map features to UI sections
        feature_ui = {
            "tree_view": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>📁 Hierarchy</span>
          </div>
          <div style={{{name}Styles.treeView}}>
            <div style={{{name}Styles.treeItem}}>
              <span style={{{name}Styles.expandIcon}}>▶</span>
              <span>Root Object</span>
            </div>
            <div style={{...{name}Styles.treeItem, paddingLeft: '24px'}}>
              <span style={{{name}Styles.expandIcon}}>▶</span>
              <span>Child Object 1</span>
            </div>
            <div style={{...{name}Styles.treeItem, paddingLeft: '24px'}}>
              <span style={{{name}Styles.expandIcon}}>▶</span>
              <span>Child Object 2</span>
            </div>
          </div>
        </div>""",
            "property_grid": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>📝 Properties</span>
          </div>
          <div style={{{name}Styles.propertyGrid}}>
            <div style={{{name}Styles.propertyRow}}>
              <span style={{{name}Styles.propertyLabel}}>Name</span>
              <input style={{{name}Styles.propertyInput}} type="text" defaultValue="Object" />
            </div>
            <div style={{{name}Styles.propertyRow}}>
              <span style={{{name}Styles.propertyLabel}}>Active</span>
              <input style={{{name}Styles.checkbox}} type="checkbox" defaultChecked />
            </div>
          </div>
        </div>""",
            "vector_inputs": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>📐 Transform</span>
          </div>
          <div style={{{name}Styles.vectorGroup}}>
            <span style={{{name}Styles.vectorLabel}}>Position</span>
            <div style={{{name}Styles.vectorInputs}}>
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="X" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="Y" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="Z" />
            </div>
          </div>
          <div style={{{name}Styles.vectorGroup}}>
            <span style={{{name}Styles.vectorLabel}}>Rotation</span>
            <div style={{{name}Styles.vectorInputs}}>
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="X" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="Y" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="Z" />
            </div>
          </div>
          <div style={{{name}Styles.vectorGroup}}>
            <span style={{{name}Styles.vectorLabel}}>Scale</span>
            <div style={{{name}Styles.vectorInputs}}>
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="1" placeholder="X" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="1" placeholder="Y" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="1" placeholder="Z" />
            </div>
          </div>
        </div>""",
            "log_levels": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.toolbar}}>
            <button style={{{name}Styles.filterBtn}}>All</button>
            <button style={{{name}Styles.filterBtn}}>ℹ️ Log</button>
            <button style={{{name}Styles.filterBtn}}>⚠️ Warn</button>
            <button style={{{name}Styles.filterBtn}}>❌ Error</button>
            <button style={{{name}Styles.clearBtn}}>Clear</button>
          </div>
          <div style={{{name}Styles.logList}}>
            <div style={{{name}Styles.logEntry}}>
              <span style={{{name}Styles.logTime}}>[12:00:00]</span>
              <span style={{{name}Styles.logIcon}}>ℹ️</span>
              <span>Application started</span>
            </div>
            <div style={{{name}Styles.logEntry}}>
              <span style={{{name}Styles.logTime}}>[12:00:01]</span>
              <span style={{{name}Styles.logIcon}}>⚠️</span>
              <span style={{color: '#d97706'}}>Performance warning: High draw calls</span>
            </div>
            <div style={{{name}Styles.logEntry}}>
              <span style={{{name}Styles.logTime}}>[12:00:02]</span>
              <span style={{{name}Styles.logIcon}}>ℹ️</span>
              <span>Scene loaded successfully</span>
            </div>
          </div>
        </div>""",
            "tool_selection": """        <div style={{{name}Styles.toolbarSection}}>
          <div style={{{name}Styles.toolGroup}}>
            <button style={{{name}Styles.toolBtn}} title="Select">🔲</button>
            <button style={{{name}Styles.toolBtn}} title="Move">✥</button>
            <button style={{{name}Styles.toolBtn}} title="Rotate">🔄</button>
            <button style={{{name}Styles.toolBtn}} title="Scale">⤢</button>
          </div>
          <div style={{{name}Styles.divider}} />
          <div style={{{name}Styles.toolGroup}}>
            <button style={{{name}Styles.toolBtn}} title="Play">▶️</button>
            <button style={{{name}Styles.toolBtn}} title="Pause">⏸️</button>
            <button style={{{name}Styles.toolBtn}} title="Stop">⏹️</button>
          </div>
        </div>""",
            "keyframes": """        <div style={{{name}Styles.timeline}}>
          <div style={{{name}Styles.timelineHeader}}>
            <div style={{{name}Styles.trackLabels}}>
              <div style={{{name}Styles.trackLabel}}>Position</div>
              <div style={{{name}Styles.trackLabel}}>Rotation</div>
              <div style={{{name}Styles.trackLabel}}>Scale</div>
            </div>
            <div style={{{name}Styles.timeRuler}}>
              {Array.from({{length: 10}}).map((_, i) => (
                <span key={{i}} style={{{name}Styles.timeMarker}}>{{i}}s</span>
              ))}
            </div>
          </div>
          <div style={{{name}Styles.tracks}}>
            <div style={{{name}Styles.track}}>
              <div style={{...{name}Styles.keyframe, left: '10%'}} />
              <div style={{...{name}Styles.keyframe, left: '50%'}} />
              <div style={{...{name}Styles.keyframe, left: '90%'}} />
            </div>
            <div style={{{name}Styles.track}}>
              <div style={{...{name}Styles.keyframe, left: '0%'}} />
              <div style={{...{name}Styles.keyframe, left: '100%'}} />
            </div>
            <div style={{{name}Styles.track}}>
              <div style={{...{name}Styles.keyframe, left: '30%'}} />
              <div style={{...{name}Styles.keyframe, left: '70%'}} />
            </div>
          </div>
          <div style={{{name}Styles.playhead}} />
        </div>""",
            "texture_slots": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>🖼️ Textures</span>
          </div>
          <div style={{{name}Styles.textureGrid}}>
            <div style={{{name}Styles.textureSlot}}>
              <div style={{{name}Styles.texturePreview}}>🎨</div>
              <span>Albedo</span>
            </div>
            <div style={{{name}Styles.textureSlot}}>
              <div style={{{name}Styles.texturePreview}}>📐</div>
              <span>Normal</span>
            </div>
            <div style={{{name}Styles.textureSlot}}>
              <div style={{{name}Styles.texturePreview}}>✨</div>
              <span>Metallic</span>
            </div>
            <div style={{{name}Styles.textureSlot}}>
              <div style={{{name}Styles.texturePreview}}>💡</div>
              <span>Emission</span>
            </div>
          </div>
        </div>""",
            "color_picker": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>🎨 Colors</span>
          </div>
          <div style={{{name}Styles.colorRow}}>
            <span>Base Color</span>
            <input type="color" defaultValue="#3b82f6" style={{{name}Styles.colorPicker}} />
          </div>
          <div style={{{name}Styles.colorRow}}>
            <span>Emission</span>
            <input type="color" defaultValue="#000000" style={{{name}Styles.colorPicker}} />
          </div>
        </div>""",
            "modules": """        <div style={{{name}Styles.moduleList}}>
          <div style={{{name}Styles.module}}>
            <div style={{{name}Styles.moduleHeader}}>
              <span>💨 Emission</span>
              <input type="checkbox" defaultChecked />
            </div>
            <div style={{{name}Styles.moduleContent}}>
              <div style={{{name}Styles.sliderRow}}>
                <span>Rate</span>
                <input type="range" min="0" max="100" defaultValue="50" />
                <span>50</span>
              </div>
            </div>
          </div>
          <div style={{{name}Styles.module}}>
            <div style={{{name}Styles.moduleHeader}}>
              <span>📐 Shape</span>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
          <div style={{{name}Styles.module}}>
            <div style={{{name}Styles.moduleHeader}}>
              <span>⏱️ Lifetime</span>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
        </div>""",
            "mixer_channels": """        <div style={{{name}Styles.mixer}}>
          <div style={{{name}Styles.channel}}>
            <div style={{{name}Styles.channelName}}>Master</div>
            <div style={{{name}Styles.fader}}>
              <input type="range" min="0" max="100" defaultValue="80"
                style={{...{name}Styles.faderSlider, writingMode: 'bt-lr'}} />
            </div>
            <div style={{{name}Styles.channelControls}}>
              <button style={{{name}Styles.muteBtn}}>M</button>
              <button style={{{name}Styles.soloBtn}}>S</button>
            </div>
            <div style={{{name}Styles.meter}} />
          </div>
          <div style={{{name}Styles.channel}}>
            <div style={{{name}Styles.channelName}}>Music</div>
            <div style={{{name}Styles.fader}}>
              <input type="range" min="0" max="100" defaultValue="70"
                style={{...{name}Styles.faderSlider}} />
            </div>
            <div style={{{name}Styles.channelControls}}>
              <button style={{{name}Styles.muteBtn}}>M</button>
              <button style={{{name}Styles.soloBtn}}>S</button>
            </div>
          </div>
          <div style={{{name}Styles.channel}}>
            <div style={{{name}Styles.channelName}}>SFX</div>
            <div style={{{name}Styles.fader}}>
              <input type="range" min="0" max="100" defaultValue="90"
                style={{...{name}Styles.faderSlider}} />
            </div>
            <div style={{{name}Styles.channelControls}}>
              <button style={{{name}Styles.muteBtn}}>M</button>
              <button style={{{name}Styles.soloBtn}}>S</button>
            </div>
          </div>
        </div>""",
            "prefab_library": """        <div style={{{name}Styles.library}}>
          <div style={{{name}Styles.searchBar}}>
            <input type="text" placeholder="Search prefabs..." style={{{name}Styles.searchInput}} />
          </div>
          <div style={{{name}Styles.prefabGrid}}>
            <div style={{{name}Styles.prefabCard}}>
              <div style={{{name}Styles.prefabPreview}}>🧊</div>
              <span>Cube</span>
            </div>
            <div style={{{name}Styles.prefabCard}}>
              <div style={{{name}Styles.prefabPreview}}>⚽</div>
              <span>Sphere</span>
            </div>
            <div style={{{name}Styles.prefabCard}}>
              <div style={{{name}Styles.prefabPreview}}>🎭</div>
              <span>Character</span>
            </div>
            <div style={{{name}Styles.prefabCard}}>
              <div style={{{name}Styles.prefabPreview}}>🌳</div>
              <span>Tree</span>
            </div>
          </div>
        </div>""",
            "light_list": """        <div style={{{name}Styles.lightList}}>
          <div style={{{name}Styles.lightItem}}>
            <span style={{{name}Styles.lightIcon}}>☀️</span>
            <span>Directional Light</span>
            <input type="color" defaultValue="#fffbeb" style={{{name}Styles.lightColor}} />
          </div>
          <div style={{{name}Styles.lightItem}}>
            <span style={{{name}Styles.lightIcon}}>💡</span>
            <span>Point Light 1</span>
            <input type="color" defaultValue="#3b82f6" style={{{name}Styles.lightColor}} />
          </div>
          <div style={{{name}Styles.lightItem}}>
            <span style={{{name}Styles.lightIcon}}>🔦</span>
            <span>Spot Light</span>
            <input type="color" defaultValue="#ffffff" style={{{name}Styles.lightColor}} />
          </div>
          <button style={{{name}Styles.addLightBtn}}>+ Add Light</button>
        </div>""",
            "gravity": """        <div style={{{name}Styles.section}}>
          <div style={{{name}Styles.sectionHeader}}>
            <span>🌍 World Physics</span>
          </div>
          <div style={{{name}Styles.vectorGroup}}>
            <span style={{{name}Styles.vectorLabel}}>Gravity</span>
            <div style={{{name}Styles.vectorInputs}}>
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="X" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="-9.81" placeholder="Y" />
              <input style={{{name}Styles.vectorInput}} type="number" defaultValue="0" placeholder="Z" />
            </div>
          </div>
          <div style={{{name}Styles.sliderRow}}>
            <span>Time Scale</span>
            <input type="range" min="0" max="200" defaultValue="100" />
            <span>1.0x</span>
          </div>
        </div>""",
            "action_map": """        <div style={{{name}Styles.actionList}}>
          <div style={{{name}Styles.actionItem}}>
            <span style={{{name}Styles.actionName}}>Jump</span>
            <span style={{{name}Styles.binding}}>Space</span>
            <button style={{{name}Styles.rebindBtn}}>🔄</button>
          </div>
          <div style={{{name}Styles.actionItem}}>
            <span style={{{name}Styles.actionName}}>Move</span>
            <span style={{{name}Styles.binding}}>WASD</span>
            <button style={{{name}Styles.rebindBtn}}>🔄</button>
          </div>
          <div style={{{name}Styles.actionItem}}>
            <span style={{{name}Styles.actionName}}>Attack</span>
            <span style={{{name}Styles.binding}}>Left Click</span>
            <button style={{{name}Styles.rebindBtn}}>🔄</button>
          </div>
          <button style={{{name}Styles.addActionBtn}}>+ Add Action</button>
        </div>""",
            "platform_select": """        <div style={{{name}Styles.platformGrid}}>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>🪟</span>
            <span>Windows</span>
          </div>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>🍎</span>
            <span>macOS</span>
          </div>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>🐧</span>
            <span>Linux</span>
          </div>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>🌐</span>
            <span>WebGL</span>
          </div>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>📱</span>
            <span>Android</span>
          </div>
          <div style={{{name}Styles.platformCard}}>
            <span style={{{name}Styles.platformIcon}}>📱</span>
            <span>iOS</span>
          </div>
        </div>""",
            "changes": """        <div style={{{name}Styles.changesList}}>
          <div style={{{name}Styles.changeItem}}>
            <input type="checkbox" style={{{name}Styles.changeCheckbox}} />
            <span style={{{name}Styles.changeStatus}}>M</span>
            <span style={{{name}Styles.changePath}}>src/scenes/MainScene.ts</span>
          </div>
          <div style={{{name}Styles.changeItem}}>
            <input type="checkbox" style={{{name}Styles.changeCheckbox}} />
            <span style={{...{name}Styles.changeStatus, color: '#16a34a'}}>A</span>
            <span style={{{name}Styles.changePath}}>src/prefabs/Player.ts</span>
          </div>
          <div style={{{name}Styles.changeItem}}>
            <input type="checkbox" style={{{name}Styles.changeCheckbox}} />
            <span style={{...{name}Styles.changeStatus, color: '#dc2626'}}>D</span>
            <span style={{{name}Styles.changePath}}>src/old/unused.ts</span>
          </div>
        </div>
        <div style={{{name}Styles.commitSection}}>
          <input type="text" placeholder="Commit message..." style={{{name}Styles.commitInput}} />
          <button style={{{name}Styles.commitBtn}}>Commit</button>
        </div>""",
            "browse": """        <div style={{{name}Styles.pluginGrid}}>
          <div style={{{name}Styles.pluginCard}}>
            <div style={{{name}Styles.pluginIcon}}>🎮</div>
            <div style={{{name}Styles.pluginInfo}}>
              <span style={{{name}Styles.pluginName}}>Input System Pro</span>
              <span style={{{name}Styles.pluginDesc}}>Advanced input handling</span>
            </div>
            <button style={{{name}Styles.installBtn}}>Install</button>
          </div>
          <div style={{{name}Styles.pluginCard}}>
            <div style={{{name}Styles.pluginIcon}}>🎨</div>
            <div style={{{name}Styles.pluginInfo}}>
              <span style={{{name}Styles.pluginName}}>Shader Graph</span>
              <span style={{{name}Styles.pluginDesc}}>Visual shader editor</span>
            </div>
            <button style={{{name}Styles.installBtn}}>Installed ✓</button>
          </div>
        </div>""",
            "string_table": """        <div style={{{name}Styles.localeSelector}}>
          <select style={{{name}Styles.localeSelect}}>
            <option value="en">🇺🇸 English</option>
            <option value="es">🇪🇸 Spanish</option>
            <option value="fr">🇫🇷 French</option>
            <option value="de">🇩🇪 German</option>
            <option value="ja">🇯🇵 Japanese</option>
          </select>
        </div>
        <div style={{{name}Styles.stringTable}}>
          <div style={{{name}Styles.stringRow}}>
            <span style={{{name}Styles.stringKey}}>menu.start</span>
            <input style={{{name}Styles.stringValue}} type="text" defaultValue="Start Game" />
          </div>
          <div style={{{name}Styles.stringRow}}>
            <span style={{{name}Styles.stringKey}}>menu.options</span>
            <input style={{{name}Styles.stringValue}} type="text" defaultValue="Options" />
          </div>
          <div style={{{name}Styles.stringRow}}>
            <span style={{{name}Styles.stringKey}}>menu.quit</span>
            <input style={{{name}Styles.stringValue}} type="text" defaultValue="Quit" />
          </div>
        </div>""",
            "chat": """        <div style={{{name}Styles.chatContainer}}>
          <div style={{{name}Styles.messages}}>
            <div style={{{name}Styles.assistantMessage}}>
              <span style={{{name}Styles.messageIcon}}>🤖</span>
              <div style={{{name}Styles.messageContent}}>
                Hello! I'm your AI assistant. I can help you generate code, create assets, and design game mechanics. What would you like to create today?
              </div>
            </div>
          </div>
          <div style={{{name}Styles.inputArea}}>
            <input
              type="text"
              placeholder="Ask me to generate something..."
              style={{{name}Styles.chatInput}}
            />
            <button style={{{name}Styles.sendBtn}}>Send</button>
          </div>
        </div>""",
            "fps_graph": """        <div style={{{name}Styles.metricsGrid}}>
          <div style={{{name}Styles.metricCard}}>
            <div style={{{name}Styles.metricValue}}>60</div>
            <div style={{{name}Styles.metricLabel}}>FPS</div>
            <div style={{{name}Styles.miniGraph}}>
              <svg viewBox="0 0 100 30" style={{width: '100%', height: '30px'}}>
                <polyline points="0,15 20,10 40,12 60,8 80,15 100,10"
                  fill="none" stroke="#16a34a" strokeWidth="2" />
              </svg>
            </div>
          </div>
          <div style={{{name}Styles.metricCard}}>
            <div style={{{name}Styles.metricValue}}>16.7</div>
            <div style={{{name}Styles.metricLabel}}>Frame Time (ms)</div>
          </div>
          <div style={{{name}Styles.metricCard}}>
            <div style={{{name}Styles.metricValue}}>256</div>
            <div style={{{name}Styles.metricLabel}}>Memory (MB)</div>
          </div>
          <div style={{{name}Styles.metricCard}}>
            <div style={{{name}Styles.metricValue}}>150</div>
            <div style={{{name}Styles.metricLabel}}>Draw Calls</div>
          </div>
        </div>""",
            "steps": """        <div style={{{name}Styles.tutorialContent}}>
          <div style={{{name}Styles.stepIndicator}}>
            <div style={{...{name}Styles.stepDot, background: '#16a34a'}} />
            <div style={{...{name}Styles.stepDot, background: '#3b82f6'}} />
            <div style={{{name}Styles.stepDot}} />
            <div style={{{name}Styles.stepDot}} />
          </div>
          <div style={{{name}Styles.stepContent}}>
            <h4 style={{{name}Styles.stepTitle}}>Step 2: Create Your First Scene</h4>
            <p style={{{name}Styles.stepDesc}}>
              Click on File → New Scene to create a new scene for your game.
              You can add objects, lights, and cameras to build your world.
            </p>
          </div>
          <div style={{{name}Styles.stepActions}}>
            <button style={{{name}Styles.prevBtn}}>← Previous</button>
            <button style={{{name}Styles.nextBtn}}>Next →</button>
            <button style={{{name}Styles.skipBtn}}>Skip Tutorial</button>
          </div>
        </div>""",
            "search": """        <div style={{{name}Styles.searchSection}}>
          <input
            type="text"
            placeholder="Search commands... (Ctrl+K)"
            style={{{name}Styles.searchInput}}
          />
        </div>
        <div style={{{name}Styles.commandList}}>
          <div style={{{name}Styles.commandItem}}>
            <span style={{{name}Styles.commandIcon}}>📄</span>
            <span style={{{name}Styles.commandName}}>New Scene</span>
            <span style={{{name}Styles.commandShortcut}}>Ctrl+N</span>
          </div>
          <div style={{{name}Styles.commandItem}}>
            <span style={{{name}Styles.commandIcon}}>💾</span>
            <span style={{{name}Styles.commandName}}>Save Project</span>
            <span style={{{name}Styles.commandShortcut}}>Ctrl+S</span>
          </div>
          <div style={{{name}Styles.commandItem}}>
            <span style={{{name}Styles.commandIcon}}>▶️</span>
            <span style={{{name}Styles.commandName}}>Play Scene</span>
            <span style={{{name}Styles.commandShortcut}}>Ctrl+P</span>
          </div>
          <div style={{{name}Styles.commandItem}}>
            <span style={{{name}Styles.commandIcon}}>🔨</span>
            <span style={{{name}Styles.commandName}}>Build Project</span>
            <span style={{{name}Styles.commandShortcut}}>Ctrl+B</span>
          </div>
        </div>""",
        }

        # Add default section if no features match
        default_section = f"""        <div style={{{name.lower()}Styles.emptyState}}>
          <span style={{{name.lower()}Styles.emptyIcon}}>{icon}</span>
          <h4>{{name}}.replace('([A-Z])', ' $1').strip()</h4>
          <p>This panel is ready to use.</p>
        </div>"""

        for feature in features[
            :3
        ]:  # Limit to 3 features to keep components manageable
            if feature in feature_ui:
                section = feature_ui[feature].replace("{name}", name.lower())
                sections.append(section)

        if not sections:
            sections.append(default_section)

        return "\n".join(sections)

    def _generate_styles(self, name: str, features: List[str]) -> str:
        """Generate inline styles object"""
        style_name = f"{name.lower()}Styles"

        return f"""  // Styles
  const {style_name} = {{
    container: {{
      display: 'flex',
      flexDirection: 'column' as const,
      height: '100%',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '8px',
      overflow: 'hidden',
    }},
    header: {{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.75rem 1rem',
      background: 'var(--header-bg, #f8fafc)',
      borderBottom: '1px solid var(--border-color, #e2e8f0)',
    }},
    titleSection: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
    }},
    icon: {{
      fontSize: '1.25rem',
    }},
    title: {{
      margin: 0,
      fontSize: '1rem',
      fontWeight: 600,
      color: 'var(--text-primary, #0f172a)',
    }},
    headerActions: {{
      display: 'flex',
      gap: '0.25rem',
    }},
    actionBtn: {{
      padding: '0.375rem 0.5rem',
      background: 'transparent',
      border: '1px solid transparent',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '0.875rem',
      transition: 'all 0.15s ease',
    }},
    content: {{
      flex: 1,
      padding: '1rem',
      overflow: 'auto',
    }},
    footer: {{
      padding: '0.5rem 1rem',
      background: 'var(--header-bg, #f8fafc)',
      borderTop: '1px solid var(--border-color, #e2e8f0)',
    }},
    footerText: {{
      fontSize: '0.75rem',
      color: 'var(--text-muted, #64748b)',
    }},
    loadingState: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '1rem',
      color: 'var(--text-secondary, #64748b)',
    }},
    spinner: {{
      fontSize: '2rem',
      animation: 'spin 1s linear infinite',
    }},
    errorState: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '0.75rem',
      color: 'var(--error-color, #dc2626)',
    }},
    errorIcon: {{
      fontSize: '2rem',
    }},
    retryBtn: {{
      padding: '0.5rem 1rem',
      background: 'var(--primary-color, #3b82f6)',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
    }},
    emptyState: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      height: '200px',
      color: 'var(--text-secondary, #64748b)',
      textAlign: 'center' as const,
    }},
    emptyIcon: {{
      fontSize: '3rem',
      marginBottom: '1rem',
    }},
    section: {{
      marginBottom: '1rem',
      padding: '0.75rem',
      background: 'var(--background-color, #f8fafc)',
      borderRadius: '6px',
      border: '1px solid var(--border-color, #e2e8f0)',
    }},
    sectionHeader: {{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '0.75rem',
      fontWeight: 600,
      fontSize: '0.875rem',
      color: 'var(--text-primary, #0f172a)',
    }},
    // Tree view styles
    treeView: {{
      fontSize: '0.875rem',
    }},
    treeItem: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.375rem 0.5rem',
      cursor: 'pointer',
      borderRadius: '4px',
      transition: 'background 0.15s ease',
    }},
    expandIcon: {{
      fontSize: '0.75rem',
      color: 'var(--text-muted, #64748b)',
    }},
    // Property grid styles
    propertyGrid: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.5rem',
    }},
    propertyRow: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
    }},
    propertyLabel: {{
      flex: '0 0 80px',
      fontSize: '0.8125rem',
      color: 'var(--text-secondary, #64748b)',
    }},
    propertyInput: {{
      flex: 1,
      padding: '0.375rem 0.5rem',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      fontSize: '0.8125rem',
    }},
    checkbox: {{
      width: '16px',
      height: '16px',
    }},
    // Vector input styles
    vectorGroup: {{
      marginBottom: '0.75rem',
    }},
    vectorLabel: {{
      display: 'block',
      marginBottom: '0.375rem',
      fontSize: '0.8125rem',
      color: 'var(--text-secondary, #64748b)',
    }},
    vectorInputs: {{
      display: 'flex',
      gap: '0.375rem',
    }},
    vectorInput: {{
      flex: 1,
      padding: '0.375rem 0.5rem',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      fontSize: '0.8125rem',
      textAlign: 'center' as const,
    }},
    // Toolbar styles
    toolbar: {{
      display: 'flex',
      gap: '0.5rem',
      marginBottom: '0.75rem',
      flexWrap: 'wrap' as const,
    }},
    filterBtn: {{
      padding: '0.375rem 0.75rem',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '0.8125rem',
    }},
    clearBtn: {{
      padding: '0.375rem 0.75rem',
      background: 'var(--error-color, #dc2626)',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '0.8125rem',
    }},
    // Log styles
    logList: {{
      maxHeight: '300px',
      overflow: 'auto',
      fontFamily: 'monospace',
      fontSize: '0.8125rem',
    }},
    logEntry: {{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.5rem',
      padding: '0.375rem 0',
      borderBottom: '1px solid var(--border-color, #e2e8f0)',
    }},
    logTime: {{
      color: 'var(--text-muted, #64748b)',
      flexShrink: 0,
    }},
    logIcon: {{
      flexShrink: 0,
    }},
    // Tool styles
    toolbarSection: {{
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
    }},
    toolGroup: {{
      display: 'flex',
      gap: '0.25rem',
    }},
    toolBtn: {{
      padding: '0.5rem',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '1rem',
    }},
    divider: {{
      width: '1px',
      height: '24px',
      background: 'var(--border-color, #e2e8f0)',
    }},
    // Timeline styles
    timeline: {{
      position: 'relative' as const,
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
    }},
    timelineHeader: {{
      display: 'flex',
      borderBottom: '1px solid var(--border-color, #e2e8f0)',
    }},
    trackLabels: {{
      width: '100px',
      flexShrink: 0,
      borderRight: '1px solid var(--border-color, #e2e8f0)',
    }},
    trackLabel: {{
      padding: '0.5rem',
      fontSize: '0.75rem',
      borderBottom: '1px solid var(--border-color, #e2e8f0)',
    }},
    timeRuler: {{
      flex: 1,
      display: 'flex',
      padding: '0.25rem',
      gap: '1rem',
      overflowX: 'auto' as const,
    }},
    timeMarker: {{
      fontSize: '0.6875rem',
      color: 'var(--text-muted, #64748b)',
    }},
    tracks: {{
      position: 'relative' as const,
    }},
    track: {{
      position: 'relative' as const,
      height: '32px',
      borderBottom: '1px solid var(--border-color, #e2e8f0)',
      marginLeft: '100px',
    }},
    keyframe: {{
      position: 'absolute' as const,
      top: '50%',
      transform: 'translate(-50%, -50%) rotate(45deg)',
      width: '8px',
      height: '8px',
      background: 'var(--primary-color, #3b82f6)',
      cursor: 'pointer',
    }},
    playhead: {{
      position: 'absolute' as const,
      top: 0,
      left: '100px',
      width: '2px',
      height: '100%',
      background: 'var(--error-color, #dc2626)',
      pointerEvents: 'none' as const,
    }},
    // Texture slots
    textureGrid: {{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
      gap: '0.75rem',
    }},
    textureSlot: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      gap: '0.25rem',
      fontSize: '0.75rem',
    }},
    texturePreview: {{
      width: '60px',
      height: '60px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--surface-color, #ffffff)',
      border: '2px dashed var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      fontSize: '1.5rem',
      cursor: 'pointer',
    }},
    // Color picker
    colorRow: {{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.375rem 0',
      fontSize: '0.875rem',
    }},
    colorPicker: {{
      width: '40px',
      height: '24px',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      cursor: 'pointer',
    }},
    // Module list
    moduleList: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.5rem',
    }},
    module: {{
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      overflow: 'hidden',
    }},
    moduleHeader: {{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.5rem 0.75rem',
      background: 'var(--header-bg, #f8fafc)',
      cursor: 'pointer',
    }},
    moduleContent: {{
      padding: '0.75rem',
    }},
    sliderRow: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      fontSize: '0.8125rem',
    }},
    // Mixer
    mixer: {{
      display: 'flex',
      gap: '1rem',
      justifyContent: 'center',
      padding: '1rem',
    }},
    channel: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      gap: '0.5rem',
      width: '60px',
    }},
    channelName: {{
      fontSize: '0.75rem',
      fontWeight: 600,
    }},
    fader: {{
      height: '120px',
      display: 'flex',
      alignItems: 'center',
    }},
    faderSlider: {{
      height: '100px',
      writingMode: 'vertical-lr' as const,
      direction: 'rtl' as const,
    }},
    channelControls: {{
      display: 'flex',
      gap: '0.25rem',
    }},
    muteBtn: {{
      width: '24px',
      height: '24px',
      fontSize: '0.6875rem',
      fontWeight: 700,
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '2px',
      cursor: 'pointer',
    }},
    soloBtn: {{
      width: '24px',
      height: '24px',
      fontSize: '0.6875rem',
      fontWeight: 700,
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '2px',
      cursor: 'pointer',
    }},
    meter: {{
      width: '8px',
      height: '60px',
      background: 'linear-gradient(to top, #16a34a, #d97706, #dc2626)',
      borderRadius: '2px',
    }},
    // Prefab library
    library: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '1rem',
    }},
    searchBar: {{
      marginBottom: '0.5rem',
    }},
    searchInput: {{
      width: '100%',
      padding: '0.5rem 0.75rem',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      fontSize: '0.875rem',
    }},
    prefabGrid: {{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
      gap: '0.75rem',
    }},
    prefabCard: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      padding: '0.75rem',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '6px',
      cursor: 'pointer',
      transition: 'all 0.15s ease',
      fontSize: '0.8125rem',
    }},
    prefabPreview: {{
      fontSize: '2rem',
      marginBottom: '0.375rem',
    }},
    // Light list
    lightList: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.5rem',
    }},
    lightItem: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.5rem',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
    }},
    lightIcon: {{
      fontSize: '1rem',
    }},
    lightColor: {{
      width: '32px',
      height: '20px',
      marginLeft: 'auto',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '2px',
    }},
    addLightBtn: {{
      padding: '0.5rem',
      background: 'var(--primary-color, #3b82f6)',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '0.875rem',
    }},
    // Action list
    actionList: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.5rem',
    }},
    actionItem: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.5rem 0.75rem',
      background: 'var(--surface-color, #ffffff)',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
    }},
    actionName: {{
      flex: 1,
      fontWeight: 500,
    }},
    binding: {{
      padding: '0.25rem 0.5rem',
      background: 'var(--header-bg, #f8fafc)',
      borderRadius: '3px',
      fontSize: '0.75rem',
      fontFamily: 'monospace',
    }},
    rebindBtn: {{
      padding: '0.25rem 0.5rem',
      background: 'transparent',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '3px',
      cursor: 'pointer',
    }},
    addActionBtn: {{
      padding: '0.5rem',
      background: 'var(--primary-color, #3b82f6)',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
    }},
    // Platform grid
    platformGrid: {{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
      gap: '0.75rem',
    }},
    platformCard: {{
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      padding: '1rem',
      background: 'var(--surface-color, #ffffff)',
      border: '2px solid var(--border-color, #e2e8f0)',
      borderRadius: '8px',
      cursor: 'pointer',
      transition: 'all 0.15s ease',
    }},
    platformIcon: {{
      fontSize: '2rem',
      marginBottom: '0.5rem',
    }},
    // Version control
    changesList: {{
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.25rem',
      marginBottom: '1rem',
    }},
    changeItem: {{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.375rem 0.5rem',
      fontSize: '0.8125rem',
      fontFamily: 'monospace',
    }},
    changeCheckbox: {{
      margin: 0,
    }},
    changeStatus: {{
      width: '16px',
      fontWeight: 700,
      color: '#d97706',
    }},
    changePath: {{
      flex: 1,
    }},
    commitSection: {{
      display: 'flex',
      gap: '0.5rem',
    }},
    commitInput: {{
      flex: 1,
      padding: '0.5rem',
      border: '1px solid var(--border-color, #e2e8f0)',
      borderRadius: '4px',
      fontSize: '0.875rem',
    }},
    commitBtn: {{
      padding: '0.5rem 1rem',
      background: 'var(--primary-color, #3b82f6)',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '0.875rem',
    }},
  }};
}};
"""

    def run(self):
        """Execute the complete marathon build process"""
        self.print_banner()

        self.start_time = time.time()

        for phase in range(1, 6):
            self.print_phase_header(phase)

            phase_start = time.time()

            components = get_phase_components(phase)
            component_count = len(components)

            for i, (name, config) in enumerate(components.items()):
                code = self.generate_component_code(name, config)

                # Write component file
                component_path = self.components_dir / f"{name}.tsx"
                self.components_dir.mkdir(parents=True, exist_ok=True)

                with open(component_path, "w", encoding="utf-8") as f:
                    f.write(code)

                self.generated_components.append(name)
                self.total_lines += len(code.split("\n"))

                self.print_progress_bar(i + 1, component_count)

            phase_time = time.time() - phase_start
            self.print_milestone_complete(phase, component_count, phase_time)

            self.phase_results[phase] = {
                "components_built": component_count,
                "time_taken": phase_time,
            }

        total_time = time.time() - self.start_time

        print(f"\n{'=' * 60}")
        print("🏆 MARATHON COMPLETE!")
        print(f"Total components built: {len(self.generated_components)}")
        print(f"Total lines of code: {self.total_lines}")
        print(f"Total time: {total_time:.2f}s")
        print(f"{'=' * 60}")

        print_marathon_summary()


if __name__ == "__main__":
    # Run marathon on the mundane-offerings project
    project_root = Path(__file__).parent.parent.parent
    runner = MarathonRunner(str(project_root))
    runner.run()
