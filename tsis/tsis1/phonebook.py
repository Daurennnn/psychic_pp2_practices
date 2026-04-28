import csv, json, datetime, math
import psycopg2
from psycopg2.extras import RealDictCursor

# Config

DB_DSN = "host=localhost dbname=phonebook user=postgres password=12345678"

# DB helpers

def conn():
    return psycopg2.connect(DB_DSN, cursor_factory=RealDictCursor)

def run(sql, params=None, *, fetch="none"):
    with conn() as c, c.cursor() as cur:
        cur.execute(sql, params)
        if fetch == "one":
            result = cur.fetchone()
            c.commit()
            return result
        if fetch == "all":
            result = cur.fetchall()
            c.commit()
            return result
        c.commit()

def callproc(name, params=()):
    ph = ", ".join(["%s"] * len(params))
    with conn() as c, c.cursor() as cur:
        cur.execute(f"CALL {name}({ph})", params)
        c.commit()

# Schema + procedures

SCHEMA = """
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name) VALUES ('Family'),('Work'),('Friend'),('Other')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home','work','mobile')) DEFAULT 'mobile'
);

CREATE OR REPLACE PROCEDURE add_phone(
    p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts
    WHERE first_name || ' ' || last_name ILIKE p_name LIMIT 1;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END; $$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_name VARCHAR, p_group VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE v_cid INTEGER; v_gid INTEGER;
BEGIN
    SELECT id INTO v_cid FROM contacts
    WHERE first_name || ' ' || last_name ILIKE p_name LIMIT 1;
    IF v_cid IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_name;
    END IF;
    INSERT INTO groups (name) VALUES (p_group) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_gid FROM groups WHERE name = p_group;
    UPDATE contacts SET group_id = v_gid WHERE id = v_cid;
END; $$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INTEGER, full_name TEXT, email VARCHAR,
    birthday DATE, group_name VARCHAR, phones TEXT, created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id,
           (c.first_name || ' ' || c.last_name)::TEXT,
           c.email, c.birthday, g.name,
           STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', '),
           c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.first_name || ' ' || c.last_name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR EXISTS (SELECT 1 FROM phones ph
                  WHERE ph.contact_id = c.id
                    AND ph.phone ILIKE '%' || p_query || '%')
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.first_name, c.last_name;
END; $$;
"""

def init_db():
    c = conn()
    try:
        c.autocommit = True          # DDL must not run inside a transaction block
        with c.cursor() as cur:
            cur.execute(SCHEMA)
    finally:
        c.close()
    print("Database ready.")

# Data helpers

def get_groups():
    return [r["name"] for r in run("SELECT name FROM groups ORDER BY name", fetch="all")]

def get_or_create_group(name):
    run("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))
    return run("SELECT id FROM groups WHERE name=%s", (name,), fetch="one")["id"]

def add_contact(first, last, email="", birthday=None, group="", phones=None):
    gid  = get_or_create_group(group) if group else None
    bday = datetime.date.fromisoformat(birthday) if birthday else None
    try:
        with conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO contacts (first_name,last_name,email,birthday,group_id) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (first, last, email or None, bday, gid)
            )
            cid = cur.fetchone()["id"]
            for ph in (phones or []):
                cur.execute(
                    "INSERT INTO phones (contact_id,phone,type) VALUES (%s,%s,%s)",
                    (cid, ph["phone"], ph.get("type", "mobile"))
                )
            c.commit()
        return cid
    except psycopg2.errors.UniqueViolation:
        return None

def update_contact(cid, first=None, last=None, email=None, birthday=None, group=None):
    fields, vals = [], []
    if first    is not None: fields.append("first_name=%s"); vals.append(first)
    if last     is not None: fields.append("last_name=%s");  vals.append(last)
    if email    is not None: fields.append("email=%s");      vals.append(email)
    if birthday is not None: fields.append("birthday=%s");   vals.append(datetime.date.fromisoformat(birthday))
    if group    is not None: fields.append("group_id=%s");   vals.append(get_or_create_group(group))
    if not fields: return False
    vals.append(cid)
    with conn() as c, c.cursor() as cur:
        cur.execute(f"UPDATE contacts SET {', '.join(fields)} WHERE id=%s", vals)
        c.commit()
        return cur.rowcount > 0

def delete_contact(cid):
    with conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE id=%s", (cid,))
        c.commit()
        return cur.rowcount > 0

def search(query):
    return [dict(r) for r in run("SELECT * FROM search_contacts(%s)", (query,), fetch="all")]

def filter_group(group, sort="name"):
    order = {"name": "c.first_name,c.last_name", "birthday": "c.birthday NULLS LAST", "date": "c.created_at"}.get(sort, "c.first_name")
    return [dict(r) for r in run(f"""
        SELECT c.id, c.first_name||' '||c.last_name AS full_name, c.email, c.birthday,
               g.name AS group_name,
               STRING_AGG(p.phone||' ('||COALESCE(p.type,'?')||')',', ') AS phones,
               c.created_at
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        WHERE g.name ILIKE %s
        GROUP BY c.id,c.first_name,c.last_name,c.email,c.birthday,g.name,c.created_at
        ORDER BY {order}""", (group,), fetch="all")]

def search_email(partial):
    return [dict(r) for r in run("""
        SELECT c.id, c.first_name||' '||c.last_name AS full_name, c.email, c.birthday,
               g.name AS group_name,
               STRING_AGG(p.phone||' ('||COALESCE(p.type,'?')||')',', ') AS phones,
               c.created_at
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id,c.first_name,c.last_name,c.email,c.birthday,g.name,c.created_at
        ORDER BY c.first_name""", (f"%{partial}%",), fetch="all")]

def list_page(page=1, size=5, sort="name"):
    order = {"name": "c.first_name,c.last_name", "birthday": "c.birthday NULLS LAST", "date": "c.created_at"}.get(sort, "c.first_name")
    total = run("SELECT COUNT(*) AS n FROM contacts", fetch="one")["n"]
    rows  = run(f"""
        SELECT c.id, c.first_name||' '||c.last_name AS full_name, c.email, c.birthday,
               g.name AS group_name,
               STRING_AGG(p.phone||' ('||COALESCE(p.type,'?')||')',', ') AS phones,
               c.created_at
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        GROUP BY c.id,c.first_name,c.last_name,c.email,c.birthday,g.name,c.created_at
        ORDER BY {order} LIMIT %s OFFSET %s""", (size, (page - 1) * size), fetch="all")
    return [dict(r) for r in rows], total

def export_json(path):
    rows = run("""
        SELECT c.id, c.first_name, c.last_name, c.email, c.birthday::TEXT,
               g.name AS group_name,
               JSON_AGG(JSON_BUILD_OBJECT('phone',p.phone,'type',p.type)
                        ORDER BY p.type) FILTER (WHERE p.id IS NOT NULL) AS phones,
               c.created_at::TEXT
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        GROUP BY c.id,c.first_name,c.last_name,c.email,c.birthday,g.name,c.created_at
        ORDER BY c.first_name""", fetch="all")
    data = [dict(r) for r in rows]
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return len(data)

def import_json(path, on_dup="ask"):
    records = json.load(open(path))
    stats = {"inserted": 0, "skipped": 0, "overwritten": 0}
    for rec in records:
        first, last = rec.get("first_name", ""), rec.get("last_name", "")
        name = f"{first} {last}".strip()
        existing = run(
            "SELECT id FROM contacts WHERE first_name||' '||last_name ILIKE %s LIMIT 1",
            (name,), fetch="one"
        )
        if existing:
            action = on_dup
            if action == "ask":
                action = "overwrite" if input(f"  Duplicate '{name}'. Overwrite? [y/N]: ").strip().lower() == "y" else "skip"
            if action == "skip":
                stats["skipped"] += 1
                continue
            delete_contact(existing["id"])
            stats["overwritten"] += 1
        else:
            stats["inserted"] += 1
        phones = rec.get("phones") or []
        if isinstance(phones, str):
            phones = [{"phone": phones, "type": "mobile"}]
        add_contact(first, last, rec.get("email", ""), rec.get("birthday"), rec.get("group_name", ""), phones)
    return stats

def import_csv(path):
    stats = {"inserted": 0, "skipped": 0, "errors": 0}
    for row in csv.DictReader(open(path)):
        first, last = row.get("first_name", "").strip(), row.get("last_name", "").strip()
        if not first or not last:
            stats["errors"] += 1
            continue
        phones = [{"phone": row["phone"].strip(), "type": row.get("phone_type", "mobile").strip()}] if row.get("phone", "").strip() else []
        cid = add_contact(first, last, row.get("email", "").strip(),
                          row.get("birthday", "").strip() or None,
                          row.get("group", "").strip(), phones)
        stats["inserted" if cid else "skipped"] += 1
    return stats

# UI helpers

def ask(label, default=""):
    return input(f"  {label}: ").strip() or default

def pick(options, label="Choose"):
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        v = input(f"  {label} (1-{len(options)}): ").strip()
        if v.isdigit() and 1 <= int(v) <= len(options):
            return options[int(v) - 1]

def show_rows(rows, title=""):
    if title:
        print(f"\n  {title}")
    if not rows:
        print("  (no results)")
        return
    print()
    for r in rows:
        name   = r.get("full_name") or "?"
        email  = r.get("email") or "-"
        group  = r.get("group_name") or "-"
        bday   = str(r.get("birthday") or "-")[:10]
        phones = r.get("phones") or "-"
        cid    = r.get("id") or "?"
        print(f"  [{cid}] {name}")
        print(f"       email: {email}  group: {group}  birthday: {bday}")
        print(f"       phones: {phones}")
        print()

def pager(sort="name"):
    page, size = 1, 5
    while True:
        rows, total = list_page(page, size, sort)
        pages = max(1, math.ceil(total / size))
        print(f"\n  Page {page}/{pages}  (total: {total}, sorted by: {sort})\n")
        show_rows(rows)
        nav = []
        if page > 1:     nav.append("prev")
        if page < pages: nav.append("next")
        nav.append("quit")
        cmd = input(f"  [{' / '.join(nav)}]: ").strip().lower()
        if   cmd == "next" and page < pages: page += 1
        elif cmd == "prev" and page > 1:     page -= 1
        elif cmd in ("quit", "q"):           break

# Menu actions

def do_browse():
    sort = pick(["name", "birthday", "date"], "Sort by")
    pager(sort)

def do_search():
    q = ask("Search (name / email / phone)")
    show_rows(search(q), f"Results for '{q}'")
    input("  Enter to continue: ")

def do_filter_group():
    g    = pick(get_groups(), "Group")
    sort = pick(["name", "birthday", "date"], "Sort by")
    show_rows(filter_group(g, sort), f"Group: {g}")
    input("  Enter to continue: ")

def do_search_email():
    q = ask("Email fragment")
    show_rows(search_email(q), f"Email: '{q}'")
    input("  Enter to continue: ")

def do_add():
    first = ask("First name")
    last  = ask("Last name")
    email = ask("Email (optional)")
    bday  = ask("Birthday YYYY-MM-DD (optional)")
    group = pick(get_groups() + ["(none)"], "Group")
    if group == "(none)":
        group = ""
    phones = []
    while True:
        ph = ask("Phone (blank to finish)")
        if not ph:
            break
        pt = pick(["mobile", "home", "work"], "Type")
        phones.append({"phone": ph, "type": pt})
    cid = add_contact(first, last, email, bday or None, group, phones)
    print(f"\n  {'Added (id=' + str(cid) + ').' if cid else 'Duplicate name, skipped.'}")
    input("  Enter to continue: ")

def do_update():
    cid = ask("Contact ID")
    if not cid.isdigit():
        return
    print("  Leave blank to keep current value.")
    ok = update_contact(
        int(cid),
        first    = ask("New first name") or None,
        last     = ask("New last name")  or None,
        email    = ask("New email")      or None,
        birthday = ask("New birthday YYYY-MM-DD") or None,
        group    = (pick(get_groups(), "Group")
                    if input("  Change group? [y/N]: ").strip().lower() == "y"
                    else None),
    )
    print(f"\n  {'Updated.' if ok else 'Not found.'}")
    input("  Enter to continue: ")

def do_delete():
    cid = ask("Contact ID")
    if not cid.isdigit():
        return
    if input(f"  Delete contact {cid}? [y/N]: ").strip().lower() == "y":
        print(f"\n  {'Deleted.' if delete_contact(int(cid)) else 'Not found.'}")
    input("  Enter to continue: ")

def do_add_phone():
    name  = ask("Contact full name")
    phone = ask("Phone number")
    ptype = pick(["mobile", "home", "work"], "Type")
    try:
        callproc("add_phone", (name, phone, ptype))
        print("  Phone added.")
    except Exception as e:
        print(f"  Error: {e}")
    input("  Enter to continue: ")

def do_move_group():
    name  = ask("Contact full name")
    group = ask("Target group (created if new)")
    try:
        callproc("move_to_group", (name, group))
        print(f"  Moved to '{group}'.")
    except Exception as e:
        print(f"  Error: {e}")
    input("  Enter to continue: ")

def do_export():
    path = ask("Output file", "phonebook_export.json")
    n = export_json(path)
    print(f"  {n} contacts saved to '{path}'")
    input("  Enter to continue: ")

def do_import_json():
    path = ask("JSON file path")
    if not path:
        return
    dup = pick(["ask", "skip", "overwrite"], "On duplicate")
    try:
        s = import_json(path, dup)
        print(f"  Inserted: {s['inserted']}  Skipped: {s['skipped']}  Overwritten: {s['overwritten']}")
    except FileNotFoundError:
        print("  File not found.")
    input("  Enter to continue: ")

def do_import_csv():
    print("  Columns: first_name, last_name, phone, phone_type, email, birthday, group")
    path = ask("CSV file path")
    if not path:
        return
    try:
        s = import_csv(path)
        print(f"  Inserted: {s['inserted']}  Skipped: {s['skipped']}  Errors: {s['errors']}")
    except FileNotFoundError:
        print("  File not found.")
    input("  Enter to continue: ")

# -- Main loop

MENU = [
    ("Browse all (paginated)",        do_browse),
    ("Search (name / email / phone)", do_search),
    ("Filter by group",               do_filter_group),
    ("Search by email",               do_search_email),
    ("Add contact",                   do_add),
    ("Update contact",                do_update),
    ("Delete contact",                do_delete),
    ("Add phone to contact [proc]",   do_add_phone),
    ("Move contact to group [proc]",  do_move_group),
    ("Export to JSON",                do_export),
    ("Import from JSON",              do_import_json),
    ("Import from CSV",               do_import_csv),
    ("Exit",                          None),
]

def main():
    init_db()
    while True:
        print("\n  PhoneBook - Practice 9\n")
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i:>2}. {label}")
        raw = input("\n  Select: ").strip()
        if not raw.isdigit() or not (1 <= int(raw) <= len(MENU)):
            continue
        label, fn = MENU[int(raw) - 1]
        if fn is None:
            print("\n  Goodbye!")
            break
        print()
        fn()

if __name__ == "__main__":
    main()