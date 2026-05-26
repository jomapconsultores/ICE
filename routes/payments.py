from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import Suscripcion, Pago, Usuario
from config import Config
from datetime import datetime, timedelta
import os, uuid, json

payments = Blueprint('payments', __name__)

if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)

def calcular_precio_plan(modulos_seleccionados, duracion_meses):
    modulos_mensuales = [m for m in modulos_seleccionados if m in Config.MODULOS and not Config.MODULOS[m].get('precio_unico', False)]
    modulos_unicos = [m for m in modulos_seleccionados if m in Config.MODULOS and Config.MODULOS[m].get('precio_unico', False)]
    subtotal_mensual = sum(Config.MODULOS[m]['precio'] for m in modulos_mensuales)
    subtotal_unico = sum(Config.MODULOS[m]['precio'] for m in modulos_unicos)
    subtotal_total = (subtotal_mensual * duracion_meses) + subtotal_unico
    if duracion_meses >= 3 and len(modulos_mensuales) >= 3:
        descuento_pct = Config.DURACIONES[duracion_meses]['descuento']
        descuento = (subtotal_mensual * duracion_meses) * (descuento_pct / 100)
    else:
        descuento_pct = 0
        descuento = 0
    subtotal_con_descuento = subtotal_total - descuento
    iva = subtotal_con_descuento * Config.IVA
    total = subtotal_con_descuento + iva
    return {
        'subtotal_mensual': round(subtotal_mensual, 2), 'subtotal_unico': round(subtotal_unico, 2),
        'subtotal_total': round(subtotal_total, 2), 'descuento_pct': descuento_pct,
        'descuento': round(descuento, 2), 'subtotal_final': round(subtotal_con_descuento, 2),
        'iva': round(iva, 2), 'total': round(total, 2),
        'duracion': Config.DURACIONES[duracion_meses]['nombre'], 'dias': Config.DURACIONES[duracion_meses]['dias'],
        'modulos_count': len(modulos_seleccionados), 'aplica_descuento': descuento_pct > 0
    }

def activar_suscripcion(usuario_id, modulos, duracion_meses, precio_total, descuento):
    suscripcion = Suscripcion.query.filter_by(usuario_id=usuario_id).first()
    dias = Config.DURACIONES[duracion_meses]['dias']
    ahora = datetime.utcnow()
    if suscripcion:
        if suscripcion.fecha_vencimiento and suscripcion.fecha_vencimiento < ahora:
            suscripcion.fecha_inicio = ahora
            suscripcion.fecha_vencimiento = ahora + timedelta(days=dias)
        else:
            if suscripcion.fecha_vencimiento:
                suscripcion.fecha_vencimiento = suscripcion.fecha_vencimiento + timedelta(days=dias)
            else:
                suscripcion.fecha_vencimiento = ahora + timedelta(days=dias)
        suscripcion.estado = 'activa'
        suscripcion.modulos_activos = json.dumps(modulos)
        suscripcion.precio_personalizado = precio_total
        suscripcion.duracion_meses = duracion_meses
        suscripcion.descuento_aplicado = descuento
        suscripcion.facturas_procesadas_mes = 0
    else:
        suscripcion = Suscripcion(usuario_id=usuario_id, plan_id='personalizado', estado='activa',
                                  fecha_inicio=ahora, fecha_vencimiento=ahora + timedelta(days=dias),
                                  modulos_activos=json.dumps(modulos), precio_personalizado=precio_total,
                                  duracion_meses=duracion_meses, descuento_aplicado=descuento)
        db.session.add(suscripcion)
    db.session.commit()

@payments.route('/planes')
def ver_planes():
    return render_template('payments/planes.html', modulos=Config.MODULOS, duraciones=Config.DURACIONES)

@payments.route('/calcular_precio', methods=['POST'])
def calcular_precio_ajax():
    data = request.get_json()
    modulos = data.get('modulos', [])
    duracion = int(data.get('duracion', 1))
    if duracion not in Config.DURACIONES: duracion = 1
    return jsonify(calcular_precio_plan(modulos, duracion))

@payments.route('/pagar_transferencia', methods=['POST'])
@login_required
def pagar_transferencia():
    modulos = request.form.getlist('modulos')
    duracion = int(request.form.get('duracion', 1))
    if not modulos:
        flash('Selecciona al menos un modulo.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    precios = calcular_precio_plan(modulos, duracion)
    if 'comprobante' not in request.files:
        flash('Debes subir el comprobante.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    archivo = request.files['comprobante']
    if archivo.filename == '':
        flash('Selecciona un archivo.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    ext = archivo.filename.rsplit('.', 1)[-1].lower()
    nombre = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    ruta = os.path.join(Config.UPLOAD_FOLDER, nombre)
    archivo.save(ruta)
    pago = Pago(usuario_id=current_user.id, plan_id='personalizado', metodo='transferencia',
                monto=precios['total'], estado='pendiente', comprobante_ruta=ruta,
                referencia=json.dumps({'modulos': modulos, 'duracion': duracion}))
    db.session.add(pago)
    db.session.commit()
    flash('Comprobante subido. Un administrador activara tu cuenta.', 'success')
    return redirect(url_for('payments.mis_pagos'))

@payments.route('/mis_pagos')
@login_required
def mis_pagos():
    pagos = Pago.query.filter_by(usuario_id=current_user.id).order_by(Pago.fecha_pago.desc()).all()
    return render_template('payments/mis_pagos.html', pagos=pagos)

@payments.route('/admin')
@login_required
def admin_panel():
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    pagos_pendientes = Pago.query.filter_by(estado='pendiente').order_by(Pago.fecha_pago.desc()).all()
    usuarios = Usuario.query.all()
    return render_template('payments/admin.html', pagos_pendientes=pagos_pendientes, usuarios=usuarios,
                         modulos_info=Config.MODULOS, duraciones=Config.DURACIONES)

@payments.route('/admin/aprobar/<int:pago_id>')
@login_required
def aprobar_pago(pago_id):
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    pago = Pago.query.get(pago_id)
    if pago and pago.estado == 'pendiente':
        datos = json.loads(pago.referencia or '{}')
        modulos = datos.get('modulos', [])
        duracion = datos.get('duracion', 1)
        activar_suscripcion(pago.usuario_id, modulos, duracion, pago.monto, 0)
        pago.estado = 'aprobado'
        pago.fecha_aprobacion = datetime.utcnow()
        pago.admin_notas = 'Pago aprobado'
        db.session.commit()
        flash('Pago aprobado. Suscripcion activada.', 'success')
    return redirect(url_for('payments.admin_panel'))

@payments.route('/admin/rechazar/<int:pago_id>', methods=['POST'])
@login_required
def rechazar_pago(pago_id):
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    pago = Pago.query.get(pago_id)
    if pago:
        pago.estado = 'rechazado'
        pago.admin_notas = request.form.get('motivo', 'Pago rechazado')
        db.session.commit()
        flash('Pago rechazado.', 'warning')
    return redirect(url_for('payments.admin_panel'))