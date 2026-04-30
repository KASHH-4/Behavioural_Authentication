create extension if not exists pg_cron;

create or replace function process_active_sessions()
returns void
language plpgsql
as $$
begin
  update sessions
  set last_seen = last_seen
  where is_active = true
    and last_seen >= now() - interval '5 minutes';

  update sessions
  set is_active = false,
      is_valid = false,
      invalid_reason = 'Session timeout (5 min inactivity)',
      end_time = now()
  where is_active = true
    and last_seen < now() - interval '5 minutes';
end;
$$;

select cron.schedule(
  'behavior-monitor-job',
  '* * * * *',
  $$select process_active_sessions();$$
);
