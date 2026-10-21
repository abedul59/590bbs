create extension if not exists pgcrypto;

create table if not exists public.macrowave_dashboard_data (
  id uuid primary key default gen_random_uuid(),
  content jsonb not null,
  source_type text,
  created_at timestamptz not null default now()
);

create table if not exists public.macrowave_bulletins (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text not null default '',
  urls text[] not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists public.macrowave_lead_0050 (
  date date primary key,
  close numeric not null,
  lead numeric not null default 0,
  score numeric not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.macrowave_tmf_data (
  date date primary key,
  total_oi numeric not null default 0,
  inst_net_oi numeric not null default 0,
  retail_net_oi numeric not null default 0,
  retail_ratio numeric not null default 0,
  open numeric not null,
  high numeric not null,
  low numeric not null,
  close numeric not null,
  created_at timestamptz not null default now()
);

create table if not exists public.macrowave_options_journal (
  id uuid primary key default gen_random_uuid(),
  date date not null,
  ticker text not null,
  strategy text not null,
  expiry date not null,
  strikes jsonb not null default '{}',
  contracts integer not null default 1,
  entry_price numeric,
  exit_price numeric,
  exit_date date,
  status text not null default 'open',
  pnl numeric not null default 0,
  created_at timestamptz not null default now()
);

alter table public.macrowave_dashboard_data enable row level security;
alter table public.macrowave_bulletins enable row level security;
alter table public.macrowave_lead_0050 enable row level security;
alter table public.macrowave_tmf_data enable row level security;
alter table public.macrowave_options_journal enable row level security;

drop policy if exists "macrowave dashboard access" on public.macrowave_dashboard_data;
create policy "macrowave dashboard access" on public.macrowave_dashboard_data for all to anon, authenticated using (true) with check (true);
drop policy if exists "macrowave bulletins access" on public.macrowave_bulletins;
create policy "macrowave bulletins access" on public.macrowave_bulletins for all to anon, authenticated using (true) with check (true);
drop policy if exists "macrowave lead access" on public.macrowave_lead_0050;
create policy "macrowave lead access" on public.macrowave_lead_0050 for all to anon, authenticated using (true) with check (true);
drop policy if exists "macrowave tmf access" on public.macrowave_tmf_data;
create policy "macrowave tmf access" on public.macrowave_tmf_data for all to anon, authenticated using (true) with check (true);
drop policy if exists "macrowave journal access" on public.macrowave_options_journal;
create policy "macrowave journal access" on public.macrowave_options_journal for all to anon, authenticated using (true) with check (true);

create index if not exists macrowave_dashboard_created_at_idx on public.macrowave_dashboard_data (created_at desc);
create index if not exists macrowave_journal_created_at_idx on public.macrowave_options_journal (created_at desc);
