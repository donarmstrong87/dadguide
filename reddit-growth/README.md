# DadGuide Reddit Growth Engine

A 90-day, community-first Reddit acquisition experiment for DadGuide.

## What is implemented

- Reddit discovery worker using PRAW.
- Keyword filtering across target communities.
- Opportunity scoring.
- Local SQLite operator dashboard.
- AI-assisted response drafting with an offline fallback.
- Explicit human approval before Reddit publishing.
- Discovery snapshots for scheduled automation.
- GitHub Actions discovery every 4 hours.
- Artifact retention for discovery snapshots.
- UTM attribution helper.
- PostgreSQL production schema for a future hosted deployment.

## Important Reddit compliance model

The system does **not** run an unattended comment/post loop. Discovery and analysis are automated, but publishing is a distinct human-triggered action. Reddit's current Developer Platform requires explicit user permission/manual action for user-authorized posting/commenting and emphasizes avoiding spam-like experiences.

## Local setup

```bash
cd reddit-growth
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/app.py
```

Then open `http://127.0.0.1:8080`.

### Credentials

Set Reddit credentials in `.env` for discovery/publishing and `OPENAI_API_KEY` for AI drafting. If no OpenAI key is configured, the dashboard uses a safe deterministic fallback draft.

For GitHub Actions, add these repository secrets:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
- `REDDIT_USERNAME`

The scheduled workflow stores a discovery snapshot as a GitHub Actions artifact. It does not publish comments.

## 90-day experiment

### Days 1–30: Listen + establish credibility
- Monitor target communities and keywords.
- Capture recurring fatherhood problems.
- Score opportunities.
- Build a content/problem taxonomy.
- Contribute genuinely useful, non-promotional responses.

### Days 31–60: Acquisition testing
- Test five positioning angles: Prepared Dad, Daily Guidance, New Dad Survival, Dad + Partner, Confidence.
- Use unique UTM parameters for every promotional link.
- Measure subreddit → visit → signup → activation.

### Days 61–90: Scale winners
- Concentrate effort on the best-performing communities and problems.
- Test small paid Reddit campaigns only after organic winners are identified.
- Produce weekly growth reports and make go/no-go decisions based on retained users and CAC.

## Suggested initial communities

- r/daddit
- r/NewDads
- r/predaddit
- r/Parenting
- r/NewParents
- r/Fatherhood
- r/Dads

Community rules must be checked before any promotional activity.

## Automation stages

`Reddit discovery → relevance scoring → rule/risk check → opportunity queue → AI draft → human approval → publish → UTM attribution → product analytics → weekly optimization`

## Security

Never commit `.env`, Reddit credentials, OpenAI keys, database credentials, or generated discovery data. The repository `.gitignore` covers local secrets and generated files.
