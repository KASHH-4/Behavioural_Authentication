# Example API Usage

## 1) Start Session

```bash
curl -X POST http://localhost:5000/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001"}'
```

## 2) Collect Behavioral Events

```bash
curl -X POST http://localhost:5000/collect \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"<SESSION_ID>",
    "user_id":"user_001",
    "events":[
      {"event_type":"mouse_move","timestamp":1710000000.1,"x":120,"y":200,"inter_event_time":0.04},
      {"event_type":"click","timestamp":1710000000.5,"x":130,"y":210,"inter_event_time":0.40},
      {"event_type":"key_down","timestamp":1710000000.8,"flight_time":0.10,"inter_event_time":0.30},
      {"event_type":"key_up","timestamp":1710000000.9,"dwell_time":0.08,"inter_event_time":0.10}
    ]
  }'
```

## 3) Get Authentication Score

```bash
curl "http://localhost:5000/auth-score?session_id=<SESSION_ID>"
```

## 4) End Session

```bash
curl -X POST http://localhost:5000/end-session \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID>"}'
```

## 5) SDK Integration

```html
<script src="/sdk/tracker.js"></script>
<script>
  const tracker = BehaviorAuthTracker.init({
    apiBaseUrl: "http://localhost:5000",
    userId: "user_001",
    flushIntervalMs: 2000
  });

  tracker.start();

  // Trigger scoring at any point during the active session
  // const score = await tracker.getAuthScore();

  // End when the session closes
  // await tracker.stop();
</script>
```
