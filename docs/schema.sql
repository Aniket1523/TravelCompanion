-- Travel Companion Platform — Database Schema
-- Applied as Supabase migrations:
--   1. create_initial_schema
--   2. fix_rls_policy_gaps
--   3. add_missing_policies_indexes_updated_at

--------------------------------------------------
-- Enable extension
--------------------------------------------------
create extension if not exists "pgcrypto";

--------------------------------------------------
-- 1. PROFILES
--------------------------------------------------
create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  role text check (role in ('seeker', 'helper')),
  languages text[],
  created_at timestamp default now(),
  updated_at timestamp default now()
);

--------------------------------------------------
-- 2. FLIGHTS
--------------------------------------------------
create table if not exists flights (
  id uuid primary key default gen_random_uuid(),
  flight_number text not null,
  source text not null,
  destination text not null,
  departure_date date not null,
  created_at timestamp default now(),
  updated_at timestamp default now(),

  unique (flight_number, source, destination, departure_date)
);

--------------------------------------------------
-- 3. USER_FLIGHTS (PNR stored here)
--------------------------------------------------
create table if not exists user_flights (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  flight_id uuid references flights(id) on delete cascade,
  pnr text not null,
  created_at timestamp default now(),
  updated_at timestamp default now(),

  unique (user_id, flight_id)
);

--------------------------------------------------
-- 4. SEEKER REQUESTS
--------------------------------------------------
create table if not exists seeker_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  flight_id uuid references flights(id) on delete cascade,
  notes text,
  status text default 'open' check (status in ('open', 'matched', 'completed')),
  created_at timestamp default now(),
  updated_at timestamp default now()
);

--------------------------------------------------
-- 5. HELPER AVAILABILITY
--------------------------------------------------
create table if not exists helper_availability (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  flight_id uuid references flights(id) on delete cascade,
  is_available boolean default true,
  created_at timestamp default now(),
  updated_at timestamp default now(),

  unique (user_id, flight_id)
);

--------------------------------------------------
-- 6. MATCHES
--------------------------------------------------
create table if not exists matches (
  id uuid primary key default gen_random_uuid(),
  seeker_id uuid references auth.users(id),
  helper_id uuid references auth.users(id),
  flight_id uuid references flights(id),

  status text default 'pending' check (
    status in ('pending', 'accepted', 'rejected', 'completed')
  ),

  created_at timestamp default now(),
  updated_at timestamp default now()
);

--------------------------------------------------
-- INDEXES
--------------------------------------------------
create index if not exists idx_flights_lookup
on flights (flight_number, departure_date);

create index if not exists idx_user_flights_user
on user_flights (user_id);

create index if not exists idx_matches_flight
on matches (flight_id);

create index if not exists idx_matches_seeker
on matches (seeker_id);

create index if not exists idx_matches_helper
on matches (helper_id);

create index if not exists idx_seeker_requests_flight_status
on seeker_requests (flight_id, status);

create index if not exists idx_helper_availability_flight
on helper_availability (flight_id, is_available);

--------------------------------------------------
-- ENABLE RLS
--------------------------------------------------
alter table profiles enable row level security;
alter table flights enable row level security;
alter table user_flights enable row level security;
alter table seeker_requests enable row level security;
alter table helper_availability enable row level security;
alter table matches enable row level security;

--------------------------------------------------
-- PROFILES POLICIES
--------------------------------------------------
create policy "Users can insert their profile"
on profiles for insert
with check (auth.uid() = id);

create policy "Users can view their profile"
on profiles for select
using (auth.uid() = id);

create policy "Users can update their profile"
on profiles for update
using (auth.uid() = id);

--------------------------------------------------
-- FLIGHTS POLICIES
--------------------------------------------------
create policy "Authenticated users can view flights"
on flights for select
to authenticated
using (true);

create policy "Authenticated users can insert flights"
on flights for insert
to authenticated
with check (true);

--------------------------------------------------
-- USER_FLIGHTS POLICIES
--------------------------------------------------
create policy "Users manage their flights"
on user_flights for all
using (auth.uid() = user_id);

--------------------------------------------------
-- SEEKER REQUESTS POLICIES
--------------------------------------------------
create policy "Users insert their requests"
on seeker_requests for insert
with check (auth.uid() = user_id);

create policy "Users view their requests"
on seeker_requests for select
using (auth.uid() = user_id);

create policy "Users update their requests"
on seeker_requests for update
using (auth.uid() = user_id);

create policy "Users can delete their requests"
on seeker_requests for delete
using (auth.uid() = user_id);

--------------------------------------------------
-- HELPER AVAILABILITY POLICIES
--------------------------------------------------
create policy "Helpers manage availability"
on helper_availability for all
using (auth.uid() = user_id);

--------------------------------------------------
-- MATCHES POLICIES
-- NOTE: INSERT is handled via service_role key in the backend.
-- Match creation is a privileged operation to prevent self-matching.
--------------------------------------------------
create policy "Users view their matches"
on matches for select
using (
  auth.uid() = seeker_id OR
  auth.uid() = helper_id
);

create policy "Users update their matches"
on matches for update
using (
  auth.uid() = seeker_id OR
  auth.uid() = helper_id
);

create policy "Users can delete their matches"
on matches for delete
using (
  auth.uid() = seeker_id OR
  auth.uid() = helper_id
);

--------------------------------------------------
-- UPDATED_AT TRIGGER
--------------------------------------------------
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language 'plpgsql';

create trigger update_profiles_updated_at before update on profiles
for each row execute function update_updated_at_column();

create trigger update_flights_updated_at before update on flights
for each row execute function update_updated_at_column();

create trigger update_user_flights_updated_at before update on user_flights
for each row execute function update_updated_at_column();

create trigger update_seeker_requests_updated_at before update on seeker_requests
for each row execute function update_updated_at_column();

create trigger update_helper_availability_updated_at before update on helper_availability
for each row execute function update_updated_at_column();

create trigger update_matches_updated_at before update on matches
for each row execute function update_updated_at_column();
