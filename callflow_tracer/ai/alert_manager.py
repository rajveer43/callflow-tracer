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
            'condition': 'anomaly.severity == "critical"',
            'action': 'send_to_slack',
            'message': 'Critical anomaly: {anomaly.description}'
        }
    ])
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import re


@dataclass
class Alert:
    """An alert."""
    alert_id: str
    timestamp: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    message: str
    source: str  # 'anomaly', 'regression', 'performance', etc
    metadata: Dict[str, Any]
    sent_to: List[str] = None


@dataclass
class AlertRule:
    """An alert rule."""
    rule_id: str
    condition: str
    action: str  # 'send_to_slack', 'create_incident', 'send_email', etc
    message_template: str
    enabled: bool = True


class AlertManager:
    """Manage alerts and webhooks."""
    
    def __init__(self, webhooks: Optional[Dict[str, str]] = None):
        """
        Initialize alert manager.
        
        Args:
            webhooks: Dict of webhook URLs (e.g., {'slack': '...', 'pagerduty': '...'})
        """
        self.webhooks = webhooks or {}
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.custom_handlers: Dict[str, Callable] = {}
    
    def configure_rules(self, rules: List[Dict[str, Any]]) -> None:
        """
        Configure alert rules.
        
        Args:
            rules: List of rule configurations
        """
        import uuid
        
        for rule_config in rules:
            rule = AlertRule(
                rule_id=str(uuid.uuid4()),
                condition=rule_config.get('condition', ''),
                action=rule_config.get('action', 'send_to_slack'),
                message_template=rule_config.get('message', ''),
                enabled=rule_config.get('enabled', True)
            )
            self.rules.append(rule)
    
    def register_handler(self, action: str, handler: Callable) -> None:
        """
        Register custom alert handler.
        
        Args:
            action: Action name
            handler: Callable that handles the action
        """
        self.custom_handlers[action] = handler
    
    def check_and_alert(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check analysis results against rules and send alerts.
        
        Args:
            analysis_result: Analysis result to check
            
        Returns:
            List of sent alerts
        """
        sent_alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Evaluate condition
            if self._evaluate_condition(rule.condition, analysis_result):
                alert = self._create_alert(rule, analysis_result)
                
                # Execute action
                self._execute_action(rule.action, alert)
                
                sent_alerts.append(asdict(alert))
                self.alert_history.append(alert)
        
        return sent_alerts
    
    def send_alert(self, severity: str, title: str, message: str,
                  source: str = 'manual', metadata: Optional[Dict[str, Any]] = None,
                  channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send an alert to configured channels.
        
        Args:
            severity: Alert severity
            title: Alert title
            message: Alert message
            source: Alert source
            metadata: Optional metadata
            channels: Optional list of channels to send to
            
        Returns:
            Alert details
        """
        import uuid
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            severity=severity,
            title=title,
            message=message,
            source=source,
            metadata=metadata or {},
            sent_to=[]
        )
        
        # Send to channels
        if channels is None:
            channels = list(self.webhooks.keys())
        
        for channel in channels:
            if channel in self.webhooks:
                self._send_to_channel(channel, alert)
                alert.sent_to.append(channel)
        
        self.alert_history.append(alert)
        
        return asdict(alert)
    
    def get_alerts(self, limit: int = 100, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            severity: Optional severity filter
            
        Returns:
            List of alerts
        """
        alerts = self.alert_history[-limit:]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return [asdict(a) for a in alerts]
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate alert condition."""
        try:
            # Simple condition evaluation
            # Supports: 'field == value', 'field > value', 'field in [...]', etc
            
            # Replace context variables
            eval_condition = condition
            for key, value in context.items():
                if isinstance(value, str):
                    eval_condition = eval_condition.replace(f"{{{key}}}", f"'{value}'")
                else:
                    eval_condition = eval_condition.replace(f"{{{key}}}", str(value))
            
            # Evaluate
            return eval(eval_condition)
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def _create_alert(self, rule: AlertRule, context: Dict[str, Any]) -> Alert:
        """Create alert from rule and context."""
        import uuid
        
        # Format message
        message = rule.message_template
        for key, value in context.items():
            message = message.replace(f"{{{key}}}", str(value))
        
        return Alert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            severity=context.get('severity', 'medium'),
            title=f"Alert: {rule.action}",
            message=message,
            source=context.get('source', 'rule'),
            metadata=context
        )
    
    def _execute_action(self, action: str, alert: Alert) -> None:
        """Execute alert action."""
        if action == 'send_to_slack':
            self._send_to_slack(alert)
        elif action == 'send_to_pagerduty':
            self._send_to_pagerduty(alert)
        elif action == 'send_email':
            self._send_email(alert)
        elif action == 'create_incident':
            self._create_incident(alert)
        elif action in self.custom_handlers:
            self.custom_handlers[action](alert)
    
    def _send_to_channel(self, channel: str, alert: Alert) -> None:
        """Send alert to specific channel."""
        if channel == 'slack':
            self._send_to_slack(alert)
        elif channel == 'pagerduty':
            self._send_to_pagerduty(alert)
        elif channel == 'email':
            self._send_email(alert)
    
    def _send_to_slack(self, alert: Alert) -> None:
        """Send alert to Slack."""
        if 'slack' not in self.webhooks:
            return
        
        try:
            import requests
            
            # Format Slack message
            color_map = {
                'critical': '#FF0000',
                'high': '#FF6600',
                'medium': '#FFCC00',
                'low': '#00CC00'
            }
            
            payload = {
                'attachments': [
                    {
                        'color': color_map.get(alert.severity, '#808080'),
                        'title': alert.title,
                        'text': alert.message,
                        'fields': [
                            {
                                'title': 'Severity',
                                'value': alert.severity,
                                'short': True
                            },
                            {
                                'title': 'Source',
                                'value': alert.source,
                                'short': True
                            },
                            {
                                'title': 'Time',
                                'value': alert.timestamp,
                                'short': False
                            }
                        ]
                    }
                ]
            }
            
            requests.post(self.webhooks['slack'], json=payload)
        except Exception as e:
            print(f"Error sending to Slack: {e}")
    
    def _send_to_pagerduty(self, alert: Alert) -> None:
        """Send alert to PagerDuty."""
        if 'pagerduty' not in self.webhooks:
            return
        
        try:
            import requests
            
            severity_map = {
                'critical': 'critical',
                'high': 'error',
                'medium': 'warning',
                'low': 'info'
            }
            
            payload = {
                'routing_key': self.webhooks['pagerduty'],
                'event_action': 'trigger',
                'dedup_key': alert.alert_id,
                'payload': {
                    'summary': alert.title,
                    'severity': severity_map.get(alert.severity, 'error'),
                    'source': alert.source,
                    'custom_details': alert.metadata
                }
            }
            
            requests.post(
                'https://events.pagerduty.com/v2/enqueue',
                json=payload
            )
        except Exception as e:
            print(f"Error sending to PagerDuty: {e}")
    
    def _send_email(self, alert: Alert) -> None:
        """Send alert via email."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # This is a placeholder - implement with your email config
            print(f"Email alert: {alert.title}")
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def _create_incident(self, alert: Alert) -> None:
        """Create incident."""
        print(f"Creating incident: {alert.title}")


def create_alert_manager(webhooks: Optional[Dict[str, str]] = None) -> AlertManager:
    """
    Create alert manager instance.
    
    Args:
        webhooks: Webhook configuration
        
    Returns:
        AlertManager instance
    """
    return AlertManager(webhooks)
