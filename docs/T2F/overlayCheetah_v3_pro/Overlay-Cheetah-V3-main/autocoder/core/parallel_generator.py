"""
Parallel template generation using ThreadPoolExecutor
"""

import hashlib
import json
import os
import warnings
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, StrictUndefined


# Default number of workers - conservative default based on CPU count
DEFAULT_MAX_WORKERS = min(4, (os.cpu_count() or 1) + 2)


@dataclass
class GenerationResult:
    """Result of a template generation"""

    task_id: str
    output_path: str
    success: bool
    error: Optional[str] = None
    skipped: bool = False
    reason: Optional[str] = None


class ParallelGenerator:
    """Parallel template generator with incremental build support"""

    def __init__(
        self,
        templates_dir: Path,
        output_dir: Path,
        cache_dir: Optional[Path] = None,
        max_workers: int = DEFAULT_MAX_WORKERS,
    ):
        """Initialize parallel generator

        Args:
            templates_dir: Directory containing templates
            output_dir: Directory for generated files
            cache_dir: Directory for build cache (enables incremental builds)
            max_workers: Maximum number of parallel workers (default: CPU-based)

        Raises:
            ValueError: If max_workers <= 0
        """
        if max_workers <= 0:
            raise ValueError(f"max_workers must be positive, got {max_workers}")
        if max_workers > 32:
            warnings.warn(
                f"max_workers={max_workers} is very high, consider using a smaller value"
            )

        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.cache_dir = cache_dir or (output_dir / ".cache")
        self.max_workers = max_workers

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _compute_hash(self, template_path: str, context: Dict[str, Any]) -> str:
        """Compute hash of template and context for caching

        Args:
            template_path: Path to template
            context: Template context

        Returns:
            Hash string
        """
        hasher = hashlib.sha256()

        # Hash template content
        template_file = self.templates_dir / template_path
        if template_file.exists():
            hasher.update(template_file.read_bytes())

        # Hash context (sorted for consistency)
        context_json = json.dumps(context, sort_keys=True)
        hasher.update(context_json.encode())

        return hasher.hexdigest()

    def _should_regenerate(
        self, output_path: Path, template_path: str, context: Dict[str, Any]
    ) -> bool:
        """Check if file should be regenerated (incremental build)

        Args:
            output_path: Path to output file
            template_path: Path to template
            context: Template context

        Returns:
            True if file should be regenerated
        """
        # If output doesn't exist, regenerate
        if not output_path.exists():
            return True

        # Compute current hash
        current_hash = self._compute_hash(template_path, context)

        # Check cached hash
        try:
            cache_key = (
                str(output_path.relative_to(self.output_dir))
                .replace("/", "_")
                .replace("\\", "_")
            )
        except ValueError:
            cache_key = output_path.name
        cache_file = self.cache_dir / f"{cache_key}.hash"
        if cache_file.exists():
            cached_hash = cache_file.read_text().strip()
            if cached_hash == current_hash:
                return False  # Skip regeneration

        return True

    def _save_hash(
        self, output_path: Path, template_path: str, context: Dict[str, Any]
    ):
        """Save hash for incremental builds

        Args:
            output_path: Path to output file
            template_path: Path to template
            context: Template context
        """
        current_hash = self._compute_hash(template_path, context)
        try:
            cache_key = (
                str(output_path.relative_to(self.output_dir))
                .replace("/", "_")
                .replace("\\", "_")
            )
        except ValueError:
            cache_key = output_path.name
        cache_file = self.cache_dir / f"{cache_key}.hash"
        cache_file.write_text(current_hash)

    def _generate_single(
        self,
        task_id: str,
        template_path: str,
        output_rel: str,
        context: Dict[str, Any],
        incremental: bool = True,
        dry_run: bool = False,
    ) -> GenerationResult:
        """Generate a single file from template

        Args:
            task_id: Task identifier
            template_path: Path to template relative to templates_dir
            output_rel: Output path relative to output_dir
            context: Template context
            incremental: Enable incremental builds
            dry_run: Don't write files, just simulate

        Returns:
            GenerationResult
        """
        try:
            output_path = self.output_dir / output_rel
            output_path = output_path.resolve()
            output_dir_resolved = self.output_dir.resolve()

            # Path traversal protection: ensure output_path is within output_dir
            try:
                output_path.relative_to(output_dir_resolved)
            except ValueError:
                return GenerationResult(
                    task_id=task_id,
                    output_path=str(output_rel),
                    success=False,
                    error=f"Output path {output_rel} attempts to write outside output directory",
                )

            # Check if regeneration needed (incremental build)
            if incremental and not self._should_regenerate(
                output_path, template_path, context
            ):
                return GenerationResult(
                    task_id=task_id,
                    output_path=str(output_rel),
                    success=True,
                    skipped=True,
                    reason="unchanged (incremental build)",
                )

            # Render template
            template = self.env.get_template(template_path)
            rendered = template.render(**context)

            if dry_run:
                return GenerationResult(
                    task_id=task_id,
                    output_path=str(output_rel),
                    success=True,
                    skipped=True,
                    reason="dry run mode",
                )

            # Write output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")

            # Save hash for incremental builds
            if incremental:
                self._save_hash(output_path, template_path, context)

            return GenerationResult(
                task_id=task_id, output_path=str(output_rel), success=True
            )

        except Exception as e:
            return GenerationResult(
                task_id=task_id,
                output_path=str(output_rel),
                success=False,
                error=str(e),
            )

    def generate_parallel(
        self,
        tasks: List[Dict[str, Any]],
        incremental: bool = True,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[GenerationResult], None]] = None,
    ) -> List[GenerationResult]:
        """Generate multiple files in parallel

        Args:
            tasks: List of task dictionaries with keys:
                   - task_id: Task identifier
                   - template: Template path
                   - output: Output path
                   - context: Template context
            incremental: Enable incremental builds
            dry_run: Don't write files
            progress_callback: Optional callback for progress updates

        Returns:
            List of GenerationResult objects
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for task in tasks:
                future = executor.submit(
                    self._generate_single,
                    task["task_id"],
                    task["template"],
                    task["output"],
                    task.get("context", {}),
                    incremental,
                    dry_run,
                )
                futures[future] = task["task_id"]

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                if progress_callback:
                    progress_callback(result)

        return results

    def generate_sequential(
        self,
        tasks: List[Dict[str, Any]],
        incremental: bool = True,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[GenerationResult], None]] = None,
    ) -> List[GenerationResult]:
        """Generate files sequentially (for dependency-ordered tasks)

        Args:
            tasks: List of task dictionaries (in order)
            incremental: Enable incremental builds
            dry_run: Don't write files
            progress_callback: Optional callback for progress updates

        Returns:
            List of GenerationResult objects
        """
        results = []

        for task in tasks:
            result = self._generate_single(
                task["task_id"],
                task["template"],
                task["output"],
                task.get("context", {}),
                incremental,
                dry_run,
            )
            results.append(result)

            if progress_callback:
                progress_callback(result)

        return results

    def clear_cache(self):
        """Clear the build cache"""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.hash"):
                cache_file.unlink()
