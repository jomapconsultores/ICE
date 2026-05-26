from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.user import CatalogoProducto, ProductoLicor, ClasificacionGasto, Factura

catalog = Blueprint('catalog', __name__)

CATALOGO_INICIAL = [
    {'nombre': 'LICOR ORO 15V 750 ML (12U)', 'cod_marca': '000001', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000750', 'unidad': '66', 'grado_alcoholico': '000015', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'LICOR SECO BLANCO 15V 750 ML (12U)', 'cod_marca': '000002', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000750', 'unidad': '66', 'grado_alcoholico': '000015', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'AGUARDIENTE DE CANA 15V 750 ML (12U)', 'cod_marca': '000003', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000750', 'unidad': '66', 'grado_alcoholico': '000015', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'VODKA SECO GLACIAL 15V 750ML (12U)', 'cod_marca': '000004', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000750', 'unidad': '66', 'grado_alcoholico': '000015', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'COCKTAIL MARACUYA 5V 800ML (12U)', 'cod_marca': '000005', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000800', 'unidad': '66', 'grado_alcoholico': '000005', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'COCKTAIL DURAZNO 5V 800ML (12U)', 'cod_marca': '000006', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000800', 'unidad': '66', 'grado_alcoholico': '000005', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
    {'nombre': 'COCKTAIL GUARANA 5V 750ML (12U)', 'cod_marca': '000007', 'cod_impuesto': '3031', 'cod_clasificacion': '057', 'presentacion': '013', 'capacidad': '000750', 'unidad': '66', 'grado_alcoholico': '000005', 'cod_pais': '593', 'es_pack': False, 'unidades_por_caja': 12},
]

GASTOS_PERSONALES = ['ALIMENTACION', 'EDUCACION', 'SALUD', 'VESTIMENTA', 'VIVIENDA', 'TURISMO', 'ARTE Y CULTURA', 'VARIOS']

# ==================== CATÁLOGO DE PRODUCTOS (Licores) ====================

@catalog.route('/ver')
@login_required
def ver_catalogo():
    """Catálogo de productos (licores)"""
    productos = CatalogoProducto.query.filter_by(usuario_id=current_user.id).order_by(CatalogoProducto.nombre).all()
    return render_template('catalog/ver.html', productos=productos)

@catalog.route('/inicializar', methods=['POST'])
@login_required
def inicializar_catalogo():
    existentes = CatalogoProducto.query.filter_by(usuario_id=current_user.id).count()
    if existentes > 0:
        flash('El catalogo ya tiene productos.', 'info')
        return redirect(url_for('catalog.ver_catalogo'))
    for prod in CATALOGO_INICIAL:
        p = CatalogoProducto(usuario_id=current_user.id, nombre=prod['nombre'], cod_marca=prod['cod_marca'],
                            cod_impuesto=prod['cod_impuesto'], cod_clasificacion=prod['cod_clasificacion'],
                            presentacion=prod['presentacion'], capacidad=prod['capacidad'],
                            unidad=prod['unidad'], grado_alcoholico=prod['grado_alcoholico'],
                            cod_pais=prod['cod_pais'], es_pack=prod['es_pack'],
                            unidades_por_caja=prod['unidades_por_caja'])
        db.session.add(p)
    db.session.commit()
    flash('Catalogo inicializado con 7 productos.', 'success')
    return redirect(url_for('catalog.ver_catalogo'))

@catalog.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        producto = CatalogoProducto(usuario_id=current_user.id, nombre=request.form.get('nombre', '').upper(),
                                   cod_marca=request.form.get('cod_marca', '000000').zfill(6),
                                   cod_impuesto=request.form.get('cod_impuesto', '3031'),
                                   cod_clasificacion=request.form.get('cod_clasificacion', '057'),
                                   presentacion=request.form.get('presentacion', '013').zfill(3),
                                   capacidad=request.form.get('capacidad', '000750').zfill(6),
                                   unidad=request.form.get('unidad', '66'),
                                   grado_alcoholico=request.form.get('grado_alcoholico', '000015').zfill(6),
                                   cod_pais=request.form.get('cod_pais', '593'),
                                   es_pack=request.form.get('es_pack') == 'on',
                                   unidades_por_caja=int(request.form.get('unidades_por_caja', 12)))
        db.session.add(producto)
        db.session.commit()
        flash('Producto agregado.', 'success')
        return redirect(url_for('catalog.ver_catalogo'))
    return render_template('catalog/agregar.html')

@catalog.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = CatalogoProducto.query.filter_by(id=id, usuario_id=current_user.id).first()
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('catalog.ver_catalogo'))
    if request.method == 'POST':
        producto.nombre = request.form.get('nombre', producto.nombre).upper()
        producto.cod_marca = request.form.get('cod_marca', producto.cod_marca).zfill(6)
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('catalog.ver_catalogo'))
    return render_template('catalog/editar.html', producto=producto)

@catalog.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = CatalogoProducto.query.filter_by(id=id, usuario_id=current_user.id).first()
    if producto:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado.', 'success')
    return redirect(url_for('catalog.ver_catalogo'))

# ==================== LICORES DEL USUARIO ====================

@catalog.route('/licores')
@login_required
def ver_licores():
    licores = ProductoLicor.query.filter_by(usuario_id=current_user.id).order_by(ProductoLicor.nombre).all()
    return render_template('catalog/licores.html', licores=licores)

@catalog.route('/licores/agregar', methods=['GET', 'POST'])
@login_required
def agregar_licor():
    if request.method == 'POST':
        licor = ProductoLicor(usuario_id=current_user.id, nombre=request.form.get('nombre', ''),
                             tipo=request.form.get('tipo', 'Licor'),
                             precio_fabrica=float(request.form.get('precio_fabrica', 0)),
                             volumen_cc=int(request.form.get('volumen_cc', 750)),
                             grado_alcoholico=float(request.form.get('grado_alcoholico', 35)),
                             codigo_sri=request.form.get('codigo_sri', ''))
        db.session.add(licor)
        db.session.commit()
        flash('Licor agregado.', 'success')
        return redirect(url_for('catalog.ver_licores'))
    return render_template('catalog/agregar_licor.html')

# ==================== CLASIFICACIÓN DE GASTOS ====================

@catalog.route('/gastos')
@login_required
def ver_gastos():
    """Ver facturas de gasto clasificadas"""
    facturas_gasto = Factura.query.filter_by(usuario_id=current_user.id, tipo='gasto').order_by(Factura.fecha_emision.desc()).all()
    clasificaciones = ClasificacionGasto.query.filter_by(usuario_id=current_user.id).order_by(ClasificacionGasto.fecha.desc()).all()
    
    # Resumen por categoría
    from sqlalchemy import func
    resumen = db.session.query(ClasificacionGasto.categoria, func.sum(ClasificacionGasto.monto).label('total'), func.count(ClasificacionGasto.id).label('cantidad'))\
                        .filter_by(usuario_id=current_user.id).group_by(ClasificacionGasto.categoria).all()
    
    return render_template('catalog/gastos.html', facturas=facturas_gasto, clasificaciones=clasificaciones, resumen=resumen, categorias=GASTOS_PERSONALES)

@catalog.route('/gastos/clasificar/<int:factura_id>', methods=['POST'])
@login_required
def clasificar_gasto(factura_id):
    """Clasifica una factura de gasto en una categoría"""
    factura = Factura.query.filter_by(id=factura_id, usuario_id=current_user.id).first()
    if not factura:
        flash('Factura no encontrada.', 'danger')
        return redirect(url_for('catalog.ver_gastos'))
    
    categoria = request.form.get('categoria', 'VARIOS')
    
    # Verificar si ya está clasificada
    existente = ClasificacionGasto.query.filter_by(factura_id=factura_id).first()
    if existente:
        existente.categoria = categoria
    else:
        clasificacion = ClasificacionGasto(usuario_id=current_user.id, factura_id=factura_id, categoria=categoria, monto=factura.importe_total, fecha=datetime.utcnow())
        db.session.add(clasificacion)
    
    db.session.commit()
    flash(f'Factura clasificada como {categoria}.', 'success')
    return redirect(url_for('catalog.ver_gastos'))