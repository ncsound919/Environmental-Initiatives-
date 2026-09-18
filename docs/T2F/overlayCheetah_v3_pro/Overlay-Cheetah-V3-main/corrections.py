#!/usr/bin/env python3
"""
Corrections script for Game Maker Overlay build.
This script checks for common issues in the generated Godot project and applies fixes.
"""

import os
import sys
from pathlib import Path

# Assuming this script is run from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # Adjust based on location
GODOT_PLUGIN_DIR = PROJECT_ROOT / "godot-plugin"
TEMPLATES_DIR = GODOT_PLUGIN_DIR / "templates"
SCENES_DIR = GODOT_PLUGIN_DIR / "scenes"
SCRIPTS_DIR = GODOT_PLUGIN_DIR / "scripts"


def ensure_directory(path: Path):
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"Ensured directory: {path}")


def create_basic_template_scene(scene_type: str, template_path: Path):
    """Create a basic template scene if it doesn't exist."""
    if template_path.exists():
        return

    # Basic Godot scene content (simplified)
    scene_content = f"""[gd_scene load_steps=2 format=3 uid="uid://{scene_type}"]

[ext_resource type="Script" path="res://addons/game_maker_overlay/scene_template.gd" id="1"]

[node name="{scene_type}" type="Node2D"]
script = ExtResource("1")

[node name="Background" type="ColorRect" parent="."]
offset_right = 1024.0
offset_bottom = 600.0
color = Color(0.5, 0.5, 0.5, 1)

[node name="Label" type="Label" parent="."]
offset_left = 50.0
offset_top = 50.0
offset_right = 200.0
offset_bottom = 74.0
text = "{scene_type} Scene"
"""

    template_path.parent.mkdir(parents=True, exist_ok=True)
    with open(template_path, "w") as f:
        f.write(scene_content)
    print(f"Created basic template: {template_path}")


def create_basic_character_template(role: str, template_path: Path):
    """Create a basic character template."""
    if template_path.exists():
        return

    scene_content = f"""[gd_scene load_steps=3 format=3 uid="uid://{role}"]

[ext_resource type="Script" path="res://addons/game_maker_overlay/character_template.gd" id="1"]
[ext_resource type="Texture2D" uid="uid://placeholder" path="res://icon.svg" id="2"]

[node name="{role}" type="CharacterBody2D"]
script = ExtResource("1")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D")
"""

    template_path.parent.mkdir(parents=True, exist_ok=True)
    with open(template_path, "w") as f:
        f.write(scene_content)
    print(f"Created basic character template: {template_path}")


def check_and_create_templates():
    """Check and create necessary templates."""
    ensure_directory(TEMPLATES_DIR)

    # Scene templates
    scene_templates = {
        "Village.tscn": "Village",
        "Forest.tscn": "Forest",
        "Cave.tscn": "Cave",
        "Dungeon.tscn": "Dungeon",
        "Area.tscn": "Area",
    }

    for filename, scene_type in scene_templates.items():
        create_basic_template_scene(scene_type, TEMPLATES_DIR / filename)

    # Character templates
    char_templates = {
        "Hero.tscn": "Hero",
        "NPC.tscn": "NPC",
        "Enemy.tscn": "Enemy",
        "Character.tscn": "Character",
    }

    for filename, role in char_templates.items():
        create_basic_character_template(role, TEMPLATES_DIR / filename)


def check_generated_scenes():
    """Check generated scenes for issues."""
    ensure_directory(SCENES_DIR)

    # List scenes and check if they load
    for scene_file in SCENES_DIR.glob("*.tscn"):
        print(f"Checking scene: {scene_file}")
        # In a real implementation, you could try to load the scene or validate syntax
        # For now, just check if file exists and has content
        if scene_file.stat().st_size == 0:
            print(f"Warning: Empty scene file: {scene_file}")
        else:
            print(f"Scene {scene_file.name} appears valid.")


def fix_script_references():
    """Fix any broken script references in generated files."""
    # This would require parsing .tscn files and checking script paths
    # Simplified: ensure scripts directory exists
    ensure_directory(SCRIPTS_DIR)
    print("Scripts directory ensured.")


def main():
    print("Running corrections for Game Maker Overlay build...")

    try:
        check_and_create_templates()
        check_generated_scenes()
        fix_script_references()

        print("Corrections completed successfully.")
    except Exception as e:
        print(f"Error during corrections: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
