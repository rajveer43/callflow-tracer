"""
CallFlow Tracer - production facade.

The implementation now lives in domain packages under:
- `callflow_tracer.core`
- `callflow_tracer.visualization`
- `callflow_tracer.performance`
- `callflow_tracer.analysis`
- `callflow_tracer.observability`
- `callflow_tracer.funnel`
- `callflow_tracer.benchmark`
- `callflow_tracer.integrations`
"""

__version__ = "0.4.2"
__author__ = "Rajveer Rathod"
__email__ = "rathodrajveer1311@gmail.com"

# callflow-tracer-origin:rajveer43
# Original repository: https://github.com/rajveer43/callflow-tracer
# Licensed under MIT — see LICENSE for details.

from .core import *  # noqa: F401,F403
from .visualization import *  # noqa: F401,F403
from .performance import *  # noqa: F401,F403
from .analysis import *  # noqa: F401,F403
from .observability import *  # noqa: F401,F403
from .benchmark import *  # noqa: F401,F403
from .integrations import *  # noqa: F401,F403
from .funnel import *  # noqa: F401,F403


def trace_and_export(output_file: str, include_args: bool = False):
    """Convenience wrapper that mirrors the legacy top-level helper."""
    return trace_scope(output_file, include_args)
