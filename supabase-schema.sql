-- US Financial Moves Database Schema
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create sections table
create table sections (
  slug text primary key,
  name text not null,
  created_at timestamptz not null default now()
);

-- Insert default sections
insert into sections (slug, name) values
('all', 'All'),
('ma', 'M&A'),
('lbo', 'LBO/PE'),
('reg', 'Regulatory/Antitrust'),
('cap', 'Capital Markets'),
('rumor', 'Rumors/Watchlist');

-- Create posts table
create table posts (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  title text not null,
  summary text,               -- why it matters (your 1-liner)
  excerpt text,               -- quoted ≤ 75 words
  source_name text not null,
  source_url text not null,
  section_slug text not null references sections(slug) on delete restrict,
  tags text[] default '{}',
  content_hash text not null, -- sha256(source_url + normalized_title)
  status text not null default 'published', -- 'published'|'hidden'
  origin_type text not null,  -- 'SEC'|'USGOV'|'PRESS'|'MEDIA'|'RUMOR'
  unique (content_hash)
);

-- Create deliveries table (for fan-out)
create table deliveries (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references posts(id) on delete cascade,
  channel text not null,     -- 'web'|'x'
  payload jsonb not null,
  status text not null default 'queued', -- 'queued'|'sent'|'failed'|'held'
  attempts int not null default 0,
  last_error text,
  created_at timestamptz not null default now(),
  unique (post_id, channel)
);

-- Create indexes for performance
create index idx_posts_section_created on posts (section_slug, created_at desc);
create index idx_posts_status_created on posts (status, created_at desc);
create index idx_posts_tags on posts using gin (tags);
create index idx_posts_content_hash on posts (content_hash);
create index idx_deliveries_status on deliveries (status, created_at);

-- Enable Row Level Security
alter table posts enable row level security;
alter table deliveries enable row level security;
alter table sections enable row level security;

-- RLS Policies for posts
create policy "Allow anonymous read access to published posts" on posts
  for select using (status = 'published');

-- RLS Policies for sections
create policy "Allow anonymous read access to sections" on sections
  for select using (true);

-- RLS Policies for deliveries (no public access)
create policy "No public access to deliveries" on deliveries
  for all using (false);

-- Function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Trigger to automatically update updated_at
create trigger update_posts_updated_at
  before update on posts
  for each row
  execute function update_updated_at_column();
