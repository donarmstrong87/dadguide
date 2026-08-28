from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

from discover import reddit_client, discover
from config import load_config

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("GROWTH_DB_PATH", ROOT / "data" / "growth.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(ROOT / "templates"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 reddit_id TEXT UNIQUE NOT NULL,
 subreddit TEXT NOT NULL,
 title TEXT NOT NULL,
 body TEXT,
 author TEXT,
 permalink TEXT,
 score INTEGER DEFAULT 0,
 comments INTEGER DEFAULT 0,
 matched_keywords TEXT,
 opportunity REAL DEFAULT 0,
 category TEXT,
 status TEXT DEFAULT 'new',
 created_at TEXT,
 discovered_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS drafts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 post_id INTEGER NOT NULL,
 content TEXT NOT NULL,
 cta TEXT,
 status TEXT DEFAULT 'pending',
 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(post_id) REFERENCES posts(id)
);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_name TEXT NOT NULL,
 subreddit TEXT,
 content_key TEXT,
 properties TEXT DEFAULT '{}',
 occurred_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def heuristic_score(item: dict[str, Any]) -> float:
    text = f"{item.get('title','')} {item.get('body','')}".lower()
    keywords = set(item.get("matched_keywords", []))
    severity_terms = ("terrified", "overwhelmed", "struggling", "help", "lost", "sleep", "crying")
    severity = min(10, 3 + sum(term in text for term in severity_terms))
    engagement = min(10, 2 + item.get("comments", 0) / 10)
    audience = 10 if item.get("subreddit") in {"NewDads", "predaddit", "daddit"} else 7
    relevance = min(10, 4 + len(keywords) * 1.5)
    value_fit = 9 if any(x in text for x in ("advice", "what do i do", "how do i", "first time dad")) else 7
    promotion = 7
    rule_risk = 3
    positive = relevance + audience + severity + engagement + value_fit + promotion
    return round(max(0, min(100, positive / 60 * 100 - rule_risk * 5)), 1)


def store_discovery(items: list[dict[str, Any]]) -> int:
    conn = db()
    added = 0
    for item in items:
        score = heuristic_score(item)
        try:
            conn.execute(
                """INSERT INTO posts
                (reddit_id, subreddit, title, body, author, permalink, score, comments, matched_keywords, opportunity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item["reddit_id"], item["subreddit"], item["title"], item.get("body"), item.get("author"),
                 item["permalink"], item.get("score", 0), item.get("comments", 0),
                 json.dumps(item.get("matched_keywords", [])), score, item.get("created_at")),
            )
            added += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return added


def fallback_draft(post: sqlite3.Row) -> str:
    return (
        "Start with the immediate problem rather than trying to become an expert overnight. "
        "For a lot of new dads, the most useful thing is to pick one concrete thing you can take ownership of, "
        "communicate with your partner about what would actually help, and give yourself permission to learn as you go. "
        "You don't have to know everything to be a good dad."
    )


def ai_draft(post: sqlite3.Row) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_draft(post)
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    prompt = f"""Write one genuinely helpful Reddit response to this post. Answer the question first. Do not advertise. Do not claim personal experience. Be concise and empathetic.\n\nSubreddit: r/{post['subreddit']}\nTitle: {post['title']}\nBody: {post['body'] or ''}"""
    response = client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-5-mini"), input=prompt)
    return response.output_text.strip()


@app.get("/")
def dashboard():
    conn = db()
    posts = conn.execute("SELECT * FROM posts ORDER BY opportunity DESC, discovered_at DESC LIMIT 100").fetchall()
    pending = conn.execute("SELECT d.*, p.subreddit, p.title FROM drafts d JOIN posts p ON p.id=d.post_id WHERE d.status='pending' ORDER BY d.created_at DESC").fetchall()
    metrics = {
        "opportunities": conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0],
        "high_value": conn.execute("SELECT COUNT(*) FROM posts WHERE opportunity >= 75").fetchone()[0],
        "drafts": conn.execute("SELECT COUNT(*) FROM drafts WHERE status='pending'").fetchone()[0],
        "published": conn.execute("SELECT COUNT(*) FROM drafts WHERE status='published'").fetchone()[0],
    }
    conn.close()
    return render_template("dashboard.html", posts=posts, pending=pending, metrics=metrics)


@app.post("/discover")
def run_discovery():
    limit = min(int(request.form.get("limit", 50)), 100)
    added = store_discovery(discover(limit=limit))
    return redirect(url_for("dashboard", discovered=added))


@app.post("/draft/<int:post_id>")
def create_draft(post_id: int):
    conn = db()
    post = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if post:
        content = ai_draft(post)
        conn.execute("INSERT INTO drafts(post_id, content) VALUES (?, ?)", (post_id, content))
        conn.execute("UPDATE posts SET status='drafted' WHERE id=?", (post_id,))
        conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.post("/draft/<int:draft_id>/reject")
def reject_draft(draft_id: int):
    conn = db()
    conn.execute("UPDATE drafts SET status='rejected' WHERE id=?", (draft_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.post("/draft/<int:draft_id>/publish")
def publish_draft(draft_id: int):
    """Explicit human-triggered publish action. Never called by the discovery scheduler."""
    conn = db()
    row = conn.execute("SELECT d.*, p.reddit_id, p.subreddit FROM drafts d JOIN posts p ON p.id=d.post_id WHERE d.id=?", (draft_id,)).fetchone()
    if not row or row["status"] != "pending":
        conn.close()
        return redirect(url_for("dashboard"))
    reddit = reddit_client()
    submission = reddit.submission(id=row["reddit_id"])
    submission.reply(row["content"])
    conn.execute("UPDATE drafts SET status='published' WHERE id=?", (draft_id,))
    conn.execute("UPDATE posts SET status='published' WHERE id=(SELECT post_id FROM drafts WHERE id=?)", (draft_id,))
    conn.execute("INSERT INTO events(event_name, subreddit, properties) VALUES ('reddit_comment_published', ?, ?)", (row["subreddit"], json.dumps({"draft_id": draft_id})))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8080")), debug=False)
