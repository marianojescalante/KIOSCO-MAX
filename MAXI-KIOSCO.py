Código fuente del sistema de maxi kiosco > # KioscoPOS - MAXI KIOSCO - VERSION FINAL TP5 CON LOGIN CODIFICADO
Alumno: Mariano Escalante - SUR-TECH - Monte Chingolo
08-10-26 FINAL - P5 VALIDADO + LOGIN HASH + SEGURIDAD COMPLETA

import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from datetime import datetime

DB = "kioscopos_tp5.db"
turno_actual = None
usuario_logueado = None
rol_logueado = None

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()
def verificar_pass(p, h): return hash_pass(p) == h

def init_db():
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS usuarios (user TEXT PRIMARY KEY, pass_hash TEXT, rol TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS turnos (id TEXT PRIMARY KEY, cajero TEXT, fisica REAL, digital REAL, estado TEXT, usuario TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS movimientos (id INTEGER PRIMARY KEY AUTOINCREMENT, turno_id TEXT, detalle TEXT, monto REAL, caja TEXT, usuario TEXT, fecha TEXT)")
c.execute("INSERT OR IGNORE INTO usuarios VALUES (?,?,?)", ("dueño", hash_pass("admin123"), "Dueño"))
c.execute("INSERT OR IGNORE INTO usuarios VALUES (?,?,?)", ("empleado", hash_pass("empleado123"), "Empleado"))
c.execute("INSERT OR IGNORE INTO usuarios VALUES (?,?,?)", ("Mariano", hash_pass("1234"), "Dueño"))
conn.commit(); conn.close()

def login_db(user, password):
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT pass_hash, rol FROM usuarios WHERE user=?", (user,))
row = c.fetchone(); conn.close()
if row and verificar_pass(password, row[0]): return True, row[1]
return False, None

def abrir_turno_db(cajero):
global turno_actual
conn = sqlite3.connect(DB); c = conn.cursor()
c.execute("SELECT id FROM turnos WHERE estado='ABIERTO'")
if c.fetchone(): conn.close(); return None, "P5 VIOLADO: Ya hay un turno ABIERTO"
turno_id = f"T-{datetime.now().strftime('%d%H%M%S')}"
c.execute("INSERT INTO turnos VALUES (?,?,?,?,?,?)", (turno_id, cajero, 0, 0, 'ABIERTO', usuario_logueado))
conn.commit(); conn.close(); turno_actual = turno_id; return turno_id, "OK"

def registrar_venta(monto, metodo):
if not turno_actual: return False
caja = "fisica" if metodo == "EFECTIVO" else "digital"
conn = sqlite3.connect(DB); c = conn.cursor()
c.execute(f"UPDATE turnos SET {caja} = {caja} + ? WHERE id=?", (monto, turno_actual))
c.execute("INSERT INTO movimientos (turno_id, detalle, monto, caja, usuario, fecha) VALUES (?,?,?,?,?,?)", (turno_actual, f"Venta {metodo}", monto, caja, usuario_logueado, datetime.now().strftime("%d/%m/%Y %H:%M")))
conn.commit(); conn.close(); return True

def registrar_egreso_cp03(monto=8000):
if not turno_actual: return False
conn = sqlite3.connect(DB); c = conn.cursor()
c.execute("UPDATE turnos SET fisica = fisica - ? WHERE id=?", (monto, turno_actual))
c.execute("INSERT INTO movimientos (turno_id, detalle, monto, caja, usuario, fecha) VALUES (?,?,?,?,?,?)", (turno_actual, "EGRESO CP03 - Papas Fritas", -monto, "fisica", usuario_logueado, datetime.now().strftime("%d/%m/%Y %H:%M")))
conn.commit(); conn.close(); return True

def cierre_z_db():
global turno_actual
if not turno_actual: return None
conn = sqlite3.connect(DB); c = conn.cursor()
c.execute("SELECT fisica, digital FROM turnos WHERE id=?", (turno_actual,))
fisica, digital = c.fetchone()
total = fisica + digital
c.execute("UPDATE turnos SET estado='CERRADO' WHERE id=?", (turno_actual,))
conn.commit(); conn.close()
texto = f"Cierre Z {turno_actual} - Fisica: {digital} - Total: ${total} - Usuario: {usuario_logueado} - NO EDITABLE"
turno_actual = None; return texto