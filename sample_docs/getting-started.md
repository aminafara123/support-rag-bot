# Getting Started with Nimbus

Nimbus is a cloud analytics dashboard that turns your product and billing data into live charts and alerts. This guide walks you through creating your workspace and building your first dashboard.

## Creating your workspace

After signing up, you'll be asked to name your workspace. A workspace is the top-level container for your dashboards, data sources, and team members. You can rename it later under Settings > Workspace.

## Connecting your first data source

Go to Data > Sources and click "Add source". Nimbus supports PostgreSQL, MySQL, BigQuery, and CSV uploads. Paste your read-only connection string and click "Test connection". Nimbus only ever issues read queries against your database, so it can never modify your data.

## Building a dashboard

From the home screen, click "New dashboard", then "Add widget". Choose a chart type, pick a data source, and write or generate a query. Widgets refresh automatically every 15 minutes on paid plans and every 24 hours on the Free plan.

## Inviting your team

Open Settings > Members and enter your teammates' email addresses. Invited users receive an email link that expires after 7 days. You can assign each member the Viewer, Editor, or Admin role.
