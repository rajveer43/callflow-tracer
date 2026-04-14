"""
Alert management and webhook integration module for CallFlow Tracer.

Send alerts to Slack, PagerDuty, and other services.
Configure rules for automatic alerting based on trace analysis.

Example:
    from callflow_tracer.ai import AlertManager

    alerts = AlertManager(
        webhooks={
            'slack': 'https://hooks.slack.com/...',
            'pagerduty': 'https://events.pagerduty.com/...'
        }
    )

    alerts.configure_rules([
        {
            'condition': 'severity == critical',
            'action': 'slack',
            'message': 'Critical anomaly detected: {source}'
        }
    ])
"""

import uuid
import operator as op
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Deque


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Alert:
    """Represents a single alert event."""

    alert_id: str
    timestamp: str
    severity: str          # 'critical' | 'high' | 'medium' | 'low'
    title: str
    message: str
    source: str            # 'anomaly' | 'regression' | 'performance' | 'manual' …
    metadata: Dict[str, Any]
    sent_to: List[str] = field(default_factory=list)


@dataclass
class AlertRule:
    """A rule that maps a condition to a delivery action."""

    rule_id: str
    condition: str
    action: str            # name of a registered AlertChannel
    message_template: str
    enabled: bool = True


# ---------------------------------------------------------------------------
# Observer pattern — delivery result tracking
# ---------------------------------------------------------------------------

@dataclass
class AlertEvent:
    """Emitted after every delivery attempt (success or failure)."""

    alert: Alert
    channel: str
    success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AlertObserver(ABC):
    """Implement this to react to delivery outcomes without touching AlertManager."""

    @abstractmethod
    def on_alert(self, event: AlertEvent) -> None: ...


class LoggingObserver(AlertObserver):
    """Prints every delivery attempt to stdout — useful during development."""

    def on_alert(self, event: AlertEvent) -> None:
        status = "OK   " if event.success else "FAIL "
        err = f" | error={event.error}" if event.error else ""
        print(
            f"[{event.timestamp}] {status} → {event.channel}"
            f" | id={event.alert.alert_id}"
            f" | severity={event.alert.severity}"
            f"{err}"
        )


class MetricsObserver(AlertObserver):
    """Counts successes and failures — attach to Prometheus/StatsD as needed."""

    def __init__(self) -> None:
        self.sent: int = 0
        self.failed: int = 0
        self.by_channel: Dict[str, Dict[str, int]] = {}

    def on_alert(self, event: AlertEvent) -> None:
        bucket = self.by_channel.setdefault(event.channel, {"sent": 0, "failed": 0})
        if event.success:
            self.sent += 1
            bucket["sent"] += 1
        else:
            self.failed += 1
            bucket["failed"] += 1

    def summary(self) -> Dict[str, Any]:
        return {
            "total_sent": self.sent,
            "total_failed": self.failed,
            "by_channel": self.by_channel,
        }


# ---------------------------------------------------------------------------
# Strategy pattern — one class per delivery channel
# ---------------------------------------------------------------------------

class AlertChannel(ABC):
    """A single delivery channel.  Subclass to add new destinations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique channel identifier used in rules and webhook config."""
        ...

    @abstractmethod
    def send(self, alert: Alert) -> bool:
        """Deliver the alert.  Returns True on success, False on failure."""
        ...


class SlackChannel(AlertChannel):
    """Delivers alerts to a Slack incoming-webhook URL."""

    _COLOR_MAP = {
        "critical": "#FF0000",
        "high":     "#FF6600",
        "medium":   "#FFCC00",
        "low":      "#00CC00",
    }

    def __init__(self, webhook_url: str) -> None:
        self._url = webhook_url

    @property
    def name(self) -> str:
        return "slack"

    def send(self, alert: Alert) -> bool:
        try:
            import requests

            payload = {
                "attachments": [
                    {
                        "color": self._COLOR_MAP.get(alert.severity, "#808080"),
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {"title": "Severity", "value": alert.severity, "short": True},
                            {"title": "Source",   "value": alert.source,   "short": True},
                            {"title": "Time",     "value": alert.timestamp, "short": False},
                        ],
                    }
                ]
            }

            resp = requests.post(self._url, json=payload, timeout=5)
            return resp.ok
        except Exception as exc:
            raise AlertDeliveryError(self.name, alert, exc) from exc


class PagerDutyChannel(AlertChannel):
    """Delivers alerts to the PagerDuty Events v2 API."""

    _SEVERITY_MAP = {
        "critical": "critical",
        "high":     "error",
        "medium":   "warning",
        "low":      "info",
    }

    def __init__(self, routing_key: str) -> None:
        self._key = routing_key

    @property
    def name(self) -> str:
        return "pagerduty"

    def send(self, alert: Alert) -> bool:
        try:
            import requests

            payload = {
                "routing_key": self._key,
                "event_action": "trigger",
                "dedup_key": alert.alert_id,
                "payload": {
                    "summary": alert.title,
                    "severity": self._SEVERITY_MAP.get(alert.severity, "error"),
                    "source": alert.source,
                    "custom_details": alert.metadata,
                },
            }

            resp = requests.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=5,
            )
            return resp.ok
        except Exception as exc:
            raise AlertDeliveryError(self.name, alert, exc) from exc


class EmailChannel(AlertChannel):
    """Delivers alerts via SMTP.  Configure smtp_host/port/from/to at init."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_addr: str,
        to_addrs: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self._host = smtp_host
        self._port = smtp_port
        self._from = from_addr
        self._to = to_addrs
        self._username = username
        self._password = password

    @property
    def name(self) -> str:
        return "email"

    def send(self, alert: Alert) -> bool:
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.upper()}] {alert.title}"
            msg["From"] = self._from
            msg["To"] = ", ".join(self._to)
            msg.attach(MIMEText(alert.message, "plain"))

            with smtplib.SMTP(self._host, self._port) as server:
                if self._username and self._password:
                    server.login(self._username, self._password)
                server.sendmail(self._from, self._to, msg.as_string())

            return True
        except Exception as exc:
            raise AlertDeliveryError(self.name, alert, exc) from exc


class CallableChannel(AlertChannel):
    """Wraps a plain callable as a channel — for register_handler compat."""

    def __init__(self, channel_name: str, handler: Callable[[Alert], Any]) -> None:
        self._name = channel_name
        self._handler = handler

    @property
    def name(self) -> str:
        return self._name

    def send(self, alert: Alert) -> bool:
        result = self._handler(alert)
        # If the handler explicitly returns False, treat as failure
        return result is not False


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class AlertDeliveryError(Exception):
    """Raised when a channel fails to deliver an alert."""

    def __init__(self, channel: str, alert: Alert, cause: Exception) -> None:
        self.channel = channel
        self.alert = alert
        self.cause = cause
        super().__init__(f"Delivery failed on channel '{channel}' for alert {alert.alert_id}: {cause}")


class ConditionSyntaxError(ValueError):
    """Raised when a rule condition cannot be parsed."""
    pass


# ---------------------------------------------------------------------------
# Safe condition evaluator (replaces eval())
# ---------------------------------------------------------------------------

_OPERATORS: Dict[str, Callable] = {
    "==": op.eq,
    "!=": op.ne,
    ">=": op.ge,
    "<=": op.le,
    ">":  op.gt,
    "<":  op.lt,
}

# Longest symbols first so ">=" is matched before ">"
_OPERATOR_SYMBOLS = sorted(_OPERATORS.keys(), key=len, reverse=True)


class ConditionEvaluator:
    """
    Evaluates simple 'field OP value' conditions without using eval().

    Supported operators: ==  !=  >  >=  <  <=

    Examples:
        "severity == critical"
        "duration >= 1.5"
        "source != manual"
    """

    def evaluate(self, condition: str, context: Dict[str, Any]) -> bool:
        condition = condition.strip()

        for symbol in _OPERATOR_SYMBOLS:
            if symbol in condition:
                parts = condition.split(symbol, 1)
                if len(parts) != 2:
                    raise ConditionSyntaxError(
                        f"Cannot parse condition: {condition!r}"
                    )
                field_name = parts[0].strip()
                raw_value  = parts[1].strip().strip("'\"")

                actual = context.get(field_name)
                if actual is None:
                    return False

                # Coerce the literal to match the context value's type
                expected: Any = raw_value
                try:
                    expected = type(actual)(raw_value)
                except (ValueError, TypeError):
                    pass

                comparator = _OPERATORS[symbol]
                try:
                    return comparator(actual, expected)
                except TypeError as exc:
                    raise ConditionSyntaxError(
                        f"Cannot compare '{field_name}' ({type(actual).__name__}) "
                        f"{symbol} '{raw_value}': {exc}"
                    ) from exc

        raise ConditionSyntaxError(
            f"No supported operator found in condition: {condition!r}. "
            f"Supported: {', '.join(_OPERATOR_SYMBOLS)}"
        )


# ---------------------------------------------------------------------------
# Chain of Responsibility — rule evaluation pipeline
# ---------------------------------------------------------------------------

class RuleHandler(ABC):
    """One step in the rule evaluation chain."""

    def __init__(self) -> None:
        self._next: Optional["RuleHandler"] = None

    def set_next(self, handler: "RuleHandler") -> "RuleHandler":
        self._next = handler
        return handler

    def handle(self, rule: AlertRule, context: Dict[str, Any]) -> Optional[Alert]:
        if self._next:
            return self._next.handle(rule, context)
        return None


class EnabledCheckHandler(RuleHandler):
    """Short-circuits the chain when the rule is disabled."""

    def handle(self, rule: AlertRule, context: Dict[str, Any]) -> Optional[Alert]:
        if not rule.enabled:
            return None
        return super().handle(rule, context)


class ConditionEvalHandler(RuleHandler):
    """Short-circuits the chain when the condition is not met."""

    def __init__(self, evaluator: ConditionEvaluator) -> None:
        super().__init__()
        self._evaluator = evaluator

    def handle(self, rule: AlertRule, context: Dict[str, Any]) -> Optional[Alert]:
        try:
            if not self._evaluator.evaluate(rule.condition, context):
                return None
        except ConditionSyntaxError as exc:
            raise ConditionSyntaxError(
                f"Rule '{rule.rule_id}' has an invalid condition: {exc}"
            ) from exc
        return super().handle(rule, context)


class CreateAlertHandler(RuleHandler):
    """Terminal handler — builds and returns the Alert object."""

    def handle(self, rule: AlertRule, context: Dict[str, Any]) -> Optional[Alert]:
        try:
            message = rule.message_template.format(**context)
        except KeyError:
            message = rule.message_template  # leave unresolved placeholders as-is

        return Alert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            severity=context.get("severity", "medium"),
            title=f"[{context.get('severity', 'medium').upper()}] {rule.rule_id}",
            message=message,
            source=context.get("source", "rule"),
            metadata=context,
        )


# ---------------------------------------------------------------------------
# AlertManager
# ---------------------------------------------------------------------------

class AlertManager:
    """
    Orchestrates alert rules, channel delivery, and observer notification.

    Architecture:
        - AlertChannel  (Strategy)              — one class per destination
        - RuleHandler   (Chain of Responsibility) — pipeline per rule evaluation
        - AlertObserver (Observer)              — delivery outcome hooks
        - ConditionEvaluator                    — safe, no-eval condition parsing
    """

    _HISTORY_MAXLEN = 1000  # cap in-memory history to avoid unbounded growth

    def __init__(self, webhooks: Optional[Dict[str, str]] = None) -> None:
        webhooks = webhooks or {}

        # Channel registry (Strategy)
        self._channels: Dict[str, AlertChannel] = {}
        if "slack" in webhooks:
            self.register_channel(SlackChannel(webhooks["slack"]))
        if "pagerduty" in webhooks:
            self.register_channel(PagerDutyChannel(webhooks["pagerduty"]))

        # Rules and history
        self.rules: List[AlertRule] = []
        self.alert_history: Deque[Alert] = deque(maxlen=self._HISTORY_MAXLEN)

        # Observers
        self._observers: List[AlertObserver] = []

        # Rule evaluation chain (Chain of Responsibility)
        self._evaluator = ConditionEvaluator()
        self._rule_chain = EnabledCheckHandler()
        (self._rule_chain
            .set_next(ConditionEvalHandler(self._evaluator))
            .set_next(CreateAlertHandler()))

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_channel(self, channel: AlertChannel) -> None:
        """Register a delivery channel.  Replaces any existing channel with the same name."""
        self._channels[channel.name] = channel

    def register_handler(self, action: str, handler: Callable[[Alert], Any]) -> None:
        """
        Register a plain callable as a channel (backward-compatible API).

        Equivalent to: register_channel(CallableChannel(action, handler))
        """
        self.register_channel(CallableChannel(action, handler))

    def register_observer(self, observer: AlertObserver) -> None:
        """Attach an observer to receive AlertEvent notifications."""
        self._observers.append(observer)

    # ------------------------------------------------------------------
    # Rule configuration
    # ------------------------------------------------------------------

    def configure_rules(self, rules: List[Dict[str, Any]]) -> None:
        """
        Add alert rules from a list of dicts.

        Each dict supports keys:
            condition       — e.g. "severity == critical"
            action          — channel name, e.g. "slack"
            message         — message template with {field} placeholders
            enabled         — bool, default True
        """
        for rule_config in rules:
            rule = AlertRule(
                rule_id=str(uuid.uuid4()),
                condition=rule_config.get("condition", ""),
                action=rule_config.get("action", "slack"),
                message_template=rule_config.get("message", ""),
                enabled=rule_config.get("enabled", True),
            )
            self.rules.append(rule)

    # ------------------------------------------------------------------
    # Alert dispatch
    # ------------------------------------------------------------------

    def check_and_alert(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules against analysis_result and dispatch matching alerts.

        Returns a list of serialised Alert dicts for every alert that was created.
        Raises ConditionSyntaxError if any enabled rule has an invalid condition.
        """
        sent_alerts = []

        for rule in self.rules:
            alert = self._rule_chain.handle(rule, analysis_result)
            if alert is None:
                continue

            self._dispatch(alert, [rule.action])
            self.alert_history.append(alert)
            sent_alerts.append(asdict(alert))

        return sent_alerts

    def send_alert(
        self,
        severity: str,
        title: str,
        message: str,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send an alert directly to one or more channels.

        If channels is None every registered channel receives the alert.
        """
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            severity=severity,
            title=title,
            message=message,
            source=source,
            metadata=metadata or {},
        )

        target_channels = channels if channels is not None else list(self._channels.keys())
        self._dispatch(alert, target_channels)
        self.alert_history.append(alert)
        return asdict(alert)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_alerts(
        self,
        limit: int = 100,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return recent alerts, optionally filtered by severity."""
        alerts: List[Alert] = list(self.alert_history)[-limit:]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return [asdict(a) for a in alerts]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch(self, alert: Alert, channel_names: List[str]) -> None:
        """Deliver alert to each named channel and notify observers."""
        for name in channel_names:
            channel = self._channels.get(name)
            if channel is None:
                self._notify(alert, name, success=False, error=f"Channel '{name}' not registered")
                continue

            try:
                success = channel.send(alert)
                if success:
                    alert.sent_to.append(name)
                self._notify(alert, name, success=success)
            except AlertDeliveryError as exc:
                self._notify(alert, name, success=False, error=str(exc.cause))

    def _notify(
        self,
        alert: Alert,
        channel: str,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Emit an AlertEvent to all registered observers."""
        event = AlertEvent(alert=alert, channel=channel, success=success, error=error)
        for observer in self._observers:
            try:
                observer.on_alert(event)
            except Exception:
                pass  # observers must never crash the main flow


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def create_alert_manager(webhooks: Optional[Dict[str, str]] = None) -> AlertManager:
    """Create an AlertManager with optional webhook configuration."""
    return AlertManager(webhooks)
