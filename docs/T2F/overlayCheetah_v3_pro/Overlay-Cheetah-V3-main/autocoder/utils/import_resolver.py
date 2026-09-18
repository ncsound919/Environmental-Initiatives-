"""
Auto-import resolver to add missing imports automatically
"""

import re
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict


# Common import patterns for different languages
PYTHON_IMPORTS = {
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Optional": "from typing import Optional",
    "Any": "from typing import Any",
    "Tuple": "from typing import Tuple",
    "Set": "from typing import Set",
    "Union": "from typing import Union",
    "datetime": "from datetime import datetime",
    "Path": "from pathlib import Path",
    "json": "import json",
    "os": "import os",
    "sys": "import sys",
    "re": "import re",
}


class ImportResolver:
    """Automatically resolves and adds missing imports"""

    def __init__(self, language: str = "python"):
        """Initialize import resolver

        Args:
            language: Programming language (python, javascript, etc.)
        """
        self.language = language.lower()
        self.import_map = self._load_import_map()

    def _load_import_map(self) -> Dict[str, str]:
        """Load import mapping for the language

        Returns:
            Dictionary mapping symbols to import statements
        """
        if self.language == "python":
            return PYTHON_IMPORTS.copy()
        elif self.language == "javascript" or self.language == "typescript":
            # TODO: Add JavaScript/TypeScript imports
            return {}
        else:
            return {}

    def find_missing_imports(self, code: str) -> List[str]:
        """Find missing imports in code

        Args:
            code: Source code to analyze

        Returns:
            List of import statements to add
        """
        if self.language == "python":
            return self._find_missing_python_imports(code)
        else:
            return []

    def _find_missing_python_imports(self, code: str) -> List[str]:
        """Find missing Python imports

        Args:
            code: Python source code

        Returns:
            List of import statements
        """
        # Extract existing imports
        existing_imports = self._extract_existing_imports(code)

        # Find used symbols
        used_symbols = self._find_used_symbols(code)

        # Determine missing imports
        missing_imports = []
        for symbol in used_symbols:
            if symbol in self.import_map:
                import_stmt = self.import_map[symbol]
                if import_stmt not in existing_imports:
                    missing_imports.append(import_stmt)

        return list(set(missing_imports))  # Remove duplicates

    def _extract_existing_imports(self, code: str) -> Set[str]:
        """Extract existing import statements

        Args:
            code: Source code

        Returns:
            Set of import statements
        """
        imports = set()

        # Match import statements
        import_pattern = r"^(?:from\s+[\w.]+\s+)?import\s+.+$"
        for line in code.split("\n"):
            line = line.strip()
            if re.match(import_pattern, line):
                imports.add(line)

        return imports

    def _find_used_symbols(self, code: str) -> Set[str]:
        """Find symbols used in code

        Args:
            code: Source code

        Returns:
            Set of symbol names
        """
        symbols = set()

        # Look for typing annotations
        typing_pattern = r":\s*([A-Z][a-zA-Z]*)"
        for match in re.finditer(typing_pattern, code):
            symbols.add(match.group(1))

        # Look for return type annotations
        return_pattern = r"->\s*([A-Z][a-zA-Z]*)"
        for match in re.finditer(return_pattern, code):
            symbols.add(match.group(1))

        # Look for common module usage
        for module in ["json", "os", "sys", "re", "datetime", "Path"]:
            if re.search(r"\b" + module + r"\b", code):
                symbols.add(module)

        return symbols

    def add_imports(self, code: str) -> str:
        """Add missing imports to code

        Args:
            code: Source code

        Returns:
            Code with imports added
        """
        missing = self.find_missing_imports(code)

        if not missing:
            return code

        # Find insertion point (after docstring, before first code)
        lines = code.split("\n")
        insert_pos = 0

        # Skip docstring
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    insert_pos = i + 1
                    break
                in_docstring = True

            if not in_docstring and stripped and not stripped.startswith("#"):
                insert_pos = i
                break

        # Insert imports
        import_block = "\n".join(sorted(missing)) + "\n\n"
        lines.insert(insert_pos, import_block)

        return "\n".join(lines)

    def add_custom_mapping(self, symbol: str, import_stmt: str):
        """Add custom import mapping

        Args:
            symbol: Symbol name
            import_stmt: Import statement
        """
        self.import_map[symbol] = import_stmt


def resolve_imports_in_file(file_path: Path, language: str = "python") -> bool:
    """Resolve imports in a file

    Args:
        file_path: Path to file
        language: Programming language

    Returns:
        True if file was modified
    """
    if not file_path.exists():
        return False

    code = file_path.read_text(encoding="utf-8")
    resolver = ImportResolver(language)

    new_code = resolver.add_imports(code)

    if new_code != code:
        file_path.write_text(new_code, encoding="utf-8")
        return True

    return False
