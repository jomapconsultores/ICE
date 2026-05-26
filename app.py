from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, login_manager
from routes.auth import auth
from routes.payments import payments
from routes.invoices import invoices
from routes.ice import ice
from routes.catalog import catalog
from routes.annexes import annexes
from routes.exports import exports
from routes.downloader import downloader
from routes.empresas import empresas
from routes.security import security
from routes.admin_reports import admin_reports
from routes.gastos import gastos
from flask_login import login_required, current_user
import json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(payments, url_prefix='/payments')
    app.register_blueprint(invoices, url_prefix='/invoices')
    app.register_blueprint(ice, url_prefix='/ice')
    app.register_blueprint(catalog, url_prefix='/catalog')
    app.register_blueprint(annexes, url_prefix='/annexes')
    app.register_blueprint(exports, url_prefix='/exports')
    app.register_blueprint(downloader, url_prefix='/downloader')
    app.register_blueprint(empresas, url_prefix='/empresas')
    app.register_blueprint(security, url_prefix='/security')
    app.register_blueprint(admin_reports, url_prefix='/admin')
    app.register_blueprint(gastos, url_prefix='/gastos')
    with app.app_context(): db.create_all()
    return app

app = create_app()

def obtener_ip():
    if request.headers.get('X-Forwarded-For'): return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def verificar_ip_usuario():
    if not current_user.is_authenticated: return True, None
    ip = obtener_ip()
    if current_user.email == 'admin@test.com': return True, None
    from models.user import IpAutorizada
    ips_activas = IpAutorizada.query.filter_by(usuario_id=current_user.id, activa=True).all()
    if not ips_activas:
        nueva = IpAutorizada(usuario_id=current_user.id, direccion_ip=ip)
        db.session.add(nueva); db.session.commit()
        return True, None
    for ip_reg in ips_activas:
        if ip_reg.direccion_ip == ip: return True, None
    return False, {'ip_actual': ip, 'ips_autorizadas': [i.direccion_ip for i in ips_activas], 'cantidad': len(ips_activas)}

@app.before_request
def verificar_acceso_ip():
    rutas_publicas = ['/auth/login', '/auth/register', '/auth/logout', '/bienvenido', '/static']
    for ruta in rutas_publicas:
        if request.path.startswith(ruta): return None
    if current_user.is_authenticated:
        if current_user.email == 'admin@test.com': return None
        autorizado, info = verificar_ip_usuario()
        if not autorizado:
            if request.path.startswith('/security/solicitar_ip') or request.path.startswith('/dashboard'): return None
            flash('IP no autorizada.', 'danger')
            return redirect(url_for('security.solicitar_ip'))

@app.context_processor
def utility_processor():
    def tiene_modulo(modulo_id):
        if not current_user.is_authenticated: return False
        if not current_user.tiene_suscripcion_activa(): return False
        try: modulos = json.loads(current_user.suscripcion.modulos_activos or '[]')
        except: modulos = []
        if modulo_id == 'catalogo' and 'facturas_ilimitadas' in modulos: return True
        return modulo_id in modulos
    def suscripcion_activa():
        if not current_user.is_authenticated: return False
        return current_user.tiene_suscripcion_activa()
    return dict(tiene_modulo=tiene_modulo, suscripcion_activa=suscripcion_activa)

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    from models.user import Factura
    total_facturas = Factura.query.filter_by(usuario_id=current_user.id).count()
    return render_template('dashboard.html', total_facturas=total_facturas)

@app.route('/bienvenido')
def bienvenido():
    return render_template('bienvenido.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)