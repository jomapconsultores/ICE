from models import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(200))
    ruc = db.Column(db.String(13))
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    suscripcion = db.relationship('Suscripcion', backref='usuario', lazy=True, uselist=False)
    facturas = db.relationship('Factura', backref='usuario', lazy=True)
    pagos = db.relationship('Pago', backref='usuario', lazy=True)
    empresas = db.relationship('Empresa', backref='usuario', lazy=True)
    ips_autorizadas = db.relationship('IpAutorizada', backref='usuario', lazy=True)
    solicitudes_ip = db.relationship('SolicitudIp', backref='usuario', lazy=True)
    licores = db.relationship('ProductoLicor', backref='usuario', lazy=True)
    clasificaciones = db.relationship('ClasificacionGasto', backref='usuario', lazy=True)
    mapas_clasificacion = db.relationship('MapaClasificacion', backref='usuario', lazy=True)
    
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def tiene_suscripcion_activa(self):
        if self.suscripcion and self.suscripcion.estado == 'activa':
            return self.suscripcion.fecha_vencimiento > datetime.utcnow()
        return False

class Suscripcion(db.Model):
    __tablename__ = 'suscripcion'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    plan_id = db.Column(db.String(50), default='personalizado')
    estado = db.Column(db.String(20), default='inactivo')
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    modulos_activos = db.Column(db.Text, default='[]')
    precio_personalizado = db.Column(db.Numeric(10, 2))
    duracion_meses = db.Column(db.Integer, default=1)
    descuento_aplicado = db.Column(db.Integer, default=0)
    empresa_actual_id = db.Column(db.Integer, nullable=True)
    facturas_procesadas_mes = db.Column(db.Integer, default=0)

class Factura(db.Model):
    __tablename__ = 'factura'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)
    clave_acceso = db.Column(db.String(49), unique=True, nullable=False)
    ruc_emisor = db.Column(db.String(13))
    razon_social_emisor = db.Column(db.String(300))
    ruc_comprador = db.Column(db.String(13))
    razon_social_comprador = db.Column(db.String(300))
    fecha_emision = db.Column(db.Date)
    numero_factura = db.Column(db.String(50))
    importe_total = db.Column(db.Numeric(12,2))
    base_ice = db.Column(db.Numeric(12,2))
    valor_ice = db.Column(db.Numeric(12,2))
    base_iva = db.Column(db.Numeric(12,2))
    valor_iva = db.Column(db.Numeric(12,2))
    xml_original = db.Column(db.Text)
    fecha_procesamiento = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(10), default='gasto')

class CatalogoProducto(db.Model):
    __tablename__ = 'catalogo_producto'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    nombre = db.Column(db.String(300), nullable=False)
    cod_marca = db.Column(db.String(6), default='000000')
    cod_impuesto = db.Column(db.String(4), default='3031')
    cod_clasificacion = db.Column(db.String(3), default='057')
    presentacion = db.Column(db.String(3), default='013')
    capacidad = db.Column(db.String(6), default='000750')
    unidad = db.Column(db.String(2), default='66')
    grado_alcoholico = db.Column(db.String(6), default='000015')
    cod_pais = db.Column(db.String(3), default='593')
    es_pack = db.Column(db.Boolean, default=False)
    unidades_por_caja = db.Column(db.Integer, default=12)

class Pago(db.Model):
    __tablename__ = 'pago'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    plan_id = db.Column(db.String(50), nullable=False)
    metodo = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    comprobante_ruta = db.Column(db.String(500))
    referencia = db.Column(db.Text)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_aprobacion = db.Column(db.DateTime)
    admin_notas = db.Column(db.Text)

class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    nombre = db.Column(db.String(300), nullable=False)
    ruc = db.Column(db.String(13), nullable=False)
    razon_social = db.Column(db.String(300))
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class IpAutorizada(db.Model):
    __tablename__ = 'ip_autorizada'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    direccion_ip = db.Column(db.String(45), nullable=False)
    fecha_agregada = db.Column(db.DateTime, default=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)

class SolicitudIp(db.Model):
    __tablename__ = 'solicitud_ip'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    direccion_ip = db.Column(db.String(45), nullable=False)
    justificacion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)

class ClasificacionGasto(db.Model):
    __tablename__ = 'clasificacion_gasto'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('factura.id'))
    categoria = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(12,2))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class ProductoLicor(db.Model):
    __tablename__ = 'producto_licor'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50))
    precio_fabrica = db.Column(db.Numeric(10,2))
    volumen_cc = db.Column(db.Integer, default=750)
    grado_alcoholico = db.Column(db.Numeric(5,2), default=35)
    codigo_sri = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class FacturaEmitida(db.Model):
    __tablename__ = 'factura_emitida'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    numero_factura = db.Column(db.String(50))
    monto = db.Column(db.Numeric(10,2))
    fecha_emision = db.Column(db.Date)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_pago = db.Column(db.DateTime)
    admin_notas = db.Column(db.Text)

class MapaClasificacion(db.Model):
    __tablename__ = 'mapa_clasificacion'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)
    nombre = db.Column(db.String(200))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

class MapaClasificacionDetalle(db.Model):
    __tablename__ = 'mapa_clasificacion_detalle'
    id = db.Column(db.Integer, primary_key=True)
    mapa_id = db.Column(db.Integer, db.ForeignKey('mapa_clasificacion.id'))
    ruc = db.Column(db.String(13), nullable=False)
    nombre_proveedor = db.Column(db.String(300))
    categoria = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))