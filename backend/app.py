from flask import Flask, request, jsonify
import sqlite3, datetime
app=Flask(__name__)
DB='database.db'

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, nom TEXT, localisation TEXT, plat TEXT, quantite INTEGER, created_at TEXT)')
init_db()

@app.route('/api/orders', methods=['GET','POST'])
def orders():
    if request.method=='POST':
        d=request.json
        with sqlite3.connect(DB) as c:
            c.execute('INSERT INTO orders(nom,localisation,plat,quantite,created_at) VALUES(?,?,?,?,?)',(d['nom'],d['localisation'],d['plat'],d['quantite'],datetime.datetime.now().isoformat()))
        return jsonify({'ok':True})
    with sqlite3.connect(DB) as c:
        rows=c.execute('SELECT nom,localisation,plat,quantite,created_at FROM orders ORDER BY id DESC').fetchall()
    return jsonify([{'nom':r[0],'localisation':r[1],'plat':r[2],'quantite':r[3],'created_at':r[4]} for r in rows])

app.run(debug=True)