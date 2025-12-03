"""
Plugin System for CallFlow Tracer

Provides hooks for analyzers, exporters, and UI widgets with entry point support.
"""

import inspect
import importlib
from typing import Dict, List, Any, Optional, Callable, Type, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: str  # "analyzer", "exporter", "ui_widget"
    entry_point: str
    enabled: bool = True
    priority: int = 100  # Lower numbers = higher priority


class PluginHook(ABC):
    """Base class for plugin hooks."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin hook."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the plugin name."""
        pass


class AnalyzerHook(PluginHook):
    """Hook for custom analyzers."""
    
    def __init__(self, name: str, analyzer_func: Callable):
        self._name = name
        self.analyzer_func = analyzer_func
    
    @property
    def name(self) -> str:
        return self._name
    
    def execute(self, graph: Any, **kwargs) -> Dict[str, Any]:
        """Execute the analyzer on a call graph."""
        return self.analyzer_func(graph, **kwargs)


class ExporterHook(PluginHook):
    """Hook for custom exporters."""
    
    def __init__(self, name: str, exporter_func: Callable, 
                 file_extensions: List[str]):
        self._name = name
        self.exporter_func = exporter_func
        self.file_extensions = file_extensions
    
    @property
    def name(self) -> str:
        return self._name
    
    def execute(self, graph: Any, filename: str, **kwargs) -> None:
        """Execute the exporter."""
        return self.exporter_func(graph, filename, **kwargs)


class UIWidgetHook(PluginHook):
    """Hook for custom UI widgets."""
    
    def __init__(self, name: str, widget_config: Dict[str, Any]):
        self._name = name
        self.widget_config = widget_config
    
    @property
    def name(self) -> str:
        return self._name
    
    def execute(self, container_id: str, **kwargs) -> str:
        """Generate HTML/JS for the UI widget."""
        return self._generate_widget_html(container_id, **kwargs)
    
    def _generate_widget_html(self, container_id: str, **kwargs) -> str:
        """Generate HTML for the UI widget."""
        widget_type = self.widget_config.get('type', 'div')
        widget_class = self.widget_config.get('class', 'plugin-widget')
        widget_content = self.widget_config.get('content', '')
        
        html = f'''
        <div id="{container_id}" class="{widget_class}" data-widget="{self._name}">
            <h3>{self._name}</h3>
            {widget_content}
        </div>
        '''
        
        # Add JavaScript if provided
        if 'javascript' in self.widget_config:
            html += f'''
            <script>
                (function() {{
                    {self.widget_config['javascript']}
                }})();
            </script>
            '''
        
        return html


class PluginManager:
    """Manages plugins and hooks."""
    
    def __init__(self):
        self.analyzers: Dict[str, AnalyzerHook] = {}
        self.exporters: Dict[str, ExporterHook] = {}
        self.ui_widgets: Dict[str, UIWidgetHook] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'before_trace': [],
            'after_trace': [],
            'before_export': [],
            'after_export': [],
            'before_analysis': [],
            'after_analysis': []
        }
    
    def register_analyzer(self, name: str, analyzer_func: Callable, 
                          info: Optional[PluginInfo] = None) -> None:
        """Register an analyzer plugin."""
        hook = AnalyzerHook(name, analyzer_func)
        self.analyzers[name] = hook
        
        if info:
            self.plugin_info[name] = info
    
    def register_exporter(self, name: str, exporter_func: Callable,
                         file_extensions: List[str],
                         info: Optional[PluginInfo] = None) -> None:
        """Register an exporter plugin."""
        hook = ExporterHook(name, exporter_func, file_extensions)
        self.exporters[name] = hook
        
        if info:
            self.plugin_info[name] = info
    
    def register_ui_widget(self, name: str, widget_config: Dict[str, Any],
                          info: Optional[PluginInfo] = None) -> None:
        """Register a UI widget plugin."""
        hook = UIWidgetHook(name, widget_config)
        self.ui_widgets[name] = hook
        
        if info:
            self.plugin_info[name] = info
    
    def register_hook(self, hook_point: str, hook_func: Callable) -> None:
        """Register a hook function."""
        if hook_point in self.hooks:
            self.hooks[hook_point].append(hook_func)
    
    def execute_hooks(self, hook_point: str, *args, **kwargs) -> None:
        """Execute all hooks for a given hook point."""
        for hook_func in self.hooks.get(hook_point, []):
            try:
                hook_func(*args, **kwargs)
            except Exception as e:
                print(f"Hook {hook_point} failed: {e}")
    
    def get_analyzer(self, name: str) -> Optional[AnalyzerHook]:
        """Get an analyzer by name."""
        return self.analyzers.get(name)
    
    def get_exporter(self, name: str) -> Optional[ExporterHook]:
        """Get an exporter by name."""
        return self.exporters.get(name)
    
    def get_ui_widget(self, name: str) -> Optional[UIWidgetHook]:
        """Get a UI widget by name."""
        return self.ui_widgets.get(name)
    
    def list_analyzers(self) -> List[str]:
        """List all registered analyzers."""
        return list(self.analyzers.keys())
    
    def list_exporters(self) -> List[str]:
        """List all registered exporters."""
        return list(self.exporters.keys())
    
    def list_ui_widgets(self) -> List[str]:
        """List all registered UI widgets."""
        return list(self.ui_widgets.keys())
    
    def run_analyzer(self, name: str, graph: Any, **kwargs) -> Dict[str, Any]:
        """Run a specific analyzer."""
        analyzer = self.get_analyzer(name)
        if analyzer:
            self.execute_hooks('before_analysis', name, graph)
            try:
                result = analyzer.execute(graph, **kwargs)
                self.execute_hooks('after_analysis', name, graph, result)
                return result
            except Exception as e:
                print(f"Analyzer {name} failed: {e}")
                return {}
        return {}
    
    def run_exporter(self, name: str, graph: Any, filename: str, **kwargs) -> None:
        """Run a specific exporter."""
        exporter = self.get_exporter(name)
        if exporter:
            self.execute_hooks('before_export', name, graph, filename)
            try:
                exporter.execute(graph, filename, **kwargs)
                self.execute_hooks('after_export', name, graph, filename)
            except Exception as e:
                print(f"Exporter {name} failed: {e}")
    
    def generate_ui_widgets(self, container_prefix: str = "plugin_widget_") -> str:
        """Generate HTML for all UI widgets."""
        html_parts = []
        
        for name, widget in self.ui_widgets.items():
            container_id = f"{container_prefix}{name}"
            try:
                widget_html = widget.execute(container_id)
                html_parts.append(widget_html)
            except Exception as e:
                print(f"UI widget {name} failed: {e}")
        
        return '\n'.join(html_parts)
    
    def load_plugins_from_entry_points(self) -> None:
        """Load plugins from entry points."""
        try:
            import importlib.metadata as importlib_metadata
        except ImportError:
            try:
                import importlib_metadata
            except ImportError:
                print("importlib_metadata not available, skipping entry point loading")
                return
        
        # Load analyzer plugins
        try:
            for entry_point in importlib_metadata.entry_points(group='callflow_tracer.analyzers'):
                try:
                    plugin_func = entry_point.load()
                    plugin_info = PluginInfo(
                        name=entry_point.name,
                        version="1.0.0",
                        description=getattr(plugin_func, '__doc__', 'No description'),
                        author=getattr(plugin_func, '__author__', 'Unknown'),
                        plugin_type="analyzer",
                        entry_point=entry_point.value
                    )
                    self.register_analyzer(entry_point.name, plugin_func, plugin_info)
                    print(f"Loaded analyzer plugin: {entry_point.name}")
                except Exception as e:
                    print(f"Failed to load analyzer plugin {entry_point.name}: {e}")
        except Exception:
            pass  # No entry points found
        
        # Load exporter plugins
        try:
            for entry_point in importlib_metadata.entry_points(group='callflow_tracer.exporters'):
                try:
                    plugin_func = entry_point.load()
                    file_extensions = getattr(plugin_func, 'file_extensions', [])
                    plugin_info = PluginInfo(
                        name=entry_point.name,
                        version="1.0.0",
                        description=getattr(plugin_func, '__doc__', 'No description'),
                        author=getattr(plugin_func, '__author__', 'Unknown'),
                        plugin_type="exporter",
                        entry_point=entry_point.value
                    )
                    self.register_exporter(entry_point.name, plugin_func, file_extensions, plugin_info)
                    print(f"Loaded exporter plugin: {entry_point.name}")
                except Exception as e:
                    print(f"Failed to load exporter plugin {entry_point.name}: {e}")
        except Exception:
            pass
        
        # Load UI widget plugins
        try:
            for entry_point in importlib_metadata.entry_points(group='callflow_tracer.ui_widgets'):
                try:
                    widget_config = entry_point.load()
                    plugin_info = PluginInfo(
                        name=entry_point.name,
                        version="1.0.0",
                        description=widget_config.get('description', 'No description'),
                        author=widget_config.get('author', 'Unknown'),
                        plugin_type="ui_widget",
                        entry_point=entry_point.value
                    )
                    self.register_ui_widget(entry_point.name, widget_config, plugin_info)
                    print(f"Loaded UI widget plugin: {entry_point.name}")
                except Exception as e:
                    print(f"Failed to load UI widget plugin {entry_point.name}: {e}")
        except Exception:
            pass
    
    def load_plugins_from_directory(self, plugin_dir: str) -> None:
        """Load plugins from a directory."""
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            return
        
        for plugin_file in plugin_path.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for plugin registration functions
                if hasattr(module, 'register_plugin'):
                    module.register_plugin(self)
                    print(f"Loaded plugin from: {plugin_file}")
            except Exception as e:
                print(f"Failed to load plugin from {plugin_file}: {e}")
    
    def export_plugin_config(self, filename: str) -> None:
        """Export plugin configuration to JSON."""
        config = {
            'analyzers': list(self.analyzers.keys()),
            'exporters': {
                name: hook.file_extensions 
                for name, hook in self.exporters.items()
            },
            'ui_widgets': list(self.ui_widgets.keys()),
            'plugin_info': {
                name: {
                    'name': info.name,
                    'version': info.version,
                    'description': info.description,
                    'author': info.author,
                    'plugin_type': info.plugin_type,
                    'enabled': info.enabled,
                    'priority': info.priority
                }
                for name, info in self.plugin_info.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    def disable_plugin(self, name: str) -> None:
        """Disable a plugin."""
        if name in self.plugin_info:
            self.plugin_info[name].enabled = False
    
    def enable_plugin(self, name: str) -> None:
        """Enable a plugin."""
        if name in self.plugin_info:
            self.plugin_info[name].enabled = True


# Global plugin manager instance
_global_manager = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = PluginManager()
        # Auto-load plugins from entry points
        _global_manager.load_plugins_from_entry_points()
    return _global_manager


def register_analyzer(name: str, 
                     version: str = "1.0.0",
                     description: str = "",
                     author: str = ""):
    """Decorator to register an analyzer plugin."""
    def decorator(func: Callable) -> Callable:
        manager = get_plugin_manager()
        info = PluginInfo(
            name=name,
            version=version,
            description=description or func.__doc__ or "No description",
            author=author or func.__author__ if hasattr(func, '__author__') else "Unknown",
            plugin_type="analyzer",
            entry_point=f"{func.__module__}.{func.__name__}"
        )
        manager.register_analyzer(name, func, info)
        return func
    return decorator


def register_exporter(name: str,
                     file_extensions: List[str],
                     version: str = "1.0.0",
                     description: str = "",
                     author: str = ""):
    """Decorator to register an exporter plugin."""
    def decorator(func: Callable) -> Callable:
        manager = get_plugin_manager()
        info = PluginInfo(
            name=name,
            version=version,
            description=description or func.__doc__ or "No description",
            author=author or func.__author__ if hasattr(func, '__author__') else "Unknown",
            plugin_type="exporter",
            entry_point=f"{func.__module__}.{func.__name__}"
        )
        manager.register_exporter(name, func, file_extensions, info)
        return func
    return decorator


def register_ui_widget(name: str,
                      version: str = "1.0.0",
                      description: str = "",
                      author: str = ""):
    """Decorator to register a UI widget plugin."""
    def decorator(widget_config: Dict[str, Any]) -> Dict[str, Any]:
        manager = get_plugin_manager()
        info = PluginInfo(
            name=name,
            version=version,
            description=description or widget_config.get('description', 'No description'),
            author=author or widget_config.get('author', 'Unknown'),
            plugin_type="ui_widget",
            entry_point=f"{widget_config.get('module', 'unknown')}.{name}"
        )
        manager.register_ui_widget(name, widget_config, info)
        return widget_config
    return decorator


def register_hook(hook_point: str):
    """Decorator to register a hook function."""
    def decorator(func: Callable) -> Callable:
        manager = get_plugin_manager()
        manager.register_hook(hook_point, func)
        return func
    return decorator


# Example built-in plugins
@register_analyzer("complexity_analyzer", description="Analyzes code complexity")
def complexity_analyzer(graph: Any, **kwargs) -> Dict[str, Any]:
    """Built-in complexity analyzer."""
    nodes = list(graph.nodes.values()) if hasattr(graph, 'nodes') else []
    
    total_complexity = sum(
        len(getattr(node, 'children', [])) + len(getattr(node, 'parents', []))
        for node in nodes
    )
    
    return {
        'total_complexity': total_complexity,
        'average_complexity': total_complexity / len(nodes) if nodes else 0,
        'node_count': len(nodes),
        'complexity_distribution': [
            len(getattr(node, 'children', [])) + len(getattr(node, 'parents', []))
            for node in nodes
        ]
    }


@register_exporter("csv_exporter", file_extensions=["csv"], description="Export to CSV format")
def csv_exporter(graph: Any, filename: str, **kwargs) -> None:
    """Export call graph to CSV."""
    import csv
    
    nodes = list(graph.nodes.values()) if hasattr(graph, 'nodes') else []
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function', 'Call Count', 'Total Time', 'Average Time', 'Module'])
        
        for node in nodes:
            writer.writerow([
                getattr(node, 'full_name', 'unknown'),
                getattr(node, 'call_count', 0),
                getattr(node, 'total_time', 0),
                getattr(node, 'avg_time', 0),
                getattr(node, 'module', 'unknown')
            ])


# Register built-in UI widget
performance_summary_config = {
    'type': 'div',
    'class': 'performance-summary-widget',
    'content': '''
    <div class="performance-stats">
        <h4>Performance Summary</h4>
        <div id="perf-total-functions">-</div>
        <div id="perf-total-calls">-</div>
        <div id="perf-total-time">-</div>
        <div id="perf-slowest-function">-</div>
    </div>
    ''',
    'javascript': '''
    // Update performance summary
    function updatePerformanceSummary(data) {
        document.getElementById('perf-total-functions').textContent = 
            `Total Functions: ${data.total_functions || 0}`;
        document.getElementById('perf-total-calls').textContent = 
            `Total Calls: ${data.total_calls || 0}`;
        document.getElementById('perf-total-time').textContent = 
            `Total Time: ${(data.total_time || 0).toFixed(3)}s`;
        document.getElementById('perf-slowest-function').textContent = 
            `Slowest: ${data.slowest_function || 'N/A'}`;
    }
    
    // Auto-update when data is available
    if (window.callflowData) {
        updatePerformanceSummary(window.callflowData);
    }
    ''',
    'description': 'Shows performance summary',
    'author': 'CallFlow Tracer'
}

# Register the widget
get_plugin_manager().register_ui_widget("performance_summary", performance_summary_config)
