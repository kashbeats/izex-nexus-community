# Verification record

October22,2026. Maintainer:Kingsley Izex / IZEX Solutions.

- Python adapter tests:10passed. Includes read-only HTTP methods, bearer authentication, fixed configured item queries, cache expiry, future/unsupported items, valid zero, expected401, missing optional Prometheus observations, shared Prometheus evaluation time and no stale-green reuse after upstream failure.
- JavaScript chart-policy tests:4passed. Includes visible demo labels, fixed fictional clock, refusal to enable demo from live upstream content, unconfigured incident semantics and missing-data handling.
- Actual Zabbix7.0.31 read-only smoke test:existing Ubuntu CPU/memory item projection succeeded. No events/alerts/actions were modified; no synthetic outage or restore drill was run.
- Actual private Prometheus smoke test:all eight configured AI fields returned current samples after the documented freshness gate. Requests used a common explicit evaluation timestamp, preventing request latency from appearing as a future sample. No external search/model job was started.
- Grafana13.2.1 / Business Charts7.2.5 / Infinity4.1.1 runtime:the self-contained demo rendered five gauges, configured topology, fictional checks, AI pipeline, archives, history illustrations and reference inventory. Demo title/watermarks identify fictional data. Publication screenshots contain no actual lab telemetry or addresses.
- The private production NEXUS dashboard was preserved. The live public edition requires each installer's own datasource/adapter configuration. Other Grafana/plugin versions and a fresh independent Docker build remain unverified.

No performance, uptime, restore-success or editorial-acceptance claims follow from these checks. The live adapter does not query Zabbix events or implement an incident feed. Its count is unknown until an explicitly compatible extension supplies that evidence.
