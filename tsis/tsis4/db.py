import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime


DB_HOST     = "localhost"
DB_PORT     = 5432
DB_USER     = "postgres"
DB_PASSWORD = "12345678"
DB_NAME     = "SnakeGame"


def _create_database_if_missing():
    """Connect to the default 'postgres' DB and create SnakeGame if absent."""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"[db] Database '{DB_NAME}' created.")
    else:
        print(f"[db] Database '{DB_NAME}' already exists.")

    cur.close()
    conn.close()


def _create_table_if_missing(conn):
    """Create the scores table inside SnakeGame if it doesn't exist yet."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id          SERIAL PRIMARY KEY,
                nickname    VARCHAR(50)  NOT NULL,
                points      INTEGER      NOT NULL DEFAULT 0,
                play_time   INTEGER      NOT NULL DEFAULT 0,  -- seconds
                played_at   TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()


def _connect() -> psycopg2.extensions.connection:
    """Return an open connection to the SnakeGame database."""
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        dbname=DB_NAME
    )


def init_db():
    """Call once at game startup — ensures DB and table exist."""
    _create_database_if_missing()
    conn = _connect()
    _create_table_if_missing(conn)
    conn.close()
    print("[db] Initialisation complete.")



def save_result(nickname: str, points: int, play_time: int):
    """
    Insert one game result.

    Args:
        nickname:  player name (from TextBox)
        points:    score achieved
        play_time: session length in seconds
    """
    conn = _connect()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO scores (nickname, points, play_time) VALUES (%s, %s, %s)",
            (nickname, points, play_time)
        )
        conn.commit()
    conn.close()
    print(f"[db] Saved: {nickname} | {points} pts | {play_time}s")


def get_stats() -> dict:
    """
    Return aggregate statistics across all recorded games.

    Returns a dict with:
        total_games     – total number of attempts
        total_time_s    – cumulative play time in seconds
        best_score      – highest points ever
        avg_score       – average points per game
        best_player     – nickname with the highest single score
        top_scores      – list of top-10 (nickname, points, play_time, played_at)
    """
    conn = _connect()
    with conn.cursor() as cur:

        cur.execute("""
            SELECT
                COUNT(*)                        AS total_games,
                COALESCE(SUM(play_time), 0)     AS total_time_s,
                COALESCE(MAX(points), 0)        AS best_score,
                COALESCE(ROUND(AVG(points)), 0) AS avg_score
            FROM scores;
        """)
        row = cur.fetchone()
        total_games, total_time_s, best_score, avg_score = row

        # Nickname that achieved the best score
        cur.execute("""
            SELECT nickname FROM scores
            ORDER BY points DESC LIMIT 1;
        """)
        best_row   = cur.fetchone()
        best_player = best_row[0] if best_row else "—"

        # Top-10 leaderboard
        cur.execute("""
            SELECT nickname, points, play_time, played_at
            FROM scores
            ORDER BY points DESC
            LIMIT 10;
        """)
        top_scores = cur.fetchall()

    conn.close()

    return {
        "total_games":  int(total_games),
        "total_time_s": int(total_time_s),
        "best_score":   int(best_score),
        "avg_score":    int(avg_score),
        "best_player":  best_player,
        "top_scores":   top_scores,   # list of tuples
    }


def get_player_stats(nickname: str) -> dict:
    """
    Return statistics for a single player.

    Returns a dict with:
        games_played, best_score, avg_score, total_time_s
    """
    conn = _connect()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*)                        AS games_played,
                COALESCE(MAX(points), 0)        AS best_score,
                COALESCE(ROUND(AVG(points)), 0) AS avg_score,
                COALESCE(SUM(play_time), 0)     AS total_time_s
            FROM scores
            WHERE LOWER(nickname) = LOWER(%s);
        """, (nickname,))
        row = cur.fetchone()
    conn.close()

    return {
        "games_played": int(row[0]),
        "best_score":   int(row[1]),
        "avg_score":    int(row[2]),
        "total_time_s": int(row[3]),
    }



def _fmt_time(seconds: int) -> str:
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def print_stats():
    s = get_stats()
    print("\n═══════════════ SNAKE STATISTICS ═══════════════")
    print(f"  Total attempts  : {s['total_games']}")
    print(f"  Total play time : {_fmt_time(s['total_time_s'])}")
    print(f"  Best score      : {s['best_score']}  ({s['best_player']})")
    print(f"  Average score   : {s['avg_score']}")
    print("\n  ── Top 10 leaderboard ──────────────────────────")
    for i, (nick, pts, secs, ts) in enumerate(s["top_scores"], 1):
        print(f"  {i:>2}. {nick:<16} {pts:>5} pts   {_fmt_time(secs)}   {ts:%Y-%m-%d}")
    print("═════════════════════════════════════════════════\n")

# test
if __name__ == "__main__":
    init_db()
    save_result("Alice", 42, 95)
    save_result("Bob",   17, 40)
    save_result("Alice", 88, 210)
    print_stats()
    print("Alice's stats:", get_player_stats("Alice"))