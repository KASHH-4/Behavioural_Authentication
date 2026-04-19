# Behavioral Authentication System – Database README

## Overview

This database supports a real-time behavioral authentication system using session tracking, batch-level feature extraction, and machine learning inference.

---

## Tables

### 1. users

* **site_id**: Identifies the tenant/site.
* **user_id**: Unique user identifier within a site.

---

### 2. sessions

* **session_id**: Unique session identifier.
* **site_id / user_id**: Link session to a specific user and site.
* **start_time**: When session began.
* **last_seen**: Last recorded user activity timestamp.
* **end_time**: Expiry timestamp (lease-based session control).
* **is_active**: Indicates if session is currently active.
* **is_valid**: Marks session as trusted or invalid (e.g., anomaly detected).
* **invalid_reason**: Reason for invalidation.
* **batch_count**: Number of batches recorded in session.
* **avg_dwell_time**: Average pause time between interactions.
* **std_dwell_time**: Variability in dwell time.
* **avg_flight_time**: Average movement duration.
* **std_flight_time**: Variability in movement duration.
* **avg_inter_event_time**: Average time between events.
* **std_inter_event_time**: Variability in inter-event timing.
* **avg_speed**: Average cursor movement speed.
* **created_at**: Session creation timestamp.

---

### 3. session_batches

* **batch_id**: Unique identifier for each batch.
* **session_id / site_id / user_id**: Link batch to session and user.
* **batch_start / batch_end**: Time window of the batch.
* **avg_dwell_time**: Average dwell time in batch window.
* **std_dwell_time**: Variability of dwell time.
* **avg_flight_time**: Average flight time.
* **std_flight_time**: Variability of flight time.
* **avg_inter_event_time**: Average inter-event time.
* **std_inter_event_time**: Variability of inter-event time.
* **avg_speed**: Average cursor speed.
* **event_count**: Number of events in batch.
* **is_anomalous**: Flag if batch is detected as anomalous.
* **created_at**: Batch creation timestamp.

---

### 4. user_profiles

* **site_id / user_id**: Identifies user baseline profile.
* **mean_vector**: Average feature vector (baseline behavior).
* **variance_vector**: Variance of features (behavior consistency).
* **sample_count**: Number of sessions used for baseline.
* **updated_at**: Last profile update.

---

### 5. results

* **id**: Unique result identifier.
* **batch_id**: Batch associated with this inference.
* **session_id / site_id / user_id**: Context of result.
* **created_at**: Timestamp of inference.
* **gaussian_score**: Score from Gaussian model.
* **iforest_score**: Score from Isolation Forest.
* **combined_score**: Final aggregated score.
* **decision**: Final classification (e.g., normal/anomalous).
* **details**: Additional metadata or explanation.

---

## Key Concepts

### Session Lifecycle

* Session is created when user enters system.
* Frontend updates `last_seen` and extends `end_time` periodically.
* Cron job marks session inactive when `end_time` expires.

### Batch Processing

* User behavior is aggregated into 30-second batches.
* Each batch acts as input to the ML model.
* Features include averages and standard deviations of behavior metrics.

### Real-Time ML Inference

* Each batch is evaluated independently.
* Results stored per batch.
* Anomalies can invalidate session instantly.

### Session Finalization

* When session ends:

  * Batch data is aggregated into session-level features.
  * Session averages are stored.
  * User profile is updated.
  * Batch data is deleted.

### Baseline Learning

* User profiles store long-term behavior patterns.
* Mean and variance vectors updated incrementally.
* Only valid sessions contribute to baseline.

---

## User Workflow

1. User enters site → session is created.
2. Frontend tracks behavior and sends data.
3. Every ~30 seconds → batch is generated.
4. Model runs on each batch → result stored.
5. If anomaly detected → session marked invalid.
6. Frontend periodically extends session (`end_time`).
7. If no activity → cron detects expiry.
8. Session ends → aggregates computed.
9. User profile updated with new behavior.
10. Temporary batch data is deleted.

---

## Notes for Team

* Batches are the primary unit for ML inference.
* Sessions are used for lifecycle and aggregation only.
* `last_seen` ensures accurate activity tracking.
* `end_time` enables lease-based session expiry.
* Always filter by `is_valid = TRUE` for training.
* Maintain feature consistency between batches and profiles.

---

## Security Model (RLS + Backend)

### Overview

The system uses a hybrid security approach:

* Backend (service role) has full access and bypasses RLS.
* Database enforces RLS for any authenticated access.

---

### Row Level Security (RLS)

RLS is enabled on all tables to ensure strict data isolation.

#### Key Rules

* Access is restricted by **site_id AND user_id**.
* A user can only access their own data within their site.
* Cross-site and cross-user access is prevented at the database level.

---

### Access Control

#### Anonymous Users

* All access revoked.
* No direct database interaction allowed.

#### Authenticated Users

* Allowed: SELECT, INSERT, UPDATE
* Restricted by RLS policies.

---

### Backend Access

* Backend uses **service role key**.
* Bypasses all RLS policies.
* Responsible for:

  * Session management
  * Batch insertion
  * ML processing
  * Profile updates
  * Cleanup operations

---

### JWT Requirements

For RLS enforcement, JWT must include:

```json
{
  "site_id": "<uuid>",
  "user_id": "<uuid>"
}
```

---

### Security Guarantees

* Users cannot access other users' data.
* Sites cannot access data from other sites.
* Backend retains full control for processing and analytics.

---

### Important Notes

* Never expose the service role key to clients.
* Always validate `site_id` in backend requests.
* RLS acts as a safety layer, not the primary control.

---

## Summary

This system combines:

* Real-time behavioral analysis
* Session-based aggregation
* Incremental machine learning

It is optimized for scalability, accuracy, and robustness in detecting anomalous user behavior.
