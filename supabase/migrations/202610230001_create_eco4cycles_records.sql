create table if not exists public.eco4cycles_economic_records (
  date date primary key,
  verdict text not null default '',
  strategy text not null default '',
  scores jsonb not null default '{}'::jsonb,
  details jsonb not null default '{}'::jsonb,
  raw_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.eco4cycles_economic_records enable row level security;

drop policy if exists "eco4cycles records are readable" on public.eco4cycles_economic_records;
create policy "eco4cycles records are readable"
  on public.eco4cycles_economic_records for select
  to anon, authenticated
  using (true);

drop policy if exists "eco4cycles records may be inserted" on public.eco4cycles_economic_records;
create policy "eco4cycles records may be inserted"
  on public.eco4cycles_economic_records for insert
  to anon, authenticated
  with check (true);

drop policy if exists "eco4cycles records may be updated" on public.eco4cycles_economic_records;
create policy "eco4cycles records may be updated"
  on public.eco4cycles_economic_records for update
  to anon, authenticated
  using (true)
  with check (true);

create index if not exists eco4cycles_economic_records_date_desc_idx
  on public.eco4cycles_economic_records (date desc);
