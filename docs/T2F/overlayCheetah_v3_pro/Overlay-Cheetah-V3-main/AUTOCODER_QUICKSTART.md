# Enhanced AutoCoder - Quick Start Guide

## Overview

The Enhanced AutoCoder is a powerful template-based code generation system with advanced features for faster, more accurate code generation.

## Key Features

### 🚀 Smart Template Matching
Automatically selects the best template based on:
- File extension (`.py`, `.js`, `.tsx`, etc.)
- File path patterns
- Keyword matching in filenames
- Generic fallback templates

### ⚡ Parallel Generation
Generate multiple files concurrently using ThreadPoolExecutor:
- 4 parallel workers by default
- Progress tracking for each file
- Error handling per file

### 📦 Incremental Builds
Skip unchanged files to save time:
- SHA256 hashing of templates + context
- Build cache in `.cache/` directory
- Only regenerate when template or context changes

### 🧪 Dry Run Mode
Preview changes without writing files:
```bash
python autocoder_enhanced.py --once --dry-run
```

### 🔗 Dependency Resolution
Automatic task ordering based on dependencies:
- Topological sorting
- Circular dependency detection
- Parallel batch grouping
- Pattern-based dependency inference

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python tests/test_enhanced_features.py
```

## Quick Start

### 1. Create a Task File

Create a YAML file in the `tasks/` directory:

```yaml
# tasks/my_project.yaml
task_id: my_project
files:
  - template: python/api.py.j2
    output: src/api.py
    context:
      description: "My REST API"
      app_name: "MyAPI"
      models:
        - name: Item
          fields:
            - name: id
              type: int
            - name: name
              type: str
```

### 2. Run the Autocoder

```bash
# Generate files once
python autocoder_enhanced.py --once

# Watch mode (continuous generation)
python autocoder_enhanced.py

# Dry run (preview without writing)
python autocoder_enhanced.py --once --dry-run
```

### 3. Check the Output

Generated files will be in the `out/` directory:
```
out/
├── src/
│   └── api.py
```

## Command-Line Options

```bash
python autocoder_enhanced.py [options]

Options:
  --once              Process tasks once and exit
  --interval SECONDS  Watch interval (default: 3.0)
  --dry-run           Simulate without writing files
  --no-format         Skip code formatting with black
  --test              Run pytest after generation
  --no-parallel       Disable parallel generation
  --no-incremental    Disable incremental builds
  --legacy            Use legacy handler
  --clear-cache       Clear build cache
  -h, --help          Show help message
```

## Template Examples

### Python Generic Template

```jinja2
"""{{ description }}"""

{% if imports is defined %}
# Imports
{% for imp in imports %}
{{ imp }}
{% endfor %}
{% endif %}

{% if classes is defined %}
# Classes
{% for class_info in classes %}
class {{ class_info.name }}:
    """{{ class_info.get('docstring', 'Class') }}"""
    pass
{% endfor %}
{% endif %}
```

### FastAPI Template

```jinja2
"""{{ description }}"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{{ app_name }}")

{% if models %}
{% for model in models %}
class {{ model.name }}(BaseModel):
{% for field in model.fields %}
    {{ field.name }}: {{ field.type }}
{% endfor %}
{% endfor %}
{% endif %}
```

## Task File Format

```yaml
task_id: unique_task_name
files:
  - template: path/to/template.j2  # Relative to templates/
    output: output/path.py         # Relative to out/
    context:                       # Template variables
      description: "Description"
      # ... other variables
```

## Architecture

```
autocoder_enhanced.py          # Main entry point
├── autocoder/core/
│   ├── template_matcher.py    # Smart template selection
│   ├── dependency_resolver.py # Task ordering
│   ├── parallel_generator.py  # Concurrent generation
│   └── engine.py              # Core engine
├── templates/                 # Jinja2 templates
│   ├── python/
│   │   ├── generic.py.j2
│   │   └── api.py.j2
│   └── javascript/
│       └── component.js.j2
├── tasks/                     # Task definitions
│   └── example.yaml
└── out/                       # Generated code
```

## Advanced Usage

### Incremental Builds

Incremental builds automatically skip unchanged files:

```bash
# First run: generates all files
python autocoder_enhanced.py --once

# Second run: skips unchanged files
python autocoder_enhanced.py --once
```

Clear cache to force regeneration:
```bash
python autocoder_enhanced.py --clear-cache
```

### Parallel vs Sequential

```bash
# Parallel (default, faster)
python autocoder_enhanced.py --once

# Sequential (for debugging)
python autocoder_enhanced.py --once --no-parallel
```

### Template Validation

Templates are validated before rendering:
- Syntax errors are caught early
- Detailed error messages
- Per-file error reporting

## Troubleshooting

### Template Errors

If you see template errors:
1. Check Jinja2 syntax
2. Use `.get()` for dictionary access: `{{ var.get('key', 'default') }}`
3. Use `is defined` for existence checks: `{% if var is defined %}`

### Missing Templates

The system automatically searches for:
1. Exact template match
2. Generic template by extension
3. Fallback templates

### Performance

For large projects:
- Use `--parallel` (default)
- Enable `--incremental` (default)
- Adjust `--interval` for watch mode

## Examples

See `tasks/example.yaml` for a complete example that generates:
- FastAPI REST API with Pydantic models
- Base model classes
- Proper imports and formatting

## Testing

Run the test suite:
```bash
# All tests
python -m pytest tests/test_enhanced_features.py -v

# Specific test
python -m pytest tests/test_enhanced_features.py::TestTemplateMatcher -v
```

## Migration from Original AutoCoder

The enhanced autocoder is backwards compatible:

```bash
# Original
python autocoder.py --once

# Enhanced (use --legacy for exact same behavior)
python autocoder_enhanced.py --once --legacy
```

## Next Steps

1. Explore templates in `templates/`
2. Create your own task files in `tasks/`
3. Run with `--dry-run` to preview
4. Generate code with `--once`
5. Enable watch mode for continuous generation

## Performance Tips

- Use incremental builds for faster iteration
- Enable parallel generation for multiple files
- Clear cache when changing template structure
- Use dry-run to test before generating

## Support

For issues or questions:
- Check this README
- Review example task: `tasks/example.yaml`
- Run tests: `python tests/test_enhanced_features.py`
- Check logs in `reports/`
