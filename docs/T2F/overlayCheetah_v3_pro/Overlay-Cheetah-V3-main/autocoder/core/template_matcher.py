"""
Smart template matching with regex and fuzzy scoring
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


# Stop words for keyword extraction
TEMPLATE_STOP_WORDS = {"template", "tmpl", "tpl", "file", "default", "base"}

# Scoring weights for template matching
EXTENSION_MATCH_WEIGHT = 0.5  # Highest priority: file extension must match
KEYWORD_MATCH_WEIGHT = 0.3  # Medium priority: keyword overlap
PATH_MATCH_WEIGHT = 0.1  # Low priority: directory structure similarity

# Score thresholds
MIN_TEMPLATE_MATCH_SCORE = 0.3  # Minimum score to consider a template match valid
GENERIC_FALLBACK_SCORE = 0.2  # Score assigned to generic fallback templates


@dataclass
class TemplateMatch:
    """Represents a template match with score"""

    template_path: str
    score: float
    reason: str


class TemplateMatcher:
    """Smart template matcher using file extension, path, and keyword matching"""

    def __init__(self, templates_dir: Path):
        """Initialize template matcher

        Args:
            templates_dir: Directory containing templates
        """
        self.templates_dir = templates_dir
        self.template_index = self._build_template_index()

    def _build_template_index(self) -> Dict[str, Dict[str, Any]]:
        """Build an index of available templates with metadata

        Returns:
            Dictionary mapping template names to metadata
        """
        index = {}

        if not self.templates_dir.exists():
            return index

        for template_file in self.templates_dir.rglob("*"):
            if template_file.is_file() and not template_file.name.startswith("."):
                rel_path = str(template_file.relative_to(self.templates_dir))

                # Determine target extension (strip .j2 if present)
                target_ext = template_file.suffix.lstrip(".")
                stem = template_file.stem
                if target_ext == "j2" and "." in stem:
                    # Template like "api.py.j2" -> extension is "py"
                    target_ext = stem.split(".")[-1]
                    stem = ".".join(stem.split(".")[:-1])

                # Extract metadata from template path and name
                metadata = {
                    "path": rel_path,
                    "extension": target_ext,
                    "name": stem,
                    "keywords": self._extract_keywords(stem),
                    "parent_dir": template_file.parent.name,
                }

                index[rel_path] = metadata

        return index

    def _extract_keywords(self, filename: str) -> List[str]:
        """Extract keywords from filename

        Args:
            filename: Template filename

        Returns:
            List of keywords
        """
        # Split on common separators
        parts = re.split(r"[_\-\.]", filename.lower())
        # Filter out common words
        keywords = [p for p in parts if p and p not in TEMPLATE_STOP_WORDS]
        return keywords

    def match_template(
        self,
        target_path: str,
        context: Optional[Dict[str, Any]] = None,
        min_score: float = MIN_TEMPLATE_MATCH_SCORE,
    ) -> Optional[TemplateMatch]:
        """Match a template for the target file

        Args:
            target_path: Path of the file to generate
            context: Additional context for matching
            min_score: Minimum score threshold for a match

        Returns:
            Best matching template or None if no match found
        """
        context = context or {}
        target = Path(target_path)

        # Calculate scores for all templates
        matches = []
        for template_path, metadata in self.template_index.items():
            score, reason = self._calculate_match_score(target, metadata, context)
            if score >= min_score:
                matches.append(TemplateMatch(template_path, score, reason))

        # Return best match
        if matches:
            matches.sort(key=lambda x: x.score, reverse=True)
            return matches[0]

        # Try to find a generic fallback
        return self._find_generic_fallback(target)

    def _calculate_match_score(
        self, target: Path, template_metadata: Dict[str, Any], context: Dict[str, Any]
    ) -> Tuple[float, str]:
        """Calculate match score for a template

        Args:
            target: Target file path
            template_metadata: Template metadata
            context: Additional context

        Returns:
            Tuple of (score, reason)
        """
        score = 0.0
        reasons = []

        # Extension match (highest weight)
        target_ext = target.suffix.lstrip(".")
        if target_ext == template_metadata["extension"]:
            score += EXTENSION_MATCH_WEIGHT
            reasons.append(f"extension match ({target_ext})")

        # Filename keyword match
        target_keywords = self._extract_keywords(target.stem)
        template_keywords = template_metadata["keywords"]

        matching_keywords = set(target_keywords) & set(template_keywords)
        if matching_keywords:
            keyword_score = len(matching_keywords) / max(
                len(target_keywords), len(template_keywords)
            )
            score += keyword_score * KEYWORD_MATCH_WEIGHT
            reasons.append(f"keywords: {', '.join(matching_keywords)}")

        # Path similarity
        if target.parent.name == template_metadata["parent_dir"]:
            score += PATH_MATCH_WEIGHT
            reasons.append(f"parent dir match ({target.parent.name})")

        # Context hints
        if "file_type" in context:
            if context["file_type"].lower() in template_metadata["name"].lower():
                score += 0.1
                reasons.append(f"context file_type match")

        reason = "; ".join(reasons) if reasons else "no match"
        return score, reason

    def _find_generic_fallback(self, target: Path) -> Optional[TemplateMatch]:
        """Find a generic fallback template for the file type

        Args:
            target: Target file path

        Returns:
            Generic template match or None
        """
        target_ext = target.suffix.lstrip(".")

        # Look for generic templates
        generic_patterns = [
            f"generic.{target_ext}",
            f"generic_{target_ext}.j2",
            f"default.{target_ext}",
            f"base_{target_ext}.j2",
            f"{target_ext}/generic.j2",
            f"{target_ext}/default.j2",
        ]

        for pattern in generic_patterns:
            if pattern in self.template_index:
                return TemplateMatch(
                    template_path=pattern,
                    score=GENERIC_FALLBACK_SCORE,
                    reason=f"generic fallback for .{target_ext}",
                )

        return None

    def get_all_templates(self) -> List[str]:
        """Get list of all available templates

        Returns:
            List of template paths
        """
        return list(self.template_index.keys())

    def get_templates_by_extension(self, extension: str) -> List[str]:
        """Get templates for a specific file extension

        Args:
            extension: File extension (without dot)

        Returns:
            List of matching template paths
        """
        return [
            path
            for path, metadata in self.template_index.items()
            if metadata["extension"] == extension
        ]
