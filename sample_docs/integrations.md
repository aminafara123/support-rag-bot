# Integrations and API

## Generating an API key

Go to Settings > API and click "Create key". Copy the key immediately; for security we only show it once. Treat API keys like passwords and never commit them to source control.

## Using the REST API

The base URL is https://api.nimbus.example/v1. Authenticate by sending your key in the Authorization header: `Authorization: Bearer YOUR_KEY`. All responses are JSON. Rate limits are 60 requests per minute on Pro and 600 per minute on Business.

## Slack alerts

Connect Slack under Settings > Integrations > Slack. Once connected, any dashboard alert can post to a channel of your choice. To set an alert, open a widget, click the bell icon, and choose a threshold.

## Webhooks

You can register webhook URLs under Settings > Integrations > Webhooks. Nimbus sends a POST request with a JSON payload whenever an alert fires. Each request includes a signature header you can verify with your signing secret.

## Zapier and exports

Nimbus has a Zapier app for no-code automations. You can also export any widget's underlying data as CSV from the widget's "..." menu.
