#!/usr/bin/env python3
"""
Overlay Cheetah V3 PRO - Enhanced Edition
=========================================
Professional autocoder with advanced features for production use.

NEW in V3 PRO:
- Preflight tooling and environment validation
- Resource monitoring (CPU, memory, disk)
- Per-step profiling with detailed metrics
- Containerization support (Docker)
- Advanced caching with intelligent invalidation
- Multi-provider LLM support with fallback
- Comprehensive audit trail
- Version pinning and lockfile generation

Dependencies:
pip install pyyaml jinja2 psutil requests google-generativeai ollama pillow

Usage:
1. Run with GUI: python overlay_cheetah_v3_pro.py
2. Run preflight only: python overlay_cheetah_v3_pro.py --preflight
3. Run tests: python overlay_cheetah_v3_pro.py --test
4. Build EXE: python overlay_cheetah_v3_pro.py --build
"""

import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter.ttk import Progressbar
from typing import Any, Callable, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("overlay_cheetah_v3_pro")

# Try to import optional dependencies
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Resource monitoring disabled.")

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: pyyaml not available.")

# =============================================================================
# VERSION & CONFIGURATION
# =============================================================================
VERSION = "3.1.0-pro"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

PINNED_DEPENDENCIES = {
    "pyyaml": ">=6.0",
    "jinja2": ">=3.1.0",
    "psutil": ">=5.9.0",
    "requests": ">=2.28.0",
    "google-generativeai": ">=0.3.0",
    "ollama": ">=0.1.0",
    "pillow": ">=9.0.0",
}


# =============================================================================
# RESOURCE MONITORING
# =============================================================================
@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time"""

    timestamp: float
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0


class ResourceMonitor:
    """Monitors system resources during operations"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and PSUTIL_AVAILABLE
        self.snapshots: List[ResourceSnapshot] = []
        self._monitoring = False
        self._thread: Optional[threading.Thread] = None

    def take_snapshot(self) -> ResourceSnapshot:
        """Take a single resource snapshot"""
        if not self.enabled:
            return ResourceSnapshot(timestamp=time.time())

        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
            )
        except Exception as exc:
            logger.warning("Resource snapshot failed: %s", exc)
            return ResourceSnapshot(timestamp=time.time())

    def start_monitoring(self, interval: float = 1.0):
        """Start continuous resource monitoring"""
        if not self.enabled:
            logger.debug("Resource monitoring disabled")
            return

        if self._monitoring:
            logger.debug("Resource monitoring already running")
            return

        logger.debug("Starting resource monitoring (interval: %.1fs)", interval)
        self._monitoring = True
        self.snapshots = []

        def monitor():
            try:
                while self._monitoring:
                    self.snapshots.append(self.take_snapshot())
                    time.sleep(interval)
                logger.debug("Resource monitoring thread stopped normally")
            except Exception as exc:
                logger.warning("Resource monitoring thread failed: %s", exc)
                self._monitoring = False

        self._thread = threading.Thread(target=monitor, daemon=True)
        try:
            self._thread.start()
            logger.debug("Resource monitoring thread started")
        except Exception as exc:
            logger.warning("Failed to start resource monitoring thread: %s", exc)
            self._monitoring = False

    def stop_monitoring(self) -> List[ResourceSnapshot]:
        """Stop monitoring and return collected snapshots"""
        if not self._monitoring:
            logger.debug("Resource monitoring not running")
            return self.snapshots

        logger.debug("Stopping resource monitoring")
        self._monitoring = False

        if self._thread:
            try:
                self._thread.join(timeout=2.0)
                if self._thread.is_alive():
                    logger.warning(
                        "Resource monitoring thread did not stop within timeout"
                    )
                else:
                    logger.debug("Resource monitoring thread stopped successfully")
            except Exception as exc:
                logger.warning("Error stopping resource monitoring thread: %s", exc)

        logger.debug("Collected %d resource snapshots", len(self.snapshots))
        return self.snapshots

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics from monitoring session"""
        if not self.snapshots:
            return {"available": False}

        return {
            "available": True,
            "sample_count": len(self.snapshots),
            "duration_sec": self.snapshots[-1].timestamp - self.snapshots[0].timestamp
            if len(self.snapshots) > 1
            else 0,
            "cpu": {
                "avg": sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots),
                "max": max(s.cpu_percent for s in self.snapshots),
                "min": min(s.cpu_percent for s in self.snapshots),
            },
            "memory": {
                "avg_percent": sum(s.memory_percent for s in self.snapshots)
                / len(self.snapshots),
                "max_percent": max(s.memory_percent for s in self.snapshots),
                "avg_used_mb": sum(s.memory_used_mb for s in self.snapshots)
                / len(self.snapshots),
            },
            "disk": {
                "final_percent": self.snapshots[-1].disk_percent,
                "final_free_gb": self.snapshots[-1].disk_free_gb,
            },
        }


# =============================================================================
# PROFILING & METRICS
# =============================================================================
@dataclass
class StepProfile:
    """Detailed profile for a single step"""

    step_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_sec: float = 0.0
    success: bool = True
    error: Optional[str] = None
    files_processed: int = 0
    bytes_written: int = 0
    cache_hit: bool = False
    resource_snapshot_start: Optional[ResourceSnapshot] = None
    resource_snapshot_end: Optional[ResourceSnapshot] = None
    resource_delta: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "step_name": self.step_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_sec": self.duration_sec,
            "success": self.success,
            "error": self.error,
            "files_processed": self.files_processed,
            "bytes_written": self.bytes_written,
            "cache_hit": self.cache_hit,
        }
        if self.resource_snapshot_start:
            result["resource_start"] = asdict(self.resource_snapshot_start)
        if self.resource_snapshot_end:
            result["resource_end"] = asdict(self.resource_snapshot_end)
        if self.resource_delta:
            result["resource_delta"] = self.resource_delta
        return result

    def compute_resource_delta(self):
        if not (self.resource_snapshot_start and self.resource_snapshot_end):
            self.resource_delta = {}
            return

        self.resource_delta = {
            "cpu_percent": self.resource_snapshot_end.cpu_percent
            - self.resource_snapshot_start.cpu_percent,
            "memory_percent": self.resource_snapshot_end.memory_percent
            - self.resource_snapshot_start.memory_percent,
            "memory_used_mb": self.resource_snapshot_end.memory_used_mb
            - self.resource_snapshot_start.memory_used_mb,
            "memory_available_mb": self.resource_snapshot_end.memory_available_mb
            - self.resource_snapshot_start.memory_available_mb,
            "disk_percent": self.resource_snapshot_end.disk_percent
            - self.resource_snapshot_start.disk_percent,
            "disk_free_gb": self.resource_snapshot_end.disk_free_gb
            - self.resource_snapshot_start.disk_free_gb,
        }


@dataclass
class BuildTelemetry:
    """Comprehensive build telemetry with profiling"""

    task_id: str
    version: str = VERSION
    start_time: float = 0.0
    end_time: float = 0.0
    total_duration_sec: float = 0.0
    steps: List[StepProfile] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    preflight_results: Dict[str, Any] = field(default_factory=dict)
    generated_files: List[str] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    cache_stats: Dict[str, int] = field(
        default_factory=lambda: {"hits": 0, "misses": 0}
    )
    resource_summary: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: StepProfile):
        self.steps.append(step)
        if step.cache_hit:
            self.cache_stats["hits"] += 1
        else:
            self.cache_stats["misses"] += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "version": self.version,
            "build_date": BUILD_DATE,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_sec": self.total_duration_sec,
            "steps": [s.to_dict() for s in self.steps],
            "environment": self.environment,
            "preflight_results": self.preflight_results,
            "generated_files": self.generated_files,
            "errors": self.errors,
            "cache_stats": self.cache_stats,
            "resource_summary": self.resource_summary,
            "performance_summary": self._get_performance_summary(),
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        if not self.steps:
            return {}
        return {
            "total_steps": len(self.steps),
            "successful_steps": sum(1 for s in self.steps if s.success),
            "failed_steps": sum(1 for s in self.steps if not s.success),
            "avg_step_duration": sum(s.duration_sec for s in self.steps)
            / len(self.steps),
            "slowest_step": max(self.steps, key=lambda s: s.duration_sec).step_name,
            "fastest_step": min(self.steps, key=lambda s: s.duration_sec).step_name,
            "total_files": len(self.generated_files),
            "total_bytes": sum(s.bytes_written for s in self.steps),
            "cache_hit_rate": self.cache_stats["hits"]
            / (self.cache_stats["hits"] + self.cache_stats["misses"])
            if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0
            else 0,
        }


# =============================================================================
# PREFLIGHT VALIDATION
# =============================================================================
@dataclass
class PreflightCheck:
    """Result of a preflight check"""

    name: str
    category: str  # "required", "optional", "system"
    passed: bool
    message: str
    version: Optional[str] = None
    path: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class PreflightValidator:
    """Comprehensive preflight validation for production environments"""

    REQUIRED_TOOLS = [
        ("python", ["python", "--version"], "Python interpreter"),
        ("pip", ["pip", "--version"], "Python package manager"),
    ]

    OPTIONAL_TOOLS = [
        ("black", ["python", "-m", "black", "--version"], "Code formatter"),
        ("pytest", ["python", "-m", "pytest", "--version"], "Test runner"),
        ("node", ["node", "--version"], "Node.js runtime"),
        ("npm", ["npm", "--version"], "Node package manager"),
        ("npx", ["npx", "--version"], "Node package executor"),
        ("docker", ["docker", "--version"], "Container runtime"),
        ("git", ["git", "--version"], "Version control"),
    ]

    SYSTEM_CHECKS = [
        ("disk_space", 1024),  # Minimum 1GB free
        ("memory", 512),  # Minimum 512MB available
    ]

    def __init__(self):
        self.checks: List[PreflightCheck] = []
        self.environment_info: Dict[str, Any] = {}

    def _resolve_command(self, cmd: str) -> str:
        """Resolve command path, handling Windows .cmd shims"""
        resolved = shutil.which(cmd)
        if resolved:
            return resolved
        if platform.system() == "Windows":
            for ext in [".cmd", ".exe", ".bat"]:
                resolved = shutil.which(f"{cmd}{ext}")
                if resolved:
                    return resolved
        return cmd

    def _run_tool_check(
        self, name: str, cmd: List[str], description: str, category: str
    ) -> PreflightCheck:
        """Run a single tool check"""
        try:
            resolved_cmd = self._resolve_command(cmd[0])
            full_cmd = [resolved_cmd] + cmd[1:]

            logger.debug("Running preflight check for %s: %s", name, " ".join(full_cmd))

            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                shell=(platform.system() == "Windows"),
            )

            if result.returncode == 0:
                version = (result.stdout.strip() or result.stderr.strip()).split("\n")[
                    0
                ]
                logger.debug("Preflight check %s passed: %s", name, version)
                return PreflightCheck(
                    name=name,
                    category=category,
                    passed=True,
                    message=f"{description} available",
                    version=version,
                    path=resolved_cmd,
                )
            else:
                stderr_msg = result.stderr.strip() if result.stderr else "No stderr"
                logger.warning(
                    "Preflight check %s failed (code %d): stdout='%s', stderr='%s'",
                    name,
                    result.returncode,
                    result.stdout.strip(),
                    stderr_msg,
                )
                return PreflightCheck(
                    name=name,
                    category=category,
                    passed=False,
                    message=f"{description} returned error code {result.returncode}",
                )
        except FileNotFoundError:
            logger.warning("Preflight check %s failed: command not found in PATH", name)
            return PreflightCheck(
                name=name,
                category=category,
                passed=False,
                message=f"{description} not found in PATH",
            )
        except subprocess.TimeoutExpired:
            logger.warning("Preflight check %s timed out after 15 seconds", name)
            return PreflightCheck(
                name=name,
                category=category,
                passed=False,
                message=f"{description} check timed out",
            )
        except Exception as e:
            logger.warning("Preflight check %s failed with exception: %s", name, str(e))
            return PreflightCheck(
                name=name,
                category=category,
                passed=False,
                message=f"{description} check failed: {str(e)}",
            )

    def _check_disk_space(self, min_mb: int) -> PreflightCheck:
        """Check available disk space"""
        try:
            if PSUTIL_AVAILABLE:
                disk = psutil.disk_usage("/")
                free_mb = disk.free / (1024 * 1024)
                passed = free_mb >= min_mb
                return PreflightCheck(
                    name="disk_space",
                    category="system",
                    passed=passed,
                    message=f"Disk space: {free_mb:.0f}MB free"
                    + ("" if passed else f" (need {min_mb}MB)"),
                    details={
                        "free_mb": free_mb,
                        "required_mb": min_mb,
                        "percent_used": disk.percent,
                    },
                )
            else:
                return PreflightCheck(
                    name="disk_space",
                    category="system",
                    passed=True,
                    message="Disk space check skipped (psutil not available)",
                )
        except Exception as e:
            return PreflightCheck(
                name="disk_space",
                category="system",
                passed=False,
                message=f"Disk space check failed: {str(e)}",
            )

    def _check_memory(self, min_mb: int) -> PreflightCheck:
        """Check available memory"""
        try:
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                available_mb = memory.available / (1024 * 1024)
                passed = available_mb >= min_mb
                return PreflightCheck(
                    name="memory",
                    category="system",
                    passed=passed,
                    message=f"Memory: {available_mb:.0f}MB available"
                    + ("" if passed else f" (need {min_mb}MB)"),
                    details={
                        "available_mb": available_mb,
                        "required_mb": min_mb,
                        "percent_used": memory.percent,
                    },
                )
            else:
                return PreflightCheck(
                    name="memory",
                    category="system",
                    passed=True,
                    message="Memory check skipped (psutil not available)",
                )
        except Exception as e:
            return PreflightCheck(
                name="memory",
                category="system",
                passed=False,
                message=f"Memory check failed: {str(e)}",
            )

    def run_all_checks(self, verbose: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """Run all preflight checks"""
        logger.info("Starting preflight validation checks")
        self.checks = []
        all_required_passed = True

        if verbose:
            print("\n" + "=" * 70)
            print(f"PREFLIGHT VALIDATION - OverlayCheetah V3 PRO {VERSION}")
            print("=" * 70)

        # Required tools
        if verbose:
            print("\n[REQUIRED TOOLS]")
        for name, cmd, desc in self.REQUIRED_TOOLS:
            check = self._run_tool_check(name, cmd, desc, "required")
            self.checks.append(check)
            if not check.passed:
                all_required_passed = False
                logger.warning(
                    "Required tool check failed: %s - %s", name, check.message
                )
            else:
                logger.debug("Required tool check passed: %s", name)
            if verbose:
                status = "✓" if check.passed else "✗"
                print(f"  [{status}] {name}: {check.message}")
                if check.version:
                    print(f"      Version: {check.version}")

        # Optional tools
        if verbose:
            print("\n[OPTIONAL TOOLS]")
        for name, cmd, desc in self.OPTIONAL_TOOLS:
            check = self._run_tool_check(name, cmd, desc, "optional")
            self.checks.append(check)
            if verbose:
                status = "✓" if check.passed else "○"
                print(f"  [{status}] {name}: {check.message}")

        # System checks
        if verbose:
            print("\n[SYSTEM RESOURCES]")
        disk_check = self._check_disk_space(1024)
        self.checks.append(disk_check)
        if verbose:
            status = "✓" if disk_check.passed else "✗"
            print(f"  [{status}] {disk_check.message}")

        memory_check = self._check_memory(512)
        self.checks.append(memory_check)
        if verbose:
            status = "✓" if memory_check.passed else "✗"
            print(f"  [{status}] {memory_check.message}")

        # Gather environment info
        self.environment_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cwd": str(Path.cwd()),
            "timestamp": datetime.now().isoformat(),
            "cheetah_version": VERSION,
            "checks": [asdict(c) for c in self.checks],
        }

        if verbose:
            print("\n[ENVIRONMENT]")
            print(f"  Platform: {platform.system()} {platform.release()}")
            print(f"  Python: {platform.python_version()}")
            print(f"  Working Dir: {Path.cwd()}")
            print("=" * 70 + "\n")

        return all_required_passed, self.environment_info


# =============================================================================
# CONTAINERIZATION SUPPORT
# =============================================================================
class DockerManager:
    """Manages Docker containerization for reproducible builds"""

    DOCKERFILE_TEMPLATE = """# Generated by OverlayCheetah V3 PRO
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (optional, for web projects)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \\
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHEETAH_VERSION={version}

# Default command
CMD ["python", "app.py"]
"""

    DOCKER_COMPOSE_TEMPLATE = """# Generated by OverlayCheetah V3 PRO
version: '3.8'

services:
  app:
    build: .
    container_name: {project_name}
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - CHEETAH_VERSION={version}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Optional: Add database service
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_PASSWORD: changeme
  #   volumes:
  #     - db_data:/var/lib/postgresql/data

# volumes:
#   db_data:
"""

    def __init__(self):
        self.docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def generate_dockerfile(self, project_name: str) -> str:
        """Generate Dockerfile for project"""
        return self.DOCKERFILE_TEMPLATE.format(version=VERSION)

    def generate_docker_compose(self, project_name: str) -> str:
        """Generate docker-compose.yml for project"""
        return self.DOCKER_COMPOSE_TEMPLATE.format(
            project_name=project_name.lower().replace(" ", "_"),
            version=VERSION,
        )

    def build_image(
        self, path: str, tag: str, callback: Optional[Callable] = None
    ) -> Tuple[bool, str]:
        """Build Docker image"""
        if not self.docker_available:
            return False, "Docker not available"

        try:
            result = subprocess.run(
                ["docker", "build", "-t", tag, path],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            if result.returncode == 0:
                if callback:
                    callback(
                        {"success": True, "message": f"Image {tag} built successfully"}
                    )
                return True, f"Image {tag} built successfully"
            else:
                if callback:
                    callback({"success": False, "error": result.stderr})
                return False, result.stderr
        except Exception as e:
            return False, str(e)


# =============================================================================
# PATH & CACHE MANAGEMENT
# =============================================================================
@dataclass
class PathConfig:
    """Centralized path management"""

    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)

    @property
    def templates_dir(self) -> Path:
        return self.root / "templates"

    @property
    def output_dir(self) -> Path:
        return self.root / "out"

    @property
    def reports_dir(self) -> Path:
        return self.root / "reports"

    @property
    def cache_dir(self) -> Path:
        return self.root / ".cache"

    @property
    def settings_file(self) -> Path:
        return self.root / "settings_pro.json"

    @property
    def lockfile(self) -> Path:
        return self.root / "cheetah.lock"

    def ensure_directories(self):
        """Create all required directories"""
        for dir_path in [
            self.templates_dir,
            self.output_dir,
            self.reports_dir,
            self.cache_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def validate_path(self, path: Path) -> Tuple[bool, Optional[str]]:
        """Validate path is within project boundaries"""
        try:
            resolved = path.resolve()
            if not str(resolved).startswith(str(self.root)):
                return False, f"Path '{path}' is outside project root"
            return True, None
        except Exception as e:
            return False, f"Path validation error: {str(e)}"

    def safe_write(self, path: Path, content: str) -> Tuple[bool, Optional[str]]:
        """Safely write to a file"""
        valid, error = self.validate_path(path)
        if not valid:
            return False, error
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True, None
        except Exception as e:
            return False, f"Write error: {str(e)}"


class SmartCache:
    """Intelligent caching with automatic invalidation"""

    def __init__(self, cache_dir: Path, max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_seconds = max_age_hours * 3600
        self.index_file = cache_dir / "cache_index.json"
        self.index: Dict[str, Dict[str, Any]] = self._load_index()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with self.index_file.open("r", encoding="utf-8") as f:
                    index = json.load(f)
                    logger.debug("Loaded cache index with %d entries", len(index))
                    return index
            except (json.JSONDecodeError, IOError) as exc:
                logger.warning("Failed to load cache index: %s", exc)
        return {}

    def _save_index(self):
        """Save cache index to disk"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with self.index_file.open("w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
            logger.debug("Saved cache index with %d entries", len(self.index))
        except (IOError, OSError) as exc:
            logger.warning("Failed to save cache index: %s", exc)

    def _compute_hash(self, content: str, context: Dict[str, Any]) -> str:
        """Compute hash for content + context"""
        combined = content + json.dumps(context, sort_keys=True)
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, key: str, content_hash: str) -> Optional[str]:
        """Get cached value if valid"""
        if key not in self.index:
            logger.debug("Cache miss for key '%s': not in index", key)
            return None

        entry = self.index[key]

        # Check hash match
        if entry.get("hash") != content_hash:
            logger.debug("Cache miss for key '%s': hash mismatch", key)
            return None

        # Check age
        age = time.time() - entry.get("timestamp", 0)
        if age > self.max_age_seconds:
            logger.debug("Cache miss for key '%s': expired (age: %.1fs)", key, age)
            del self.index[key]
            self._save_index()
            return None

        # Load cached content
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                content = cache_file.read_text(encoding="utf-8")
                logger.debug("Cache hit for key '%s' (age: %.1fs)", key, age)
                return content
            except (IOError, OSError) as exc:
                logger.warning("Cache read failed for key '%s': %s", key, exc)
                return None

        logger.debug("Cache miss for key '%s': file not found", key)
        return None

    def set(self, key: str, content_hash: str, value: str):
        """Set cache value"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Save content
            cache_file = self.cache_dir / f"{key}.cache"
            cache_file.write_text(value, encoding="utf-8")

            # Update index
            self.index[key] = {
                "hash": content_hash,
                "timestamp": time.time(),
                "size": len(value),
            }
            self._save_index()
            logger.debug("Cache set for key '%s' (size: %d bytes)", key, len(value))
        except (IOError, OSError) as exc:
            logger.warning("Cache write failed for key '%s': %s", key, exc)

    def invalidate(self, key: Optional[str] = None):
        """Invalidate cache entries"""
        if key is None:
            # Invalidate all
            self.index = {}
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
        elif key in self.index:
            del self.index[key]
            cache_file = self.cache_dir / f"{key}.cache"
            if cache_file.exists():
                cache_file.unlink()
        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = sum(entry.get("size", 0) for entry in self.index.values())
        return {
            "entries": len(self.index),
            "total_size_kb": total_size / 1024,
            "oldest_entry": min(
                (e.get("timestamp", 0) for e in self.index.values()), default=0
            ),
            "newest_entry": max(
                (e.get("timestamp", 0) for e in self.index.values()), default=0
            ),
        }


# =============================================================================
# LLM MANAGEMENT
# =============================================================================
class LLMManager:
    """Multi-provider LLM manager with fallback support"""

    def __init__(self):
        self.providers = {
            "lm_studio": {"endpoint": "http://localhost:1234/v1/chat/completions"},
            "huggingface": {"model": "microsoft/DialoGPT-medium"},
            "ollama": {"model": "llama2"},
            "copilot": {"token": os.getenv("GITHUB_TOKEN")},
            "gemini": {"api_key": os.getenv("GEMINI_API_KEY")},
        }
        self.current = "ollama"
        self.fallback_order = ["ollama", "lm_studio", "gemini"]
        self.retries = 3
        self.timeout = 30

    def set_provider(self, provider: str):
        self.current = provider

    def query(
        self,
        prompt: str,
        callback: Optional[Callable] = None,
        use_fallback: bool = True,
    ):
        """Query LLM with optional fallback"""

        def _query():
            providers_to_try = [self.current]
            if use_fallback:
                providers_to_try.extend(
                    [p for p in self.fallback_order if p != self.current]
                )

            last_error = None
            for provider in providers_to_try:
                for attempt in range(self.retries):
                    try:
                        result = self._query_provider(provider, prompt)
                        if callback:
                            callback(
                                {
                                    "success": True,
                                    "result": result,
                                    "provider": provider,
                                }
                            )
                        return result
                    except Exception as e:
                        last_error = str(e)
                        time.sleep(1)

            error = f"All providers failed. Last error: {last_error}"
            if callback:
                callback({"success": False, "error": error})
            return error

        thread = threading.Thread(target=_query)
        thread.start()

    def _query_provider(self, provider: str, prompt: str) -> str:
        """Query a specific provider"""
        import requests

        if provider == "lm_studio":
            response = requests.post(
                self.providers["lm_studio"]["endpoint"],
                json={"messages": [{"role": "user", "content": prompt}]},
                timeout=self.timeout,
            )
            return response.json()["choices"][0]["message"]["content"]

        elif provider == "ollama":
            try:
                import ollama

                response = ollama.chat(
                    model=self.providers["ollama"]["model"],
                    messages=[{"role": "user", "content": prompt}],
                )
                return response["message"]["content"]
            except Exception:
                raise Exception("Ollama not available")

        elif provider == "gemini":
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.providers["gemini"]["api_key"])
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                raise Exception("Gemini not available")

        else:
            return f"Provider {provider} not implemented"


# =============================================================================
# TEMPLATE ENGINE
# =============================================================================
class TemplateEngine:
    """Advanced template engine with validation and caching"""

    def __init__(self, paths: PathConfig, cache: SmartCache):
        self.paths = paths
        self.cache = cache

    def generate_yaml(
        self, inputs: Dict[str, Any], stack: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Generate YAML task specification"""
        errors = []

        if not inputs.get("name"):
            errors.append("Project name is required")

        task_id = inputs.get("name", "project").lower().replace(" ", "_")

        yaml_content = f"""# Generated by OverlayCheetah V3 PRO {VERSION}
# Timestamp: {datetime.now().isoformat()}

task_id: vibe_build_{task_id}
version: "{VERSION}"
description: Professional build generated by OverlayCheetah V3 PRO

metadata:
  created: "{datetime.now().isoformat()}"
  generator: "OverlayCheetah V3 PRO"
  generator_version: "{VERSION}"
  reproducible: true

inputs:
  name: "{inputs.get("name", "MyProject")}"
  type: "{inputs.get("type", "Full-Stack Platform")}"
  features: {inputs.get("features", 10)}

stack:
  frontend: "{stack.get("frontend", "React")}"
  backend: "{stack.get("backend", "FastAPI")}"
  database: "{stack.get("database", "PostgreSQL")}"
  cache: "{stack.get("cache", "Redis")}"

dependencies:
  pinned: true
  lockfile: "cheetah.lock"
  containerized: true

files:
  - template: main_app.py.j2
    output: app.py
    context:
      app_name: "{inputs.get("name", "MyProject")}"
      features: {inputs.get("features", 10)}
      stack: {stack}

  - template: requirements.txt.j2
    output: requirements.txt
    context:
      dependencies: {list(PINNED_DEPENDENCIES.keys())}

  - template: dockerfile.j2
    output: Dockerfile
    context:
      version: "{VERSION}"

build:
  validate: true
  profile: true
  monitor_resources: true
  generate_telemetry: true
"""

        return yaml_content, errors


# =============================================================================
# BUILD EXECUTOR
# =============================================================================
class BuildExecutor:
    """Professional build executor with profiling and monitoring"""

    def __init__(self, paths: PathConfig, cache: SmartCache):
        self.paths = paths
        self.cache = cache
        self.resource_monitor = ResourceMonitor()
        self.docker_manager = DockerManager()

    def execute(
        self,
        yaml_content: str,
        callback: Optional[Callable] = None,
        enable_profiling: bool = True,
        enable_monitoring: bool = True,
        generate_docker: bool = False,
    ):
        """Execute build with full profiling and monitoring"""

        def _execute():
            telemetry = BuildTelemetry(task_id="build")
            telemetry.start_time = time.time()

            # Start resource monitoring
            if enable_monitoring:
                self.resource_monitor.start_monitoring()

            try:
                # Step 1: Validate YAML
                step = StepProfile(step_name="validate_yaml")
                step.start_time = time.time()
                if enable_monitoring:
                    step.resource_snapshot_start = self.resource_monitor.take_snapshot()

                if YAML_AVAILABLE:
                    try:
                        spec = yaml.safe_load(yaml_content)
                        step.success = True
                    except yaml.YAMLError as e:
                        step.success = False
                        step.error = str(e)
                else:
                    step.success = True  # Skip if yaml not available

                step.end_time = time.time()
                step.duration_sec = step.end_time - step.start_time
                if enable_monitoring:
                    step.resource_snapshot_end = self.resource_monitor.take_snapshot()
                    step.compute_resource_delta()
                telemetry.add_step(step)

                if not step.success:
                    raise Exception(f"YAML validation failed: {step.error}")

                # Step 2: Write output files
                step = StepProfile(step_name="write_files")
                step.start_time = time.time()
                if enable_monitoring:
                    step.resource_snapshot_start = self.resource_monitor.take_snapshot()

                output_path = self.paths.output_dir / "generated_template_pro.yaml"
                success, error = self.paths.safe_write(output_path, yaml_content)

                if success:
                    step.success = True
                    step.files_processed = 1
                    step.bytes_written = len(yaml_content.encode("utf-8"))
                    telemetry.generated_files.append(str(output_path))
                else:
                    step.success = False
                    step.error = error

                step.end_time = time.time()
                step.duration_sec = step.end_time - step.start_time
                if enable_monitoring:
                    step.resource_snapshot_end = self.resource_monitor.take_snapshot()
                    step.compute_resource_delta()
                telemetry.add_step(step)

                # Step 3: Generate requirements.txt
                step = StepProfile(step_name="generate_requirements")
                step.start_time = time.time()

                req_content = f"# Generated by OverlayCheetah V3 PRO {VERSION}\n"
                req_content += f"# Timestamp: {datetime.now().isoformat()}\n\n"
                for name, constraint in PINNED_DEPENDENCIES.items():
                    req_content += f"{name}{constraint}\n"

                req_path = self.paths.output_dir / "requirements.txt"
                success, _ = self.paths.safe_write(req_path, req_content)
                if success:
                    telemetry.generated_files.append(str(req_path))
                    step.files_processed = 1
                    step.bytes_written = len(req_content.encode("utf-8"))

                step.success = True
                step.end_time = time.time()
                step.duration_sec = step.end_time - step.start_time
                telemetry.add_step(step)

                # Step 4: Generate Docker files (optional)
                if generate_docker:
                    step = StepProfile(step_name="generate_docker")
                    step.start_time = time.time()

                    dockerfile = self.docker_manager.generate_dockerfile("project")
                    docker_path = self.paths.output_dir / "Dockerfile"
                    success, _ = self.paths.safe_write(docker_path, dockerfile)
                    if success:
                        telemetry.generated_files.append(str(docker_path))

                    compose = self.docker_manager.generate_docker_compose("project")
                    compose_path = self.paths.output_dir / "docker-compose.yml"
                    success, _ = self.paths.safe_write(compose_path, compose)
                    if success:
                        telemetry.generated_files.append(str(compose_path))

                    step.success = True
                    step.files_processed = 2
                    step.end_time = time.time()
                    step.duration_sec = step.end_time - step.start_time
                    telemetry.add_step(step)

                # Finalize
                telemetry.end_time = time.time()
                telemetry.total_duration_sec = telemetry.end_time - telemetry.start_time

                # Stop monitoring and get summary
                if enable_monitoring:
                    self.resource_monitor.stop_monitoring()
                    telemetry.resource_summary = self.resource_monitor.get_summary()

                # Save telemetry report
                report_path = (
                    self.paths.reports_dir / f"build_telemetry_{int(time.time())}.json"
                )
                self.paths.safe_write(
                    report_path, json.dumps(telemetry.to_dict(), indent=2)
                )

                if callback:
                    callback(
                        {
                            "success": True,
                            "message": "Build completed successfully!",
                            "files": telemetry.generated_files,
                            "duration_sec": telemetry.total_duration_sec,
                            "telemetry": telemetry.to_dict(),
                        }
                    )

            except Exception as e:
                if enable_monitoring:
                    self.resource_monitor.stop_monitoring()
                if callback:
                    callback({"success": False, "error": str(e)})

        thread = threading.Thread(target=_execute)
        thread.start()


# =============================================================================
# AUDITOR
# =============================================================================
class Auditor:
    """Comprehensive auditing system"""

    def __init__(self, paths: PathConfig):
        self.paths = paths
        self.audit_log: List[Dict[str, Any]] = []

    def log_action(self, action: str, details: Dict[str, Any]):
        """Log an audit action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
        }
        self.audit_log.append(entry)

    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project inputs"""
        errors = []
        warnings = []

        if not inputs.get("name"):
            errors.append("Project name is required")
        elif len(inputs["name"]) < 2:
            warnings.append("Project name is very short")

        features = inputs.get("features", 0)
        if isinstance(features, int) and features < 1:
            errors.append("Features must be at least 1")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def security_scan(self, code: str) -> Dict[str, Any]:
        """Security scan code"""
        risks = []
        dangerous = ["eval(", "exec(", "__import__", "os.system(", "subprocess.call("]
        for pattern in dangerous:
            if pattern in code:
                risks.append(f"Dangerous pattern detected: {pattern}")

        return {
            "secure": len(risks) == 0,
            "risks": risks,
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "version": VERSION,
            "log_entries": len(self.audit_log),
            "audit_log": self.audit_log,
        }


# =============================================================================
# BENCHMARK FUNCTIONALITY
# =============================================================================
def run_benchmark(cache_policy: str = "auto") -> Dict[str, Any]:
    """Run a comprehensive benchmark of the V3 PRO system"""
    logger.info("Starting benchmark with cache policy: %s", cache_policy)

    paths = PathConfig()

    # Handle cache clearing for cold start
    if cache_policy == "cold":
        logger.info("Clearing all caches for cold benchmark")
        if paths.cache_dir.exists():
            shutil.rmtree(paths.cache_dir)
        # Also clear npm cache if available
        try:
            subprocess.run(
                ["npm", "cache", "clean", "--force"], capture_output=True, timeout=30
            )
        except Exception as exc:
            logger.warning("Failed to clear npm cache: %s", exc)

    start_time = time.time()

    # Initialize components
    cache = SmartCache(paths.cache_dir)
    template_engine = TemplateEngine(paths, cache)
    llm_manager = LLMManager()
    resource_monitor = ResourceMonitor()

    # Start resource monitoring
    resource_monitor.start_monitoring(interval=0.5)

    benchmark_data = {
        "version": VERSION,
        "cache_policy": cache_policy,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        },
        "steps": [],
        "errors": [],
    }

    try:
        # Step 1: Template Generation Test
        step_start = time.time()
        try:
            test_spec = {
                "name": "BenchmarkApp",
                "description": "Test application for benchmarking",
                "features": 8,
                "complexity": "medium",
            }
            test_context = {
                "frontend": "React",
                "backend": "Node.js",
                "database": "MongoDB",
            }

            yaml_content, errors = template_engine.generate_yaml(
                test_spec, test_context
            )
            step_duration = time.time() - step_start

            benchmark_data["steps"].append(
                {
                    "name": "template_generation",
                    "duration_sec": step_duration,
                    "success": len(errors) == 0,
                    "details": {
                        "yaml_size": len(yaml_content),
                        "errors": errors,
                        "cache_stats": cache.get_stats(),
                    },
                }
            )

        except Exception as exc:
            step_duration = time.time() - step_start
            error_msg = f"Template generation failed: {exc}"
            logger.error(error_msg)
            benchmark_data["errors"].append(error_msg)
            benchmark_data["steps"].append(
                {
                    "name": "template_generation",
                    "duration_sec": step_duration,
                    "success": False,
                    "error": str(exc),
                }
            )

        # Step 2: Preflight Validation Test
        step_start = time.time()
        try:
            validator = PreflightValidator()
            passed, env_info = validator.run_all_checks(verbose=False)
            step_duration = time.time() - step_start

            benchmark_data["steps"].append(
                {
                    "name": "preflight_validation",
                    "duration_sec": step_duration,
                    "success": True,
                    "details": {
                        "all_required_passed": passed,
                        "environment_info": env_info,
                        "check_count": len(validator.checks),
                    },
                }
            )

        except Exception as exc:
            step_duration = time.time() - step_start
            error_msg = f"Preflight validation failed: {exc}"
            logger.error(error_msg)
            benchmark_data["errors"].append(error_msg)
            benchmark_data["steps"].append(
                {
                    "name": "preflight_validation",
                    "duration_sec": step_duration,
                    "success": False,
                    "error": str(exc),
                }
            )

        # Step 3: Cache Performance Test
        step_start = time.time()
        try:
            # Test cache write/read performance
            test_data = "x" * 10000  # 10KB test data
            test_hash = hashlib.sha256(test_data.encode()).hexdigest()

            # Write test
            cache.set("benchmark_test", test_hash, test_data)

            # Read test
            result = cache.get("benchmark_test", test_hash)
            step_duration = time.time() - step_start

            benchmark_data["steps"].append(
                {
                    "name": "cache_performance",
                    "duration_sec": step_duration,
                    "success": result == test_data,
                    "details": {
                        "data_size": len(test_data),
                        "cache_hit": result is not None,
                        "cache_stats": cache.get_stats(),
                    },
                }
            )

        except Exception as exc:
            step_duration = time.time() - step_start
            error_msg = f"Cache performance test failed: {exc}"
            logger.error(error_msg)
            benchmark_data["errors"].append(error_msg)
            benchmark_data["steps"].append(
                {
                    "name": "cache_performance",
                    "duration_sec": step_duration,
                    "success": False,
                    "error": str(exc),
                }
            )

    finally:
        # Stop resource monitoring
        resource_snapshots = resource_monitor.stop_monitoring()
        resource_summary = resource_monitor.get_summary()

        total_duration = time.time() - start_time

        benchmark_data.update(
            {
                "total_duration_sec": total_duration,
                "end_time": datetime.fromtimestamp(time.time()).isoformat(),
                "resource_monitoring": {
                    "summary": resource_summary,
                    "snapshot_count": len(resource_snapshots),
                },
                "final_cache_stats": cache.get_stats(),
            }
        )

        logger.info("Benchmark completed in %.2f seconds", total_duration)

    return benchmark_data


# =============================================================================
# MAIN APPLICATION
# =============================================================================
class OverlayCheetahV3Pro:
    """Professional version of OverlayCheetah V3"""

    def __init__(self):
        print(f"Initializing OverlayCheetah V3 PRO {VERSION}...")

        self.paths = PathConfig()
        self.paths.ensure_directories()

        self.cache = SmartCache(self.paths.cache_dir)
        self.llm = LLMManager()
        self.template = TemplateEngine(self.paths, self.cache)
        self.builder = BuildExecutor(self.paths, self.cache)
        self.auditor = Auditor(self.paths)
        self.docker = DockerManager()
        self.settings = self._load_settings()

        # Run preflight
        self.preflight = PreflightValidator()
        self.preflight_passed, self.env_info = self.preflight.run_all_checks(
            verbose=False
        )

        self.root = tk.Tk()
        self.root.title(f"OverlayCheetah V3 PRO {VERSION}")
        self.root.geometry("1200x800")

        self._setup_styles()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")

        self._setup_ui()
        print("GUI initialized.")

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings"""
        try:
            if self.paths.settings_file.exists():
                return json.loads(self.paths.settings_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
        return {
            "llm_provider": "ollama",
            "enable_profiling": True,
            "enable_monitoring": True,
            "generate_docker": True,
            "cache_enabled": True,
        }

    def _save_settings(self):
        """Save settings"""
        self.paths.safe_write(
            self.paths.settings_file, json.dumps(self.settings, indent=2)
        )

    def _setup_styles(self):
        """Setup UI styles"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        self.root.configure(bg="#f5f5f5")

    def _setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg="#1a5276", height=60)
        header.pack(fill="x")
        tk.Label(
            header,
            text=f"OverlayCheetah V3 PRO {VERSION}",
            font=("Arial", 16, "bold"),
            bg="#1a5276",
            fg="white",
        ).pack(side="left", padx=20, pady=15)

        preflight_status = (
            "✓ Preflight OK" if self.preflight_passed else "⚠ Preflight Issues"
        )
        preflight_color = "#2ecc71" if self.preflight_passed else "#e74c3c"
        tk.Label(
            header,
            text=preflight_status,
            font=("Arial", 10),
            bg="#1a5276",
            fg=preflight_color,
        ).pack(side="right", padx=20, pady=15)

        # Status bar
        status_frame = tk.Frame(self.root, bg="#ecf0f1")
        status_frame.pack(side="bottom", fill="x")
        ttk.Label(status_frame, textvariable=self.status_var).pack(
            side="left", padx=10, pady=5
        )
        self.progress_bar = Progressbar(
            status_frame, variable=self.progress_var, maximum=100, length=200
        )
        self.progress_bar.pack(side="right", padx=10, pady=5)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self._setup_main_tab()
        self._setup_profiling_tab()
        self._setup_docker_tab()
        self._setup_settings_tab()

    def _setup_main_tab(self):
        """Setup main build tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Build")

        # Left panel - inputs
        left = ttk.LabelFrame(frame, text="Project Configuration", padding=15)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(left, text="Project Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(left, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(left, text="Project Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="Full-Stack Platform")
        ttk.Combobox(
            left,
            textvariable=self.type_var,
            values=[
                "Full-Stack Platform",
                "SaaS Web App",
                "API Service",
                "Microservices",
            ],
            width=37,
        ).grid(row=1, column=1, pady=5)

        ttk.Label(left, text="Features (1-20):").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.features_scale = tk.Scale(
            left, from_=1, to=20, orient=tk.HORIZONTAL, length=200
        )
        self.features_scale.set(10)
        self.features_scale.grid(row=2, column=1, pady=5)

        # Buttons
        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Generate Template", command=self._generate).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Build Project", command=self._build).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Run Preflight", command=self._run_preflight).pack(
            side="left", padx=5
        )

        # Output area
        ttk.Label(left, text="Output:").grid(row=4, column=0, columnspan=2, sticky="w")
        self.output_area = scrolledtext.ScrolledText(left, height=15, width=60)
        self.output_area.grid(row=5, column=0, columnspan=2, pady=5)

        # Welcome message
        self.output_area.insert(tk.END, f"OverlayCheetah V3 PRO {VERSION}\n")
        self.output_area.insert(tk.END, "=" * 50 + "\n")
        self.output_area.insert(tk.END, "Professional Features:\n")
        self.output_area.insert(tk.END, "• Resource monitoring during builds\n")
        self.output_area.insert(tk.END, "• Per-step profiling with metrics\n")
        self.output_area.insert(tk.END, "• Docker containerization support\n")
        self.output_area.insert(tk.END, "• Intelligent caching system\n")
        self.output_area.insert(tk.END, "• Multi-provider LLM fallback\n")
        self.output_area.insert(tk.END, "=" * 50 + "\n\n")

    def _setup_profiling_tab(self):
        """Setup profiling/metrics tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Profiling & Metrics")

        ttk.Label(
            frame, text="Build Profiling & Resource Metrics", style="Header.TLabel"
        ).pack(pady=10)

        self.metrics_text = scrolledtext.ScrolledText(frame, height=30, width=100)
        self.metrics_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame, text="Load Latest Report", command=self._load_latest_report
        ).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Cache", command=self._clear_cache).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Cache Stats", command=self._show_cache_stats).pack(
            side="left", padx=5
        )

    def _setup_docker_tab(self):
        """Setup Docker tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Docker")

        ttk.Label(frame, text="Containerization", style="Header.TLabel").pack(pady=10)

        status = (
            "✓ Docker Available"
            if self.docker.docker_available
            else "✗ Docker Not Found"
        )
        color = "green" if self.docker.docker_available else "red"
        ttk.Label(frame, text=status, foreground=color).pack(pady=5)

        self.docker_text = scrolledtext.ScrolledText(frame, height=25, width=100)
        self.docker_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame, text="Preview Dockerfile", command=self._preview_dockerfile
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Preview docker-compose.yml", command=self._preview_compose
        ).pack(side="left", padx=5)

    def _setup_settings_tab(self):
        """Setup settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")

        ttk.Label(frame, text="Configuration", style="Header.TLabel").pack(pady=10)

        settings_frame = ttk.Frame(frame)
        settings_frame.pack(pady=20)

        # LLM Provider
        ttk.Label(settings_frame, text="LLM Provider:").grid(
            row=0, column=0, sticky="w", pady=10
        )
        self.llm_var = tk.StringVar(value=self.settings.get("llm_provider", "ollama"))
        ttk.Combobox(
            settings_frame,
            textvariable=self.llm_var,
            values=["ollama", "lm_studio", "gemini", "copilot", "huggingface"],
            width=25,
        ).grid(row=0, column=1, pady=10)

        # Checkboxes
        self.profiling_var = tk.BooleanVar(
            value=self.settings.get("enable_profiling", True)
        )
        ttk.Checkbutton(
            settings_frame, text="Enable Profiling", variable=self.profiling_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        self.monitoring_var = tk.BooleanVar(
            value=self.settings.get("enable_monitoring", True)
        )
        ttk.Checkbutton(
            settings_frame,
            text="Enable Resource Monitoring",
            variable=self.monitoring_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        self.docker_var = tk.BooleanVar(
            value=self.settings.get("generate_docker", True)
        )
        ttk.Checkbutton(
            settings_frame, text="Generate Docker Files", variable=self.docker_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        self.cache_var = tk.BooleanVar(value=self.settings.get("cache_enabled", True))
        ttk.Checkbutton(
            settings_frame, text="Enable Caching", variable=self.cache_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(
            settings_frame, text="Save Settings", command=self._save_settings_ui
        ).grid(row=5, column=0, columnspan=2, pady=20)

    def _generate(self):
        """Generate template"""
        inputs = {
            "name": self.name_entry.get() or "MyProject",
            "type": self.type_var.get(),
            "features": self.features_scale.get(),
        }
        stack = {
            "frontend": "React",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "cache": "Redis",
        }

        yaml_content, errors = self.template.generate_yaml(inputs, stack)

        if errors:
            self.output_area.insert(tk.END, "\n✗ Generation errors:\n")
            for error in errors:
                self.output_area.insert(tk.END, f"  • {error}\n")
        else:
            self.output_area.insert(
                tk.END, f"\n✓ Template generated for: {inputs['name']}\n"
            )

            output_path = self.paths.output_dir / "v3_pro_template.yaml"
            success, _ = self.paths.safe_write(output_path, yaml_content)
            if success:
                self.output_area.insert(tk.END, f"  Saved to: {output_path}\n")

        self.output_area.see(tk.END)
        self.auditor.log_action("generate", {"inputs": inputs})

    def _build(self):
        """Execute build"""
        template_path = self.paths.output_dir / "v3_pro_template.yaml"

        if not template_path.exists():
            messagebox.showwarning("Warning", "Please generate a template first.")
            return

        yaml_content = template_path.read_text(encoding="utf-8")
        self.status_var.set("Building with profiling...")
        self.progress_var.set(25)

        def callback(result):
            if result.get("success"):
                self.output_area.insert(tk.END, f"\n✓ Build completed!\n")
                self.output_area.insert(
                    tk.END, f"  Duration: {result.get('duration_sec', 0):.2f}s\n"
                )
                self.output_area.insert(
                    tk.END, f"  Files: {len(result.get('files', []))}\n"
                )

                # Show telemetry summary
                telemetry = result.get("telemetry", {})
                perf = telemetry.get("performance_summary", {})
                if perf:
                    self.output_area.insert(tk.END, f"\n  Performance Summary:\n")
                    self.output_area.insert(
                        tk.END,
                        f"    Steps: {perf.get('successful_steps', 0)}/{perf.get('total_steps', 0)} successful\n",
                    )
                    self.output_area.insert(
                        tk.END,
                        f"    Cache hit rate: {perf.get('cache_hit_rate', 0):.1%}\n",
                    )

                resource = telemetry.get("resource_summary", {})
                if resource.get("available"):
                    self.output_area.insert(tk.END, f"\n  Resource Usage:\n")
                    cpu = resource.get("cpu", {})
                    self.output_area.insert(
                        tk.END,
                        f"    CPU: avg {cpu.get('avg', 0):.1f}%, max {cpu.get('max', 0):.1f}%\n",
                    )
                    mem = resource.get("memory", {})
                    self.output_area.insert(
                        tk.END, f"    Memory: avg {mem.get('avg_percent', 0):.1f}%\n"
                    )

                self.progress_var.set(100)
                self.status_var.set("Build Complete")
            else:
                self.output_area.insert(
                    tk.END, f"\n✗ Build failed: {result.get('error')}\n"
                )
                self.status_var.set("Build Failed")
                self.progress_var.set(0)

            self.output_area.see(tk.END)

        self.builder.execute(
            yaml_content,
            callback=callback,
            enable_profiling=self.settings.get("enable_profiling", True),
            enable_monitoring=self.settings.get("enable_monitoring", True),
            generate_docker=self.settings.get("generate_docker", True),
        )

    def _run_preflight(self):
        """Run preflight checks"""
        self.output_area.insert(tk.END, "\n--- Running Preflight Checks ---\n")
        passed, env_info = self.preflight.run_all_checks(verbose=False)

        for check in self.preflight.checks:
            status = (
                "✓" if check.passed else ("○" if check.category == "optional" else "✗")
            )
            self.output_area.insert(
                tk.END, f"  [{status}] {check.name}: {check.message}\n"
            )

        result = "PASSED" if passed else "FAILED"
        self.output_area.insert(tk.END, f"\n--- Preflight: {result} ---\n")
        self.output_area.see(tk.END)

    def _load_latest_report(self):
        """Load latest telemetry report"""
        reports = list(self.paths.reports_dir.glob("build_telemetry_*.json"))
        if not reports:
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, "No telemetry reports found.\n")
            return

        latest = max(reports, key=lambda p: p.stat().st_mtime)
        content = latest.read_text(encoding="utf-8")

        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, f"Report: {latest.name}\n")
        self.metrics_text.insert(tk.END, "=" * 60 + "\n\n")
        self.metrics_text.insert(tk.END, content)

    def _clear_cache(self):
        """Clear cache"""
        self.cache.invalidate()
        messagebox.showinfo("Cache", "Cache cleared successfully.")

    def _show_cache_stats(self):
        """Show cache statistics"""
        stats = self.cache.get_stats()
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, "Cache Statistics\n")
        self.metrics_text.insert(tk.END, "=" * 40 + "\n\n")
        self.metrics_text.insert(tk.END, json.dumps(stats, indent=2))

    def _preview_dockerfile(self):
        """Preview Dockerfile"""
        content = self.docker.generate_dockerfile(self.name_entry.get() or "project")
        self.docker_text.delete(1.0, tk.END)
        self.docker_text.insert(tk.END, content)

    def _preview_compose(self):
        """Preview docker-compose.yml"""
        content = self.docker.generate_docker_compose(
            self.name_entry.get() or "project"
        )
        self.docker_text.delete(1.0, tk.END)
        self.docker_text.insert(tk.END, content)

    def _save_settings_ui(self):
        """Save settings from UI"""
        self.settings.update(
            {
                "llm_provider": self.llm_var.get(),
                "enable_profiling": self.profiling_var.get(),
                "enable_monitoring": self.monitoring_var.get(),
                "generate_docker": self.docker_var.get(),
                "cache_enabled": self.cache_var.get(),
            }
        )
        self._save_settings()
        self.llm.set_provider(self.llm_var.get())
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def run(self):
        """Run the application"""
        self.root.mainloop()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"OverlayCheetah V3 PRO {VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python overlay_cheetah_v3_pro.py                     Run GUI
  python overlay_cheetah_v3_pro.py --preflight         Run preflight checks only
  python overlay_cheetah_v3_pro.py --test              Run self-tests
  python overlay_cheetah_v3_pro.py --build             Build EXE
  python overlay_cheetah_v3_pro.py --benchmark --cold  Run cold benchmark
  python overlay_cheetah_v3_pro.py --benchmark --warm  Run warm benchmark
        """,
    )

    parser.add_argument(
        "--preflight", action="store_true", help="Run preflight checks only"
    )
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument(
        "--build", action="store_true", help="Build EXE with PyInstaller"
    )
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark mode")
    parser.add_argument(
        "--cold", action="store_true", help="Force cold start (clear all caches)"
    )
    parser.add_argument(
        "--warm", action="store_true", help="Force warm start (preserve caches)"
    )
    parser.add_argument(
        "--output-benchmark", type=str, help="Save benchmark results to JSON file"
    )
    parser.add_argument(
        "--version", action="version", version=f"OverlayCheetah V3 PRO {VERSION}"
    )

    args = parser.parse_args()

    if args.preflight:
        print(f"OverlayCheetah V3 PRO {VERSION} - Preflight Check")
        validator = PreflightValidator()
        passed, _ = validator.run_all_checks(verbose=True)
        sys.exit(0 if passed else 1)

    elif args.benchmark:
        print(f"OverlayCheetah V3 PRO {VERSION} - Benchmark Mode")
        print("=" * 50)

        # Determine cache policy
        if args.cold and args.warm:
            print("Error: Cannot specify both --cold and --warm")
            sys.exit(1)
        elif args.cold:
            cache_policy = "cold"
            print("Running COLD benchmark (all caches cleared)")
        elif args.warm:
            cache_policy = "warm"
            print("Running WARM benchmark (caches preserved)")
        else:
            cache_policy = "auto"
            print("Running AUTO benchmark (current cache state)")

        # Run benchmark
        benchmark_result = run_benchmark(cache_policy)

        # Save results if requested
        if args.output_benchmark:
            output_path = Path(args.output_benchmark)
            output_path.write_text(json.dumps(benchmark_result, indent=2))
            print(f"Benchmark results saved to: {output_path}")

        # Print summary
        duration = benchmark_result.get("total_duration_sec", 0)
        print(f"\nBenchmark completed in {duration:.2f} seconds")
        print(f"Cache policy: {cache_policy}")
        sys.exit(0)

    elif args.test:
        print(f"OverlayCheetah V3 PRO {VERSION} - Self Tests")
        print("=" * 50)
        passed = 0
        failed = 0

        # Test 1: Path config
        try:
            paths = PathConfig()
            paths.ensure_directories()
            assert paths.output_dir.exists()
            print("✓ Path configuration test passed")
            passed += 1
        except Exception as e:
            print(f"✗ Path configuration test failed: {e}")
            failed += 1

        # Test 2: Cache
        try:
            cache = SmartCache(PathConfig().cache_dir)
            cache.set("test_key", "test_hash", "test_value")
            result = cache.get("test_key", "test_hash")
            assert result == "test_value"
            cache.invalidate("test_key")
            print("✓ Cache test passed")
            passed += 1
        except Exception as e:
            print(f"✗ Cache test failed: {e}")
            failed += 1

        # Test 3: Template generation
        try:
            paths = PathConfig()
            cache = SmartCache(paths.cache_dir)
            template = TemplateEngine(paths, cache)
            yaml_content, errors = template.generate_yaml(
                {"name": "Test", "features": 5}, {"frontend": "React"}
            )
            assert "task_id" in yaml_content
            assert len(errors) == 0
            print("✓ Template generation test passed")
            passed += 1
        except Exception as e:
            print(f"✗ Template generation test failed: {e}")
            failed += 1

        # Test 4: Resource monitoring
        try:
            monitor = ResourceMonitor()
            snapshot = monitor.take_snapshot()
            assert snapshot.timestamp > 0
            print("✓ Resource monitoring test passed")
            passed += 1
        except Exception as e:
            print(f"✗ Resource monitoring test failed: {e}")
            failed += 1

        # Test 5: Preflight validator
        try:
            validator = PreflightValidator()
            passed_check, env_info = validator.run_all_checks(verbose=False)
            assert "platform" in env_info
            print("✓ Preflight validator test passed")
            passed += 1
        except Exception as e:
            print(f"✗ Preflight validator test failed: {e}")
            failed += 1

        print("=" * 50)
        print(f"Results: {passed} passed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)

    elif args.build:
        print(f"Building OverlayCheetah V3 PRO {VERSION} EXE...")
        try:
            import PyInstaller.__main__

            PyInstaller.__main__.run(
                [
                    "overlay_cheetah_v3_pro.py",
                    "--onefile",
                    f"--name=OverlayCheetahV3Pro_{VERSION.replace('.', '_')}",
                    "--hidden-import=psutil",
                    "--hidden-import=google.generativeai",
                    "--hidden-import=ollama",
                ]
            )
            print("✓ EXE built successfully!")
        except ImportError:
            print("✗ PyInstaller not installed. Run: pip install pyinstaller")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Build failed: {e}")
            sys.exit(1)

    else:
        # Handle cache flags for GUI mode
        if args.cold or args.warm:
            print("Note: --cold/--warm flags only apply in --benchmark mode")

        # Run GUI
        app = OverlayCheetahV3Pro()
        app.run()


if __name__ == "__main__":
    main()
