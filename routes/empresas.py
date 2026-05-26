from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.user import Empresa

empresas = Blueprint('empresas', __name__)


@empresas.route('/mis_empresas')
@login_required
def mis_empresas():
    if not current_user.tiene_suscripcion_activa():
        flash('Necesitas una suscripcion activa.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    
    if current_user.suscripcion.plan_id != 'empresarial':
        flash('El plan multi-empresa es exclusivo del Plan Empresarial.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    
    empresas = Empresa.query.filter_by(usuario_id=current_user.id, activa=True).all()
    return render_template('empresas/mis_empresas.html', empresas=empresas)


@empresas.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar_empresa():
    if current_user.suscripcion.plan_id != 'empresarial':
        flash('Plan Empresarial requerido.', 'warning')
        return redirect(url_for('payments.ver_planes'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        ruc = request.form.get('ruc', '').strip()
        razon_social = request.form.get('razon_social', '').strip()
        
        if not nombre or not ruc:
            flash('Nombre y RUC son obligatorios.', 'warning')
            return render_template('empresas/agregar.html')
        
        existente = Empresa.query.filter_by(usuario_id=current_user.id, ruc=ruc).first()
        if existente:
            flash('Ya tienes registrada una empresa con ese RUC.', 'warning')
            return render_template('empresas/agregar.html')
        
        empresa = Empresa(
            usuario_id=current_user.id,
            nombre=nombre,
            ruc=ruc,
            razon_social=razon_social
        )
        db.session.add(empresa)
        
        if current_user.suscripcion.empresa_actual_id is None:
            db.session.flush()
            current_user.suscripcion.empresa_actual_id = empresa.id
        
        db.session.commit()
        flash(f'Empresa "{nombre}" agregada correctamente.', 'success')
        return redirect(url_for('empresas.mis_empresas'))
    
    return render_template('empresas/agregar.html')


@empresas.route('/seleccionar/<int:empresa_id>')
@login_required
def seleccionar_empresa(empresa_id):
    empresa = Empresa.query.filter_by(id=empresa_id, usuario_id=current_user.id).first()
    
    if not empresa:
        flash('Empresa no encontrada.', 'danger')
        return redirect(url_for('empresas.mis_empresas'))
    
    current_user.suscripcion.empresa_actual_id = empresa_id
    db.session.commit()
    
    flash(f'Empresa actual: {empresa.nombre}', 'success')
    return redirect(url_for('dashboard'))


@empresas.route('/editar/<int:empresa_id>', methods=['GET', 'POST'])
@login_required
def editar_empresa(empresa_id):
    empresa = Empresa.query.filter_by(id=empresa_id, usuario_id=current_user.id).first()
    
    if not empresa:
        flash('Empresa no encontrada.', 'danger')
        return redirect(url_for('empresas.mis_empresas'))
    
    if request.method == 'POST':
        empresa.nombre = request.form.get('nombre', empresa.nombre).strip()
        empresa.ruc = request.form.get('ruc', empresa.ruc).strip()
        empresa.razon_social = request.form.get('razon_social', empresa.razon_social).strip()
        db.session.commit()
        flash('Empresa actualizada.', 'success')
        return redirect(url_for('empresas.mis_empresas'))
    
    return render_template('empresas/editar.html', empresa=empresa)


@empresas.route('/desactivar/<int:empresa_id>')
@login_required
def desactivar_empresa(empresa_id):
    empresa = Empresa.query.filter_by(id=empresa_id, usuario_id=current_user.id).first()
    
    if empresa:
        empresa.activa = False
        if current_user.suscripcion.empresa_actual_id == empresa_id:
            current_user.suscripcion.empresa_actual_id = None
        db.session.commit()
        flash(f'Empresa "{empresa.nombre}" desactivada.', 'info')
    
    return redirect(url_for('empresas.mis_empresas'))