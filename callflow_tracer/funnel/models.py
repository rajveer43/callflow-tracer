from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
import uuid


@dataclass
class AnomalyResult:
    """Result of anomaly detection"""

    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    description: str
    affected_steps: List[str]
    metrics: Dict[str, float]
    timestamp: datetime
    recommendations: List[str]


@dataclass
class PredictionResult:
    """Result of predictive analysis"""

    prediction_type: str
    confidence: float
    predicted_value: float
    time_horizon: str
    factors: List[str]
    accuracy_estimate: float
    recommendations: List[str]


@dataclass
class PatternResult:
    """Result of pattern recognition"""

    pattern_type: str
    description: str
    frequency: int
    confidence: float
    impact_score: float
    examples: List[Dict[str, Any]]
    actionable_insights: List[str]


class FunnelType(Enum):
    """Types of funnel analysis"""

    PERFORMANCE = "performance"
    CONVERSION = "conversion"
    ERROR_TRACKING = "error_tracking"
    USER_JOURNEY = "user_journey"
    API_FLOW = "api_flow"
    BUSINESS_PROCESS = "business_process"


class StepStatus(Enum):
    """Status of funnel step"""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class FunnelStep:
    """Represents a single step in a funnel"""

    name: str
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 0
    description: str = ""

    # Metrics
    total_users: int = 0
    successful_users: int = 0
    failed_users: int = 0
    avg_time_ms: float = 0.0
    median_time_ms: float = 0.0
    p95_time_ms: float = 0.0
    p99_time_ms: float = 0.0

    # Error tracking
    error_count: int = 0
    error_rate: float = 0.0
    common_errors: List[str] = field(default_factory=list)

    # Conversion metrics
    conversion_rate: float = 0.0
    dropoff_rate: float = 0.0
    relative_dropoff: float = 0.0

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0

    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate for this step"""
        if self.total_users == 0:
            return 0.0
        return (self.successful_users / self.total_users) * 100

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate for this step"""
        if self.total_users == 0:
            return 0.0
        return (self.failed_users / self.total_users) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        data = asdict(self)
        # Convert datetime to string for JSON serialization
        if self.start_time:
            data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        return data


@dataclass
class FunnelSession:
    """Represents a single user session through the funnel"""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Journey tracking
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    step_timings: Dict[str, float] = field(default_factory=dict)

    # Session metadata
    user_agent: str = ""
    ip_address: str = ""
    device_type: str = ""
    geographic_location: str = ""

    # Business context
    conversion_value: float = 0.0
    revenue_impact: float = 0.0

    # Status
    status: StepStatus = StepStatus.SUCCESS
    exit_reason: str = ""

    def add_step_timing(self, step_name: str, duration_ms: float):
        """Add timing for a step"""
        self.step_timings[step_name] = duration_ms

    def complete_step(self, step_name: str, status: StepStatus = StepStatus.SUCCESS):
        """Mark a step as completed"""
        if status == StepStatus.SUCCESS:
            if step_name not in self.completed_steps:
                self.completed_steps.append(step_name)
        else:
            if step_name not in self.failed_steps:
                self.failed_steps.append(step_name)
        self.current_step = step_name

    @property
    def total_duration_ms(self) -> float:
        """Calculate total session duration"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return (datetime.now() - self.start_time).total_seconds() * 1000

    @property
    def is_completed(self) -> bool:
        """Check if session completed all steps"""
        return self.status == StepStatus.SUCCESS and len(self.failed_steps) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        data = asdict(self)
        data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        data["total_duration_ms"] = self.total_duration_ms
        data["is_completed"] = self.is_completed
        return data
