<file_path>
project 5\AutoCoder-Forge-Basic\COPILOT_README.md
</file_path>

<edit_description>
Create Copilot README file for AutoCoder consistency
</edit_description>

# Copilot README: AutoCoder Execution Guide for Cheetah Chat Builds

## Overview
You (GitHub Copilot) are assisting in building "Cheetah Chat," a productivity-focused AI coding app. Use AutoCoder (a lightweight tool in this project) to generate code from templates. AutoCoder reads YAML tasks from `tasks/`, renders Jinja2 templates from `templates/`, outputs to `out/`, formats with Black, runs tests, and creates reports.

**Goal**: Generate complete, EXE-ready systems with guardrails, auditing, dependencies, optimizations, and tool integrations. Ensure builds are tested, debugged, and fixed in iterations.

## Prerequisites
- Project structure: `AutoCoder-Forge-Basic/` with `autocoder.py`, `tasks/`, `templates/`, `out/`, `reports/`.
- Templates exist in `templates/` (e.g., `main_app.py.j2`). If missing, create basic ones.
- Python environment with Jinja2, PyYAML, Black, pytest.
- Copilot access to terminal for commands.

## Step-by-Step Process for Each Build
Follow this exactly for consistency. Do not deviate unless user specifies.

1. **Understand the Request**: User wants a build (e.g., Cheetah Chat EXE). Confirm features: guardrails, auditing, dependencies, tools, testing, EXE packaging.

2. **Write the YAML Template**:
   - Create a new YAML file in `tasks/` (e.g., `cheetah_chat_build.yaml`).
   - Structure:
     - `task_id`: Unique name (e.g., "cheetah_chat_build").
     - `description`: Brief overview.
     - `author`, `created_by`, `created_at`, `priority`: Standard metadata.
     - `files`: List of dicts with `template` (Jinja2 file), `output` (path in `out/`), `context` (variables).
     - `notes`: Any extras.
   - Include files for: main app, UI, tools, guardrails, auditing, dependencies, optimizer, tests, build script.
   - Example YAML:
     ```yaml
     task_id: cheetah_chat_build
     description: Build Cheetah Chat EXE with all features.
     author: AutoCoder
     created_by: copilot
     created_at: 2024-12-19T18:00:00Z
     priority: high
     files:
       - template: main_app.py.j2
         output: main.py
         context: {app_name: "CheetahChat", features: ["chat", "guardrails"]}
       # Add more files...
     notes: Test and fix in second run.
     completion_target: "100%"
     estimated_time: "60 seconds"
     ```

3. **Save and Validate YAML**:
   - Ensure valid YAML (no syntax errors).
   - Check for required fields.

4. **Initiate AutoCoder**:
   - Run: `python autocoder.py --once --test` (from `AutoCoder-Forge-Basic/`).
   - This generates files in `out/`, formats, tests, reports.

5. **Review Output**:
   - Check `out/` for generated files.
   - Review `reports/cheetah_chat_build.json` for errors.
   - If tests fail, debug (e.g., fix templates, add mocks).

6. **Second Run for Fixes**:
   - Update YAML or templates based on errors.
   - Re-run: `python autocoder.py --once --test`.
   - Ensure all tests pass; build EXE via generated `build_exe.py`.

7. **Finalize**:
   - Confirm EXE in `out/` (e.g., `CheetahChat.exe`).
   - Report completion to user.

## Tips for Consistency
- Always start with this README.
- Use exact YAML structure.
- If templates missing, generate basic ones (e.g., `{{app_name}}` in Jinja2).
- Handle errors: Missing imports → Add to context; Test failures → Update test template.
- For Cheetah Chat specifics: Include guardrails (validation), auditing (linting), dependencies (pre-checks), tools (integrations), optimizations (caching), EXE (PyInstaller).
- If user changes request, adapt YAML accordingly but follow process.

## Example Full YAML for Cheetah Chat
See above example. Expand `files` for all components.

This ensures every session proceeds smoothly. If issues, escalate to user.