from __future__ import annotations

from flask import Flask, current_app
from supabase import Client, create_client


def init_supabase(app: Flask) -> None:
	url = app.config.get("SUPABASE_URL", "")
	key = app.config.get("SUPABASE_KEY", "")

	if not url or not key:
		raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured")

	app.extensions["supabase"] = create_client(url, key)


def get_supabase() -> Client:
	client = current_app.extensions.get("supabase")
	if client is None:
		raise RuntimeError("Supabase client is not initialized")
	return client
