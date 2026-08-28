CREATE TABLE IF NOT EXISTS subreddits (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  rules_text TEXT,
  promotion_allowed BOOLEAN,
  last_rules_checked_at TIMESTAMPTZ,
  active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reddit_posts (
  id BIGSERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE NOT NULL,
  subreddit TEXT NOT NULL,
  title TEXT,
  body TEXT,
  author TEXT,
  permalink TEXT,
  created_at TIMESTAMPTZ,
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  relevance_score NUMERIC(5,2),
  audience_score NUMERIC(5,2),
  severity_score NUMERIC(5,2),
  engagement_score NUMERIC(5,2),
  value_fit_score NUMERIC(5,2),
  promotion_score NUMERIC(5,2),
  rule_risk_score NUMERIC(5,2),
  opportunity_score NUMERIC(5,2),
  category TEXT,
  status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS drafts (
  id BIGSERIAL PRIMARY KEY,
  reddit_post_id BIGINT REFERENCES reddit_posts(id),
  draft_type TEXT NOT NULL,
  content TEXT NOT NULL,
  cta TEXT,
  model TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  approval_status TEXT NOT NULL DEFAULT 'pending',
  approved_at TIMESTAMPTZ,
  published_at TIMESTAMPTZ,
  published_reddit_id TEXT
);

CREATE TABLE IF NOT EXISTS links (
  id BIGSERIAL PRIMARY KEY,
  subreddit TEXT,
  campaign TEXT,
  content_key TEXT,
  destination TEXT NOT NULL,
  utm_source TEXT NOT NULL DEFAULT 'reddit',
  utm_medium TEXT NOT NULL DEFAULT 'organic',
  utm_campaign TEXT,
  utm_content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS experiment_events (
  id BIGSERIAL PRIMARY KEY,
  event_name TEXT NOT NULL,
  anonymous_id TEXT,
  user_id TEXT,
  subreddit TEXT,
  content_key TEXT,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  properties JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_reddit_posts_opportunity ON reddit_posts(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_status ON reddit_posts(status);
CREATE INDEX IF NOT EXISTS idx_events_subreddit ON experiment_events(subreddit);
CREATE INDEX IF NOT EXISTS idx_events_occurred_at ON experiment_events(occurred_at);
