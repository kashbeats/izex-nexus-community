# Live snapshot contract v1

JSON object. A collector emits only sanitized metadata; no private prompts, logs, credentials, endpoint secrets or customer records. `dist/schema-example.json` is a **fictional demonstration**, not a current live observation.

- `version`:1; `checked_at`:Unix seconds; `stale`:boolean. Missing/old/future clocks are unknown. Latest values require `stale=false` and age0..120seconds.
- `coverage`:map with `zabbix`,`prometheus`,`backups`, each `{ok:boolean,complete:boolean}`. Source complete means the collection finished, not all host items are fresh or every application works. Per-item validity still applies.
- `servers.servers`:up to five configured rows. Fields:`id`,`name`,`role`,`address`,`source`,`note`,`metrics`,`disks`. Use explanatory notes to distinguish in-guest vs hypervisor readings.
- `metrics`:keys `cpu_percent`,`memory_used`,`memory_total`,`memory_available`,`disk_used`,`disk_total`,`disk_free`; each `{value:number,checked_at:unixSeconds}`. CPU is percent0..100. Memory and capacity are bytes. No numeric strings, NaN or Infinity. Host samples must be current. Used/total ratios must be0..100%; invalid ratios stay unknown.
- `disks`:up to three extra pools per server, each `{name,used,total,checked_at}` with byte units. The display shows at most eight combined pools/filesystems. These layers are not additive.
- `business.checks`:up to24rows, each `{name,company,state,checked_at,http_code,expected_status,response_seconds}`. State is `passing`,`failing` or `unknown`. Unknown/missing optional values may be null. Do not invent HTTP codes from an expected status. The supplied adapter uses existing scenario failed-step evidence.
- `ai`:{`checked_at`, optional numeric `worker`,`queued`,`active`,`done`,`failed`,`web`,`sources`,`diagnostics`}. `done`/`failed` are rolling24-hour retained outcomes; `web`/`sources` are24-hour attempts/attempts with usable sources. `worker` and `diagnostics` are0/1. Missing counts are unknown, not zero. Require a freshness gate appropriate to your source.
- `readiness`:up to ten `{name,state,timestamp}` rows. State:`recent`,`verified`,`old`,`unknown`; timestamp is archive time, not collector time. No restore success is inferred. The supplied collector deliberately sets `summary.restore_validated=false`.
- `incidents`:optional `{id,status,severity,title,test}` rows. Supplied adapter leaves this empty and `summary.open=null`; it does not query events. A richer adapter can supply explicit incident counts and a sanitized ledger. Empty unconfigured feed is not a healthy-zero assertion.
- `topology.links`:up to24configured `[sourceId,targetId]` pairs; only existing visible server IDs are drawn. Not automatic discovery or traffic data.

The optional local archive input is a separate small JSON file:

```json
{"checked_at":1767225600,"readiness":[{"name":"Example VM archive","state":"recent","timestamp":1767139200}]}
```

Its fixed timestamp is intentionally old; your own trusted collector must update the collection clock when it actually checks the evidence. The adapter never refreshes that clock on behalf of an unobserved archive and never opens/changes backup archives.
