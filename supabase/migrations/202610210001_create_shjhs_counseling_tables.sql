create extension if not exists pgcrypto;

create table if not exists public.counseling_logs (
  id uuid primary key default gen_random_uuid(),
  record_date date not null,
  content text not null,
  updated_at timestamptz not null default now()
);

create index if not exists counseling_logs_record_date_idx
  on public.counseling_logs (record_date, updated_at);

create table if not exists public.evidence_logs (
  id text primary key default gen_random_uuid()::text,
  log_date date not null,
  title text,
  telegram_url text,
  file_name text,
  message_id bigint,
  file_hash text,
  created_at timestamptz not null default now()
);

create index if not exists evidence_logs_log_date_idx
  on public.evidence_logs (log_date, created_at);

create unique index if not exists evidence_logs_message_id_unique_idx
  on public.evidence_logs (message_id)
  where message_id is not null;

alter table public.counseling_logs enable row level security;
alter table public.evidence_logs enable row level security;

drop policy if exists "public counseling log access" on public.counseling_logs;
create policy "public counseling log access"
  on public.counseling_logs
  for all
  to anon, authenticated
  using (true)
  with check (true);

drop policy if exists "public evidence log access" on public.evidence_logs;
create policy "public evidence log access"
  on public.evidence_logs
  for all
  to anon, authenticated
  using (true)
  with check (true);

grant select, insert, update, delete on public.counseling_logs to anon, authenticated;
grant select, insert, update, delete on public.evidence_logs to anon, authenticated;
