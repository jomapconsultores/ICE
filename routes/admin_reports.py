from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import Usuario, Pago, FacturaEmitida
from config import Config
from datetime import datetime
from sqlalchemy import func, extract

admin_reports = Blueprint('admin_reports', __name__)

@admin_reports.route('/reportes')
@login_required
def reportes():
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    recaudacion_usuarios = db.session.query(
        Usuario.nombre, func.sum(Pago.monto).label('total'), func.count(Pago.id).label('cantidad')
    ).join(Pago).filter(Pago.estado == 'aprobado').group_by(Usuario.id).all()
    
    recaudacion_mensual = db.session.query(
        extract('year', Pago.fecha_pago).label('anio'), extract('month', Pago.fecha_pago).label('mes'),
        func.sum(Pago.monto).label('total'), func.count(Pago.id).label('cantidad')
    ).filter(Pago.estado == 'aprobado').group_by('anio', 'mes').order_by('anio', 'mes').all()
    
    facturas_pendientes = FacturaEmitida.query.filter_by(estado='pendiente').order_by(FacturaEmitida.fecha_emision).all()
    total_recaudado = db.session.query(func.sum(Pago.monto)).filter(Pago.estado == 'aprobado').scalar() or 0
    usuarios = Usuario.query.all()
    
    return render_template('admin/reportes.html', recaudacion_usuarios=recaudacion_usuarios,
                         recaudacion_mensual=recaudacion_mensual, facturas_pendientes=facturas_pendientes,
                         total_recaudado=total_recaudado, usuarios=usuarios)

@admin_reports.route('/marcar_factura/<int:factura_id>')
@login_required
def marcar_factura(factura_id):
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    factura = FacturaEmitida.query.get(factura_id)
    if factura:
        factura.estado = 'emitida'
        factura.fecha_pago = datetime.utcnow()
        db.session.commit()
        flash(f'Factura #{factura_id} marcada como emitida.', 'success')
    return redirect(url_for('admin_reports.reportes'))

@admin_reports.route('/generar_factura/<int:usuario_id>/<float:monto>')
@login_required
def generar_factura(usuario_id, monto):
    if current_user.email != 'admin@test.com':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    factura = FacturaEmitida(usuario_id=usuario_id, monto=monto, fecha_emision=datetime.utcnow().date(),
                            estado='pendiente', numero_factura=f'F-{datetime.utcnow().strftime("%Y%m%d")}-{usuario_id}')
    db.session.add(factura)
    db.session.commit()
    flash('Factura generada para emision.', 'success')
    return redirect(url_for('admin_reports.reportes'))