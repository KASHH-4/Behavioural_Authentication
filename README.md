# Behavioral Continuous Authentication System
minor change 

A modular, real-time behavioral continuous authentication system with:

- Browser SDK (`sdk/tracker.js`) for behavior capture
- Flask backend for data collection and scoring
- Feature extraction and profile building pipeline
- Comparative anomaly detection (Gaussian + Isolation Forest)
- Decision engine and evaluation utilities
- SQL schema for users, sessions, events, features, and results
- Supabase-backed storage using PostgreSQL tables

## 1. Project Structure

```text
EDI_2/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── services/
│       ├── __init__.py
│       ├── data_acquisition.py
│       ├── feature_extraction.py
│       ├── profile_builder.py
│       ├── anomaly_detection.py
│       ├── decision_engine.py
│       ├── evaluation.py
│       └── logging_service.py
├── sdk/
│   └── tracker.js
├── sql/
│   └── schema.sql
├── examples/
│   └── api_usage.md
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## 2. Implemented Pipeline (Strict Workflow)

Frontend SDK -> Backend -> Feature Extraction -> Profile -> Model -> Decision -> Response

1. Data Acquisition Module:
- `app/services/data_acquisition.py`
- Validates and stores raw mouse, click, keyboard, and timing events.

2. Feature Extraction Module:
- `app/services/feature_extraction.py`
- Cleans data and derives required mouse, keyboard, and interaction features.
- Produces structured feature vectors and normalization through L2 vector normalization.

3. Behavioral Profile Builder:
- `app/services/profile_builder.py`
- Builds user baseline with mean and variance over historical feature vectors.

4. Anomaly Detection Engine:
- `app/services/anomaly_detection.py`
- Model 1: Gaussian distance-based anomaly score.
- Model 2: Isolation Forest anomaly score.

5. Decision Engine:
- `app/services/decision_engine.py`
- Converts combined anomaly score to `Legitimate` or `Suspicious` using threshold.

6. Evaluation and Logging:
- `app/services/evaluation.py` computes FAR, FRR, AUC.
- `app/services/logging_service.py` logs session activity, predictions, and anomalies.

## 3. API Endpoints

- `POST /start-session`
- `POST /end-session`
- `POST /collect`
- `GET /auth-score?session_id=<SESSION_ID>`

## 4. Database Design

SQL schema is defined in `sql/schema.sql` and intended for Supabase PostgreSQL.

Tables:
- `users`
- `sessions`
- `raw_behavior_data`
- `features`
- `user_profiles`
- `results`

## 5. Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy environment file and set Supabase credentials:

```bash
copy .env.example .env
```

Run the statements in `sql/schema.sql` inside your Supabase SQL editor before starting the backend.

Run backend:

```bash
python run.py
```

Backend starts on `http://localhost:5000`.

## 6. SDK Usage

Include `sdk/tracker.js` in your web app and initialize:

```html
<script src="/sdk/tracker.js"></script>
<script>
  const tracker = BehaviorAuthTracker.init({
    apiBaseUrl: "http://localhost:5000",
    userId: "user_001",
    flushIntervalMs: 2000,
    maxBufferSize: 100
  });

  tracker.start();
  // const result = await tracker.getAuthScore();
  // await tracker.stop();
</script>
```

## 7. Evaluation Metrics

Use `app/services/evaluation.py`:

```python
from app.services.evaluation import compute_far_frr_auc

metrics = compute_far_frr_auc(
    y_true=[0, 0, 1, 1],
    y_pred=[0, 1, 1, 1],
    y_scores=[0.10, 0.70, 0.80, 0.95],
)
print(metrics)
# {'far': ..., 'frr': ..., 'auc': ...}
```

## 8. Example Requests

See `examples/api_usage.md` for complete `curl` and SDK examples.
