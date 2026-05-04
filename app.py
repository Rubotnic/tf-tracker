"""
TF G1 Tracker - local Flask app
Run: python app.py
Open: http://localhost:5000
"""

import os, sqlite3, uuid, webbrowser, threading
from flask import Flask, g, jsonify, request, send_from_directory, send_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'tracker.db')
IMG_DIR  = os.path.join(BASE_DIR, 'images')
os.makedirs(IMG_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static', static_url_path='/static')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS series (
            id         TEXT PRIMARY KEY,
            name       TEXT NOT NULL UNIQUE,
            short_name TEXT NOT NULL,
            years      TEXT,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS robots (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT DEFAULT '',
            combiner    TEXT DEFAULT '',
            instance    TEXT DEFAULT '',
            sort_order  INTEGER DEFAULT 0,
            open        INTEGER DEFAULT 0,
            img_file    TEXT,
            faction     TEXT DEFAULT '',
            series_id   TEXT REFERENCES series(id),
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS accessories (
            id            TEXT PRIMARY KEY,
            robot_id      TEXT NOT NULL REFERENCES robots(id) ON DELETE CASCADE,
            name          TEXT NOT NULL,
            qty           INTEGER DEFAULT 1,
            have          INTEGER DEFAULT 0,
            combiner_part INTEGER DEFAULT 0,
            size          TEXT DEFAULT '',
            img_file      TEXT,
            sort_order    INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_robots_series   ON robots(series_id);
        CREATE INDEX IF NOT EXISTS idx_robots_faction  ON robots(faction);
        CREATE INDEX IF NOT EXISTS idx_robots_category ON robots(category);
        CREATE INDEX IF NOT EXISTS idx_acc_robot       ON accessories(robot_id);
        CREATE INDEX IF NOT EXISTS idx_acc_have        ON accessories(have);
        CREATE INDEX IF NOT EXISTS idx_acc_combiner    ON accessories(combiner_part);
    """)

    # Seed default series if empty
    if not db.execute("SELECT 1 FROM series LIMIT 1").fetchone():
        series_data = [
            (str(uuid.uuid4()), "Generation 1",           "G1",    "1984-1990", 1),
            (str(uuid.uuid4()), "Generation 2",           "G2",    "1993-1995", 2),
            (str(uuid.uuid4()), "Beast Wars",              "BW",    "1996-2001", 3),
            (str(uuid.uuid4()), "Beast Machines",          "BM",    "2000-2001", 4),
            (str(uuid.uuid4()), "Robots in Disguise",      "RID01", "2001-2003", 5),
            (str(uuid.uuid4()), "Armada",                  "ARM",   "2002-2003", 6),
            (str(uuid.uuid4()), "Energon",                 "ENE",   "2003-2005", 7),
            (str(uuid.uuid4()), "Cybertron",               "CYB",   "2005-2006", 8),
            (str(uuid.uuid4()), "Movie (2007)",            "MOV1",  "2007-2008", 9),
            (str(uuid.uuid4()), "Animated",               "ANI",   "2008-2010", 10),
            (str(uuid.uuid4()), "Movie - ROTF",            "ROTF",  "2007-2010", 11),
            (str(uuid.uuid4()), "Movie - DOTM",            "DOTM",  "2011-2012", 12),
            (str(uuid.uuid4()), "Prime",                   "PRI",   "2011-2020", 13),
            (str(uuid.uuid4()), "Movie - AOE",             "AOE",   "2013-2014", 14),
            (str(uuid.uuid4()), "Robots in Disguise 2015", "RID15", "2015-2017", 15),
            (str(uuid.uuid4()), "Movie - TLK",             "TLK",   "2017-2018", 16),
            (str(uuid.uuid4()), "Combiner Wars",           "CW",    "2015-2018", 17),
            (str(uuid.uuid4()), "Titans Return",           "TR",    "2016-2018", 18),
        ]
        db.executemany(
            "INSERT OR IGNORE INTO series (id,name,short_name,years,sort_order) VALUES (?,?,?,?,?)",
            series_data
        )

    # Safe migrations for existing DBs
    for sql in [
        "ALTER TABLE robots ADD COLUMN series_id TEXT REFERENCES series(id)",
        "ALTER TABLE robots ADD COLUMN img_file TEXT",
        "ALTER TABLE robots ADD COLUMN faction TEXT DEFAULT ''",
    ]:
        try: db.execute(sql)
        except: pass

    db.commit()
    db.close()

# ── Serve ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMG_DIR, filename)

# ── Series ──────────────────────────────────────────────────────────────────
@app.route('/api/series', methods=['GET'])
def get_series():
    rows = get_db().execute("""
        SELECT s.*,
               COUNT(r.id) as robot_count,
               SUM(CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END) as total
        FROM series s
        LEFT JOIN robots r ON r.series_id = s.id
        GROUP BY s.id
        ORDER BY s.sort_order
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/series', methods=['POST'])
def add_series():
    d = request.json
    sid = str(uuid.uuid4())
    max_order = get_db().execute("SELECT COALESCE(MAX(sort_order),0) FROM series").fetchone()[0]
    get_db().execute(
        "INSERT INTO series (id,name,short_name,years,sort_order) VALUES (?,?,?,?,?)",
        (sid, d['name'], d.get('short_name', d['name'][:4].upper()), d.get('years',''), max_order+1)
    )
    get_db().commit()
    return jsonify({'id': sid})

@app.route('/api/series/<sid>', methods=['PATCH'])
def update_series(sid):
    d = request.json
    get_db().execute(
        "UPDATE series SET name=?, short_name=?, years=? WHERE id=?",
        (d['name'], d.get('short_name',''), d.get('years',''), sid)
    )
    get_db().commit()
    return jsonify({'ok': True})

@app.route('/api/series/<sid>', methods=['DELETE'])
def delete_series(sid):
    # Move robots to no series before deleting
    get_db().execute("UPDATE robots SET series_id=NULL WHERE series_id=?", (sid,))
    get_db().execute("DELETE FROM series WHERE id=?", (sid,))
    get_db().commit()
    return jsonify({'ok': True})

# ── Robots ──────────────────────────────────────────────────────────────────
@app.route('/api/robots', methods=['GET'])
def get_robots():
    series_id = request.args.get('series_id')
    db = get_db()
    if series_id and series_id != 'all':
        robots = db.execute(
            "SELECT * FROM robots WHERE series_id=? ORDER BY sort_order, name",
            (series_id,)
        ).fetchall()
    else:
        robots = db.execute("SELECT * FROM robots ORDER BY sort_order, name").fetchall()
    result = []
    for r in robots:
        accs = db.execute("SELECT * FROM accessories WHERE robot_id=? ORDER BY sort_order", (r['id'],)).fetchall()
        result.append({**dict(r), 'accessories': [dict(a) for a in accs]})
    return jsonify(result)

@app.route('/api/robots', methods=['POST'])
def add_robot():
    d = request.json
    rid = str(uuid.uuid4())
    max_order = get_db().execute("SELECT COALESCE(MAX(sort_order),0) FROM robots").fetchone()[0]
    get_db().execute(
        "INSERT INTO robots (id,name,category,combiner,instance,sort_order,faction,series_id) VALUES (?,?,?,?,?,?,?,?)",
        (rid, d['name'], d.get('category',''), d.get('combiner',''),
         d.get('instance',''), max_order+1, d.get('faction',''), d.get('series_id'))
    )
    get_db().commit()
    return jsonify({'id': rid})

@app.route('/api/robots/<rid>', methods=['PATCH'])
def update_robot(rid):
    d = request.json
    get_db().execute(
        "UPDATE robots SET name=?, category=?, combiner=?, instance=?, faction=?, series_id=? WHERE id=?",
        (d['name'], d.get('category',''), d.get('combiner',''),
         d.get('instance',''), d.get('faction',''), d.get('series_id'), rid)
    )
    get_db().commit()
    return jsonify({'ok': True})

@app.route('/api/robots/<rid>', methods=['DELETE'])
def delete_robot(rid):
    row = get_db().execute("SELECT img_file FROM robots WHERE id=?", (rid,)).fetchone()
    if row and row['img_file']:
        path = os.path.join(IMG_DIR, row['img_file'])
        if os.path.exists(path): os.remove(path)
    get_db().execute("DELETE FROM robots WHERE id=?", (rid,))
    get_db().commit()
    return jsonify({'ok': True})

@app.route('/api/robots/<rid>/open', methods=['PATCH'])
def toggle_open(rid):
    d = request.json
    get_db().execute("UPDATE robots SET open=? WHERE id=?", (1 if d['open'] else 0, rid))
    get_db().commit()
    return jsonify({'ok': True})

@app.route('/api/robots/<rid>/image', methods=['POST'])
def upload_robot_image(rid):
    file = request.files.get('image')
    if not file: return jsonify({'error': 'no file'}), 400
    row = get_db().execute("SELECT img_file FROM robots WHERE id=?", (rid,)).fetchone()
    if row and row['img_file']:
        old = os.path.join(IMG_DIR, row['img_file'])
        if os.path.exists(old): os.remove(old)
    ext = os.path.splitext(file.filename)[1].lower() or '.jpg'
    filename = f"robot_{rid}{ext}"
    file.save(os.path.join(IMG_DIR, filename))
    get_db().execute("UPDATE robots SET img_file=? WHERE id=?", (filename, rid))
    get_db().commit()
    return jsonify({'img_file': filename})

@app.route('/api/robots/<rid>/image', methods=['DELETE'])
def delete_robot_image(rid):
    row = get_db().execute("SELECT img_file FROM robots WHERE id=?", (rid,)).fetchone()
    if row and row['img_file']:
        path = os.path.join(IMG_DIR, row['img_file'])
        if os.path.exists(path): os.remove(path)
    get_db().execute("UPDATE robots SET img_file=NULL WHERE id=?", (rid,))
    get_db().commit()
    return jsonify({'ok': True})

# ── Accessories ─────────────────────────────────────────────────────────────
@app.route('/api/robots/<rid>/accessories', methods=['POST'])
def add_accessory(rid):
    d = request.json
    aid = str(uuid.uuid4())
    max_order = get_db().execute(
        "SELECT COALESCE(MAX(sort_order),0) FROM accessories WHERE robot_id=?", (rid,)
    ).fetchone()[0]
    get_db().execute(
        "INSERT INTO accessories (id,robot_id,name,qty,have,combiner_part,size,sort_order) VALUES (?,?,?,?,0,?,?,?)",
        (aid, rid, d['name'], d.get('qty',1), 1 if d.get('combiner_part') else 0, d.get('size',''), max_order+1)
    )
    get_db().commit()
    return jsonify({'id': aid})

@app.route('/api/accessories/<aid>/qty', methods=['PATCH'])
def update_qty(aid):
    d = request.json
    qty = max(1, int(d.get('qty', 1)))
    get_db().execute("UPDATE accessories SET qty=?, have=MIN(have,?) WHERE id=?", (qty, qty, aid))
    get_db().commit()
    row = get_db().execute("SELECT qty, have FROM accessories WHERE id=?", (aid,)).fetchone()
    return jsonify({'qty': row['qty'], 'have': row['have']})

@app.route('/api/accessories/<aid>/have', methods=['PATCH'])
def update_have(aid):
    d = request.json
    have = max(0, int(d.get('have', 0)))
    get_db().execute("UPDATE accessories SET have=? WHERE id=?", (have, aid))
    get_db().commit()
    return jsonify({'have': have})

@app.route('/api/accessories/<aid>', methods=['DELETE'])
def delete_accessory(aid):
    row = get_db().execute("SELECT img_file FROM accessories WHERE id=?", (aid,)).fetchone()
    if row and row['img_file']:
        path = os.path.join(IMG_DIR, row['img_file'])
        if os.path.exists(path): os.remove(path)
    get_db().execute("DELETE FROM accessories WHERE id=?", (aid,))
    get_db().commit()
    return jsonify({'ok': True})

@app.route('/api/accessories/<aid>/image', methods=['POST'])
def upload_image(aid):
    file = request.files.get('image')
    if not file: return jsonify({'error': 'no file'}), 400
    ext = os.path.splitext(file.filename)[1].lower() or '.jpg'
    filename = f"{aid}{ext}"
    file.save(os.path.join(IMG_DIR, filename))
    get_db().execute("UPDATE accessories SET img_file=? WHERE id=?", (filename, aid))
    get_db().commit()
    return jsonify({'img_file': filename})

@app.route('/api/accessories/<aid>/image', methods=['DELETE'])
def delete_image(aid):
    row = get_db().execute("SELECT img_file FROM accessories WHERE id=?", (aid,)).fetchone()
    if row and row['img_file']:
        path = os.path.join(IMG_DIR, row['img_file'])
        if os.path.exists(path): os.remove(path)
    get_db().execute("UPDATE accessories SET img_file=NULL WHERE id=?", (aid,))
    get_db().commit()
    return jsonify({'ok': True})

# ── PDF Export ──────────────────────────────────────────────────────────────
@app.route('/api/export/pdf')
def export_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import io, datetime

    series_id = request.args.get('series_id')
    db = get_db()

    if series_id and series_id != 'all':
        robots = db.execute("SELECT * FROM robots WHERE series_id=? ORDER BY name", (series_id,)).fetchall()
        series_name = db.execute("SELECT name FROM series WHERE id=?", (series_id,)).fetchone()
        series_label = series_name['name'] if series_name else 'Alla'
    else:
        robots = db.execute("SELECT * FROM robots ORDER BY name").fetchall()
        series_label = 'Alla serier'

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    RED = colors.HexColor('#CC1100')
    title_style = ParagraphStyle('title', fontSize=16, fontName='Helvetica-Bold', spaceAfter=4, textColor=RED)
    meta_style  = ParagraphStyle('meta',  fontSize=9,  fontName='Helvetica', textColor=colors.grey, spaceAfter=12)
    robot_style = ParagraphStyle('robot', fontSize=10, fontName='Helvetica-Bold')
    acc_style   = ParagraphStyle('acc',   fontSize=8,  fontName='Helvetica', leftIndent=12, textColor=colors.HexColor('#444444'))

    elements = []
    elements.append(Paragraph(f'TF Tracker – {series_label}', title_style))
    elements.append(Paragraph(f'Genererad: {datetime.date.today().strftime("%Y-%m-%d")}', meta_style))

    for r in robots:
        accs = db.execute("SELECT * FROM accessories WHERE robot_id=? ORDER BY sort_order", (r['id'],)).fetchall()
        hc = len([a for a in accs if a['have'] > 0])
        tc = len(accs)
        if hc == tc and tc > 0: status, sc = 'Komplett', colors.HexColor('#2e7d32')
        elif hc > 0:             status, sc = f'{hc}/{tc}', colors.HexColor('#f57f17')
        elif tc == 0:            status, sc = '–', colors.grey
        else:                    status, sc = f'0/{tc}', colors.HexColor('#c62828')

        faction  = (r['faction'] or '–').capitalize()
        combiner = r['combiner'] or '–'
        instance = f" #{r['instance']}" if r['instance'] else ''

        data = [[
            Paragraph(f"{r['name']}{instance}", robot_style),
            faction, combiner,
            Paragraph(f'<font color="{sc.hexval()}">{status}</font>',
                ParagraphStyle('s', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER))
        ]]
        for a in accs:
            a_status = f"✓ ({a['have']})" if a['have'] > 0 else '✗'
            a_color  = '#2e7d32' if a['have'] > 0 else '#c62828'
            prefix   = '⬡ ' if a['combiner_part'] else ''
            size     = f" {a['size']}" if a['size'] else ''
            data.append([
                Paragraph(f"<font size='8' color='#555555'>  {prefix}{a['name']}{size}</font>", acc_style),
                '', '',
                Paragraph(f"<font size='8' color='{a_color}'>{a_status}</font>",
                    ParagraphStyle('as', fontSize=8, alignment=TA_CENTER))
            ])

        t = Table(data, colWidths=[9*cm, 2.5*cm, 3*cm, 2.5*cm])
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
            ('LINEABOVE',  (0,0), (-1,0), 1, colors.HexColor('#cccccc')),
            ('LINEBELOW',  (0,0), (-1,0), 0.5, colors.HexColor('#dddddd')),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING',    (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ])
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fafafa'))
        t.setStyle(style)
        elements.append(t)
        elements.append(Spacer(1, 3))

    doc.build(elements)
    buf.seek(0)
    from flask import Response
    safe = series_label.replace(' ', '_').replace('/', '-')
    return Response(buf.read(), mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=tf_{safe}.pdf'})

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    import threading, time
    def stop():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=stop).start()
    return 'OK'

if __name__ == "__main__":
    init_db()
    print("\nTF Tracker")
    print("   Oppna webbläsaren: http://localhost:5000\n")
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, port=5000)