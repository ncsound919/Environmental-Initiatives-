"""
Plugin system for extending autocoder functionality
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class PluginInfo:
    """Plugin metadata"""

    name: str
    version: str
    description: str
    author: str
    module_path: str


class Plugin:
    """Base class for autocoder plugins"""

    name: str = "Base Plugin"
    version: str = "1.0.0"
    description: str = "Base plugin class"
    author: str = "Unknown"

    def on_init(self, config: Dict[str, Any]):
        """Called when plugin is initialized

        Args:
            config: Plugin configuration
        """
        pass

    def on_before_generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Called before file generation

        Args:
            task: Task dictionary

        Returns:
            Modified task dictionary
        """
        return task

    def on_after_generate(self, task: Dict[str, Any], output_path: str, success: bool):
        """Called after file generation

        Args:
            task: Task dictionary
            output_path: Path to generated file
            success: Whether generation succeeded
        """
        pass

    def on_template_render(
        self, template_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Called before template rendering

        Args:
            template_name: Name of template
            context: Template context

        Returns:
            Modified context
        """
        return context

    def register_filters(self) -> Dict[str, Callable]:
        """Register custom Jinja2 filters

        Returns:
            Dictionary of filter name to filter function
        """
        return {}

    def register_templates(self) -> Optional[Path]:
        """Register additional template directory

        Returns:
            Path to template directory or None
        """
        return None


class PluginManager:
    """Manages autocoder plugins"""

    def __init__(self, plugins_dir: Path):
        """Initialize plugin manager

        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugins_dir = plugins_dir
        self.plugins: List[Plugin] = []
        self.plugin_info: Dict[str, PluginInfo] = {}

        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py if needed
        init_file = self.plugins_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Plugins directory\n")

    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins

        Returns:
            List of plugin information
        """
        plugins = []

        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                info = self._load_plugin_info(plugin_file)
                if info:
                    plugins.append(info)
                    self.plugin_info[info.name] = info
            except Exception as e:
                print(f"Warning: Failed to load plugin {plugin_file.name}: {e}")

        return plugins

    def _load_plugin_info(self, plugin_file: Path) -> Optional[PluginInfo]:
        """Load plugin metadata without instantiating

        Args:
            plugin_file: Path to plugin file

        Returns:
            Plugin information or None
        """
        module_name = plugin_file.stem
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)

        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find Plugin subclasses
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin:
                return PluginInfo(
                    name=obj.name,
                    version=obj.version,
                    description=obj.description,
                    author=obj.author,
                    module_path=str(plugin_file),
                )

        return None

    def load_plugin(
        self, plugin_name: str, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Load and initialize a plugin

        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration

        Returns:
            True if plugin loaded successfully
        """
        if plugin_name not in self.plugin_info:
            return False

        info = self.plugin_info[plugin_name]

        try:
            # Import module
            spec = importlib.util.spec_from_file_location(plugin_name, info.module_path)

            if not spec or not spec.loader:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find and instantiate Plugin subclass
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugin_instance = obj()
                    plugin_instance.on_init(config or {})
                    self.plugins.append(plugin_instance)
                    return True

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False

        return False

    def load_all_plugins(self, config: Optional[Dict[str, Any]] = None):
        """Load all discovered plugins

        Args:
            config: Configuration for all plugins
        """
        self.discover_plugins()

        for name in self.plugin_info:
            self.load_plugin(name, config)

    def trigger_before_generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger before_generate hooks

        Args:
            task: Task dictionary

        Returns:
            Modified task
        """
        for plugin in self.plugins:
            task = plugin.on_before_generate(task)
        return task

    def trigger_after_generate(
        self, task: Dict[str, Any], output_path: str, success: bool
    ):
        """Trigger after_generate hooks

        Args:
            task: Task dictionary
            output_path: Output file path
            success: Generation success
        """
        for plugin in self.plugins:
            plugin.on_after_generate(task, output_path, success)

    def trigger_template_render(
        self, template_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger template_render hooks

        Args:
            template_name: Template name
            context: Template context

        Returns:
            Modified context
        """
        for plugin in self.plugins:
            context = plugin.on_template_render(template_name, context)
        return context

    def get_all_filters(self) -> Dict[str, Callable]:
        """Get all custom filters from plugins

        Returns:
            Dictionary of filters
        """
        filters = {}

        for plugin in self.plugins:
            plugin_filters = plugin.register_filters()
            filters.update(plugin_filters)

        return filters

    def get_all_template_dirs(self) -> List[Path]:
        """Get all additional template directories

        Returns:
            List of template directory paths
        """
        dirs = []

        for plugin in self.plugins:
            template_dir = plugin.register_templates()
            if template_dir and template_dir.exists():
                dirs.append(template_dir)

        return dirs
