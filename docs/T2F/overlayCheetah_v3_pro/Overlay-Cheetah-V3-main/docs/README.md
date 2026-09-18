# Overlay Cheetah V3 Documentation

<!-- Branding -->
<div align="center">
  <img src="../assets/branding/overlay-cheetah-logo.svg" alt="Overlay Cheetah Logo - Lightning-Fast AI Autocoder" width="400"/>
  
  <br/><br/>
  
  <img src="../assets/branding/overlay365-brand.svg" alt="Overlay365 Brand - Professional Development Suite" width="600"/>
  
  <p><em>Complete documentation for Overlay Cheetah V3 - An advanced AI-powered autocoder by Overlay365</em></p>
</div>

---

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Reference](#api-reference)

## Introduction

Overlay Cheetah V3 is an advanced AI-powered autocoder that helps developers write better code faster. It provides intelligent code generation, analysis, refactoring, and completion capabilities.

### Key Features
- 🚀 **Intelligent Code Generation**: Generate production-ready code from natural language prompts
- 🔍 **Advanced Code Analysis**: Deep analysis of code quality, complexity, and potential issues
- ✨ **Smart Refactoring**: Automatically refactor code following best practices
- ⚡ **Real-time Completion**: Context-aware code completion
- 🛡️ **Security First**: Built-in security scanning and vulnerability detection
- 🔧 **CLI & API Access**: Powerful command-line interface and REST API

## Installation

### Using pip
```bash
pip install overlay-cheetah
```

### From source
```bash
git clone https://github.com/tap919/Overlay-Cheetah-V3.git
cd Overlay-Cheetah-V3
python setup.py install
```

### Requirements
- Python 3.8 or higher
- PyYAML 6.0 or higher

## Quick Start

### Generate Code
```bash
# Create a prompt file
echo "Create a Python function that calculates factorial" > prompt.txt

# Generate code
overlay-cheetah generate --input prompt.txt --output factorial.py
```

### Analyze Code
```bash
# Analyze a Python file
overlay-cheetah analyze --file mycode.py

# Save analysis report
overlay-cheetah analyze --file mycode.py --report report.json
```

### Refactor Code
```bash
# Refactor using PEP8 style guide
overlay-cheetah refactor --file code.py --style pep8

# Save to different file
overlay-cheetah refactor --file code.py --style pep8 --output refactored.py
```

### Auto-complete Code
```bash
# Complete code with additional context
overlay-cheetah complete --file incomplete.py --context "web application"
```

## Commands

### generate
Generate code from natural language prompts.

**Usage:**
```bash
overlay-cheetah generate --input <prompt_file> --output <output_file> [--language <lang>]
```

**Options:**
- `--input`: Input prompt file (required)
- `--output`: Output code file (required)
- `--language`: Target programming language (default: python)

### analyze
Analyze existing code for quality, complexity, and issues.

**Usage:**
```bash
overlay-cheetah analyze --file <file> [--report <report_file>]
```

**Options:**
- `--file`: File to analyze (required)
- `--report`: Output report file (optional, prints to console if not specified)

### refactor
Refactor code according to style guides and best practices.

**Usage:**
```bash
overlay-cheetah refactor --file <file> [--style <style>] [--output <output_file>]
```

**Options:**
- `--file`: File to refactor (required)
- `--style`: Coding style guide (default: default)
- `--output`: Output file (optional, overwrites input if not specified)

### complete
Auto-complete code based on context.

**Usage:**
```bash
overlay-cheetah complete --file <file> [--context <context>]
```

**Options:**
- `--file`: File to complete (required)
- `--context`: Additional context for completion (optional)

## Configuration

Overlay Cheetah uses a YAML configuration file. By default, it looks for `config.yaml` in the current directory.

### Specifying a custom config file
```bash
overlay-cheetah --config myconfig.yaml generate --input prompt.txt --output code.py
```

### Configuration Options

```yaml
# AI Model settings
model: "gpt-4"
temperature: 0.7
max_tokens: 2000

# Language-specific defaults
language_defaults:
  python:
    style: "pep8"
    max_line_length: 88
  javascript:
    style: "airbnb"
    max_line_length: 100

# Output settings
output:
  format: "auto"
  encoding: "utf-8"
  add_headers: true

# Analysis settings
analysis:
  check_complexity: true
  check_style: true
  max_complexity: 10
```

## Examples

### Example 1: Generate a REST API
```bash
# Create prompt
cat > prompt.txt << EOF
Create a Flask REST API with the following endpoints:
- GET /users - list all users
- POST /users - create a new user
- GET /users/<id> - get user by id
- PUT /users/<id> - update user
- DELETE /users/<id> - delete user
EOF

# Generate code
overlay-cheetah generate --input prompt.txt --output api.py --language python
```

### Example 2: Analyze and Refactor
```bash
# Analyze code
overlay-cheetah analyze --file myapp.py --report analysis.json

# Refactor based on findings
overlay-cheetah refactor --file myapp.py --style pep8
```

### Example 3: Complete Partial Code
```bash
# Create incomplete code file
cat > incomplete.py << EOF
def calculate_statistics(data):
    # TODO: Calculate mean, median, and mode
    pass
EOF

# Complete the code
overlay-cheetah complete --file incomplete.py --context "statistical analysis"
```

## API Reference

### AutocoderEngine

The core engine class for Overlay Cheetah.

```python
from autocoder.core.engine import AutocoderEngine
from autocoder.core.config import Config

# Initialize
config = Config.load('config.yaml')
engine = AutocoderEngine(config)

# Generate code
engine.generate('prompt.txt', 'output.py', 'python')

# Analyze code
results = engine.analyze('mycode.py')

# Refactor code
engine.refactor('code.py', 'refactored.py', 'pep8')

# Complete code
engine.complete('incomplete.py', 'additional context')
```

### Config

Configuration management class.

```python
from autocoder.core.config import Config

# Load from file
config = Config.load('config.yaml')

# Get values
model = config.get('model', 'gpt-4')

# Set values
config.set('temperature', 0.8)
```

## Supported Languages

Overlay Cheetah V3 supports code generation, analysis, and refactoring for:

- Python
- JavaScript/TypeScript
- Java
- C/C++
- Go
- Rust
- Ruby
- PHP
- Swift
- Kotlin
- And 40+ more languages

## Support

- 📧 Email: support@overlaycheetah.com
- 🐛 Issues: https://github.com/tap919/Overlay-Cheetah-V3/issues
- 📖 Documentation: https://github.com/tap919/Overlay-Cheetah-V3/docs

## License

Overlay Cheetah V3 is licensed under the Apache License 2.0. See LICENSE for details.
