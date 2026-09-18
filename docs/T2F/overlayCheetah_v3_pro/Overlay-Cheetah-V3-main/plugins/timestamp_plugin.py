"""
Example plugin: Timestamp Injector
Adds timestamps to generated files
"""

from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autocoder.core.plugin_manager import Plugin


class TimestampPlugin(Plugin):
    """Plugin that injects timestamps into generated files"""

    name = "Timestamp Injector"
    version = "1.0.0"
    description = "Adds generation timestamps to context"
    author = "Overlay Cheetah Team"

    def on_init(self, config: Dict[str, Any]):
        """Initialize plugin"""
        self.timestamp_format = config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
        self.add_to_context = config.get("add_to_context", True)
        print(f"[Plugin] {self.name} v{self.version} initialized")

    def on_template_render(
        self, template_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add timestamp to template context"""
        if self.add_to_context:
            context["generated_at"] = datetime.now().strftime(self.timestamp_format)
            context["timestamp"] = datetime.now().isoformat()

        return context

    def on_after_generate(self, task: Dict[str, Any], output_path: str, success: bool):
        """Log generation completion"""
        if success:
            print(
                f"[Plugin] Generated {output_path} at {datetime.now().strftime(self.timestamp_format)}"
            )

    def register_filters(self) -> Dict[str, Any]:
        """Register custom Jinja2 filters"""
        return {
            "timestamp": lambda x: datetime.now().strftime(x or self.timestamp_format),
            "now": lambda: datetime.now().isoformat(),
        }
