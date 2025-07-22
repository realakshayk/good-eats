# Monitoring & Alerting

## Uptime & Health
- `/api/v1/health/ready` endpoint for uptime checks
- `/metrics` endpoint for Prometheus scraping
- Grafana dashboard for API, error, and latency metrics

## Error & Alert Routing
- Sentry integration for error capture
- Slack/email alerts for error spikes, fallback usage, high latency
- Alert routing tested and documented

## Logs
- Rotating file logs, journald, and log tailer
- All errors and key events logged with trace IDs 