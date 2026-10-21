-- The legacy tlogs-shjhs data can contain multiple records pointing to the
-- same Telegram message. Keep every record while retaining lookup speed.
drop index if exists public.evidence_logs_message_id_unique_idx;

create index if not exists evidence_logs_message_id_idx
  on public.evidence_logs (message_id)
  where message_id is not null;
