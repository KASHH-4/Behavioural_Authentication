# Behavioral Continuous Authentication System

A modular, real-time behavioral continuous authentication system designed for continuous user verification using behavioral biometrics.

The system includes:

* Browser SDK (`sdk/tracker.js`) for behavior collection
* Flask backend for session processing and scoring
* Feature extraction and profile-building pipeline
* Comparative anomaly detection using:

  * Gaussian Distance
  * Isolation Forest
* Decision engine for legitimacy classification
* PostgreSQL/Supabase-backed storage
* Automated session monitoring using pg_cron

This project is currently designed for a **single website/application integration**.

---

# 1. Project Structure

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
│   ├── table_creation.sql
│   └── security.sql
├── PostgreSQL/
│   ├── cron_setup.md
│   └── cron_queries.sql
├── examples/
│   └── api_usage.md
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

---

# 2. System Workflow

```text
Frontend SDK
      ↓
Backend API
      ↓
Feature Extraction
      ↓
Behavioral Profile Builder
      ↓
Anomaly Detection
      ↓
Decision Engine
      ↓
Authentication Result
```

---

# 3. Pipeline Modules

## 3.1 Data Acquisition Module

File:

```text
app/services/data_acquisition.py
```

Responsibilities:

* Validate incoming behavioral data
* Store session activity
* Handle session lifecycle
* Buffer behavioral events

Captured behaviors:

* Mouse movement
* Clicks
* Keyboard timing
* Interaction timestamps

---

## 3.2 Feature Extraction Module

File:

```text
app/services/feature_extraction.py
```

Responsibilities:

* Clean raw behavioral data
* Extract behavioral metrics
* Generate normalized feature vectors

Generated features include:

* Dwell time
* Flight time
* Inter-event timing
* Mouse velocity
* Mouse acceleration
* Typing rhythm

Feature normalization:

* L2 normalization

---

## 3.3 Behavioral Profile Builder

File:

```text
app/services/profile_builder.py
```

Responsibilities:

* Build historical user baseline
* Maintain:

  * Mean vector
  * Variance vector
* Update user behavioral profiles

---

## 3.4 Anomaly Detection Engine

File:

```text
app/services/anomaly_detection.py
```

Implemented Models:

### 1. Gaussian Distance-Based Detection

Computes statistical deviation from historical profile.

### 2. Isolation Forest

Detects anomalous behavioral patterns using unsupervised learning.

---

## 3.5 Decision Engine

File:

```text
app/services/decision_engine.py
```

Responsibilities:

* Combine anomaly scores
* Compute final confidence score
* Classify sessions as:

  * Legitimate
  * Suspicious

---

## 3.6 Evaluation Module

File:

```text
app/services/evaluation.py
```

Metrics:

* FAR (False Acceptance Rate)
* FRR (False Rejection Rate)
* AUC Score

---

## 3.7 Logging Service

File:

```text
app/services/logging_service.py
```

Responsibilities:

* Store anomaly results
* Log session events
* Maintain prediction history
* Track suspicious activity

---

# 4. API Endpoints

## Start Session

```http
POST /start-session
```

Starts a new behavioral session.

---

## End Session

```http
POST /end-session
```

Ends the active session.

---

## Collect Behavioral Data

```http
POST /collect
```

Receives behavioral event batches from SDK.

---

## Get Authentication Score

```http
GET /auth-score?session_id=<SESSION_ID>
```

Returns:

* anomaly score
* legitimacy classification
* behavioral confidence metrics

---

# 5. Database Design

The system uses PostgreSQL/Supabase.

SQL files:

```text
sql/table_creation.sql
sql/security.sql
```

---

# 6. Database Tables

## users

Stores application users.

Fields:

* internal UUID
* external user identifier
* creation timestamp

---

## sessions

Stores behavioral sessions.

Tracks:

* active state
* session timing
* aggregated session features
* session validity

---

## session_batches

Stores short behavioral windows collected during a session.

Contains:

* extracted feature vectors
* anomaly markers
* batch timing

---

## user_profiles

Stores historical behavioral baselines.

Contains:

* mean feature vector
* variance vector
* profile update metadata

---

## results

Stores anomaly detection outputs.

Contains:

* Gaussian score
* Isolation Forest score
* combined score
* legitimacy decision

---

# 7. User Identification Model

The project currently supports a **single application integration**.

Users are identified using:

```text
external_user_id
```

Example:

```text
user_001
42
abc123
```

Internally the system maps:

```text
external_user_id
        ↓
internal UUID
```

The internal UUID is used for:

* database relationships
* indexing
* profile linkage
* session tracking

---

# 8. Setup

## Create Virtual Environment

```bash
python -m venv .venv
```

---

## Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 9. Environment Variables

Copy:

```bash
copy .env.example .env
```

Add:

```env
SUPABASE_URL=
SUPABASE_KEY=
```

---

# 10. Database Initialization

Run the following SQL files inside Supabase SQL Editor:

```text
sql/table_creation.sql
```

Then:

```text
sql/security.sql
```

---

# 11. Run Backend

```bash
python run.py
```

Backend runs at:

```text
http://localhost:5000
```

---

# 12. SDK Usage

Include SDK:

```html
<script src="/sdk/tracker.js"></script>
```

Initialize tracker:

```html
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

---

# 13. SDK Responsibilities

The SDK:

* captures behavioral data
* buffers events
* periodically flushes event batches
* communicates with backend APIs
* manages session lifecycle

Collected data includes:

* mouse movement
* keyboard timing
* clicks
* interaction delays

---

# 14. Evaluation Metrics Example

Example:

```python
from app.services.evaluation import compute_far_frr_auc

metrics = compute_far_frr_auc(
    y_true=[0, 0, 1, 1],
    y_pred=[0, 1, 1, 1],
    y_scores=[0.10, 0.70, 0.80, 0.95],
)

print(metrics)
```

---

# 15. Cron-Based Session Monitoring

Session monitoring is implemented using:

```text
Supabase pg_cron
```

Responsibilities:

* monitor inactive sessions
* expire stale sessions
* maintain session consistency
* automate cleanup

---

## Cron Configuration

Runs:

```text
Every 1 minute
```

Uses:

```text
5-minute sliding inactivity window
```

Automatically:

* marks inactive sessions
* closes expired sessions
* updates validity state

---

## Cron Files

Documentation:

```text
PostgreSQL/cron_setup.md
```

Queries:

```text
PostgreSQL/cron_queries.sql
```

---

# 16. Current Scope

This version currently supports:

* single website integration
* local behavioral profiling
* continuous authentication experimentation
* anomaly detection research
* behavioral analytics

---

# 17. Future Improvements

Planned future improvements:

* Supabase Auth integration
* multi-tenant architecture
* multi-site SDK support
* adaptive thresholds
* online learning
* real-time streaming pipelines
* advanced ML models
* dashboard analytics
* device fingerprinting
* risk-based authentication

---

# 18. Important Notes

This project currently:

* does NOT use multi-tenant site mapping
* does NOT use `site_id`
* does NOT use API-key-based tenant separation

The system is intentionally simplified for:

* MVP development
* experimentation
* academic implementation
* rapid iteration
