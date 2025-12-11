"""
AI configuration management.

Provides:
- YAML-based configuration for AI behavior
- Per-task model and parameter settings
- Budget and latency constraints
- Feature toggles
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TaskConfig:
    """Configuration for a specific task."""
    task_type: str
    default_model: str
    temperature: float = 0.3
    max_tokens: int = 2000
    enable_self_critique: bool = True
    enable_multi_llm_routing: bool = True
    budget_limit: Optional[float] = None
    latency_limit_ms: Optional[float] = None
    routing_strategy: str = "balanced"


@dataclass
class AIConfig:
    """Global AI configuration."""
    provider: str = "openai"  # Default provider
    default_model: str = "gpt-4o"
    enable_retry_logic: bool = True
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    enable_self_critique: bool = True
    enable_multi_llm_routing: bool = True
    enable_tool_calling: bool = True
    enable_context_compression: bool = True
    enable_audit_log: bool = True
    enable_cost_tracking: bool = True
    budget_limit_usd: Optional[float] = None
    task_configs: Dict[str, TaskConfig] = None
    
    def __post_init__(self):
        """Initialize task configs if not provided."""
        if self.task_configs is None:
            self.task_configs = self._get_default_task_configs()
    
    def _get_default_task_configs(self) -> Dict[str, TaskConfig]:
        """Get default task configurations."""
        return {
            "performance_analysis": TaskConfig(
                task_type="performance_analysis",
                default_model="gpt-4o",
                temperature=0.3,
                max_tokens=2000,
                enable_self_critique=True,
            ),
            "root_cause_analysis": TaskConfig(
                task_type="root_cause_analysis",
                default_model="claude-3-sonnet",
                temperature=0.3,
                max_tokens=2500,
                enable_self_critique=True,
            ),
            "code_fix": TaskConfig(
                task_type="code_fix",
                default_model="gpt-4-turbo",
                temperature=0.2,
                max_tokens=2000,
                enable_self_critique=True,
            ),
            "security_analysis": TaskConfig(
                task_type="security_analysis",
                default_model="gpt-4-turbo",
                temperature=0.2,
                max_tokens=2500,
                enable_self_critique=True,
            ),
            "refactoring": TaskConfig(
                task_type="refactoring",
                default_model="gpt-4o",
                temperature=0.3,
                max_tokens=2000,
                enable_self_critique=True,
            ),
            "test_generation": TaskConfig(
                task_type="test_generation",
                default_model="gpt-4o",
                temperature=0.3,
                max_tokens=2500,
                enable_self_critique=True,
            ),
            "anomaly_analysis": TaskConfig(
                task_type="anomaly_analysis",
                default_model="claude-3-sonnet",
                temperature=0.3,
                max_tokens=2000,
                enable_self_critique=True,
            ),
            "documentation": TaskConfig(
                task_type="documentation",
                default_model="gpt-4o",
                temperature=0.3,
                max_tokens=2000,
                enable_self_critique=False,
            ),
        }


class ConfigManager:
    """
    Manages AI configuration from YAML files.
    
    Supports:
    - Loading from callflow_ai.yaml
    - Merging with defaults
    - Per-task overrides
    - Environment variable overrides
    """
    
    DEFAULT_CONFIG_FILE = "callflow_ai.yaml"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_file: Path to config file (defaults to callflow_ai.yaml)
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> AIConfig:
        """Load configuration from file."""
        if Path(self.config_file).exists():
            logger.info(f"Loading AI config from {self.config_file}")
            return self._load_from_file()
        else:
            logger.info(f"Config file not found, using defaults")
            return AIConfig()
    
    def _load_from_file(self) -> AIConfig:
        """Load configuration from YAML file."""
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Parse task configs
        task_configs = {}
        if 'tasks' in data:
            for task_name, task_data in data['tasks'].items():
                task_configs[task_name] = TaskConfig(
                    task_type=task_name,
                    **task_data
                )
        
        # Create config
        config_data = {k: v for k, v in data.items() if k != 'tasks'}
        config_data['task_configs'] = task_configs
        
        return AIConfig(**config_data)
    
    def save_config(self, config: AIConfig, file_path: Optional[str] = None):
        """Save configuration to YAML file."""
        file_path = file_path or self.config_file
        
        # Convert to dict
        config_dict = asdict(config)
        
        # Extract task configs
        task_configs = config_dict.pop('task_configs', {})
        tasks_dict = {}
        for task_name, task_config in task_configs.items():
            tasks_dict[task_name] = asdict(task_config)
            tasks_dict[task_name].pop('task_type', None)  # Remove redundant field
        
        config_dict['tasks'] = tasks_dict
        
        # Write to file
        with open(file_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def get_task_config(self, task_type: str) -> TaskConfig:
        """Get configuration for a specific task."""
        return self.config.task_configs.get(
            task_type,
            TaskConfig(task_type=task_type, default_model=self.config.default_model)
        )
    
    def update_task_config(self, task_type: str, **kwargs):
        """Update configuration for a task."""
        if task_type not in self.config.task_configs:
            self.config.task_configs[task_type] = TaskConfig(
                task_type=task_type,
                default_model=self.config.default_model
            )
        
        task_config = self.config.task_configs[task_type]
        for key, value in kwargs.items():
            if hasattr(task_config, key):
                setattr(task_config, key, value)
        
        logger.info(f"Updated config for task: {task_type}")


def create_default_config_file(file_path: str = "callflow_ai.yaml"):
    """Create a default configuration file."""
    config = AIConfig()
    manager = ConfigManager(file_path)
    manager.save_config(config, file_path)
    logger.info(f"Created default config file: {file_path}")
