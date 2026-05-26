from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import Usuario, Pago, FacturaEmitida
from datetime import datetime
from sqlalchemy import func, extract

admin_reports = Blueprint('admin_reports', __name__)


def requiere_admin():
    if not current_user.is_admin:
        flash('Acceso denegado.', 'danger')
        return False
    return True


@admin_reports.route('/reportes')
@login_required
def reportes():
    if not requiere_admin():
        return redirect(url_for('dashboard'))

    recaudacion_usuarios = db.session.query(
        Usuario.nombre,
        func.sum(Pago.monto).label('total'),
        func.count(Pago.id).label('cantidad')
    ).join(Pago, Pago.usuario_id == Usuario.id)\
     .filter(Pago.estado == 'aprobado')\
     .group_by(Usuario.id).all()

    recaudacion_mensual = db.session.query(
        extract('year', Pago.fecha_pago).label('anio'),
        extract('month', Pago.fecha_pago).label('mes'),
        func.sum(Pago.monto).label('total'),
        func.count(Pago.id).label('cantidad')
    ).filter(Pago.estado == 'aprobado')\
     .group_by('anio', 'mes').order_by('anio', 'mes').all()

    facturas_pendientes = FacturaEmitida.query\
        .filter_by(estado='pendiente')\
        .order_by(FacturaEmitida.fecha_emision).all()

    total_recaudado = db.session.query(func.sum(Pago.monto))\
        .filter(Pago.estado == 'aprobado').scalar() or 0

    usuarios = Usuario.query.order_by(Usuario.nombre).all()

    return render_template('admin/reportes.html',
                           recaudacion_usuarios=recaudacion_usuarios,
                           recaudacion_mensual=recaudacion_mensual,
                           facturas_pendientes=facturas_pendientes,
                           total_recaudado=total_recaudado,
                           usuarios=usuarios)


@admin_reports.route('/marcar_factura/<int:factura_id>', methods=['POST'])
@login_required
def marcar_factura(factura_id):
    if not requiere_admin():
        return redirect(url_for('dashboard'))

    factura = db.session.get(FacturaEmitida, factura_id)
    if factura:
        factura.estado = 'emitida'
        factura.fecha_pago = datetime.utcnow()
        db.session.commit()
        flash(f'Factura #{factura_id} marcada como emitida.', 'success')
    else:
        flash('Factura no encontrada.', 'danger')
    return redirect(url_for('admin_reports.reportes'))


@admin_reports.route('/generar_factura', methods=['POST'])
@login_required
def generar_factura():
    if not requiere_admin():
        return redirect(url_for('dashboard'))

    try:
        usuario_id = int(request.form.get('usuario_id'))
        monto = float(request.form.get('monto'))
        if monto <= 0:
            flash('El monto debe ser mayor a 0.', 'warning')
            return redirect(url_for('admin_reports.reportes'))

        numero = f"F-{datetime.utcnow().strftime('%Y%m%d')}-{usuario_id}"
        factura = FacturaEmitida(
            usuario_id=usuario_id,
            monto=monto,
            fecha_emision=datetime.utcnow().date(),
            estado='pendiente',
            numero_factura=numero
        )
        db.session.add(factura)
        db.session.commit()
        flash(f'Factura {numero} generada para emisión.', 'success')
    except (ValueError, TypeError):
        flash('Datos inválidos para generar la factura.', 'danger')

    return redirect(url_for('admin_reports.reportes'))
