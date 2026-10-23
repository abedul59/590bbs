create table if not exists public.stock_dashboard_data (
  stock_id text not null,
  stock_name text not null,
  data_year integer not null,
  data_month integer not null check (data_month between 1 and 12),
  raw_data jsonb not null default '{}'::jsonb,
  update_date timestamptz not null default now(),
  primary key (stock_id, data_year, data_month)
);

alter table public.stock_dashboard_data enable row level security;

drop policy if exists "stock dashboard records are readable" on public.stock_dashboard_data;
create policy "stock dashboard records are readable"
  on public.stock_dashboard_data for select
  to anon, authenticated
  using (true);

drop policy if exists "stock dashboard records may be inserted" on public.stock_dashboard_data;
create policy "stock dashboard records may be inserted"
  on public.stock_dashboard_data for insert
  to anon, authenticated
  with check (true);

drop policy if exists "stock dashboard records may be updated" on public.stock_dashboard_data;
create policy "stock dashboard records may be updated"
  on public.stock_dashboard_data for update
  to anon, authenticated
  using (true)
  with check (true);

create index if not exists stock_dashboard_data_updated_idx
  on public.stock_dashboard_data (update_date desc);
