# Cron Setup for Continuous Behavioral Monitoring

## Overview

This module implements automated session monitoring using Supabase PostgreSQL (`pg_cron`).

The cron job ensures continuous behavioral authentication by evaluating user activity in a rolling time window without modifying the existing database schema.

---

## Objective

- Continuously monitor user sessions
- Detect inactive users
- Maintain session validity
- Support batch-based behavioral analysis
- Ensure system consistency without schema changes

---

## Time Window Logic

- SDK updates user activity every **2.5 minutes**
- Cron job runs every **1 minute**
- System evaluates activity within the **last 5 minutes**

This ensures:
- At least 2 updates per active user inside the window
- Near real-time session monitoring

---
