import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-super-secreta-cambiar-en-produccion')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sistema_ice.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    BANCO_NOMBRE = 'Produbanco'
    BANCO_CUENTA = '27059106889'
    BANCO_TIPO = 'Corriente'
    BANCO_TITULAR = 'CMAJ ASOCIADOS SAS'
    BANCO_RUC = '0195146942001'
    BANCO_EMAIL = 'jomapconsultores@outlook.com'
    BANCO_CELULAR = '0963511411'
    
    IVA = 0.15
    
    DURACIONES = {
        1: {'nombre': '1 Mes', 'descuento': 0, 'dias': 30},
        3: {'nombre': '3 Meses', 'descuento': 5, 'dias': 90},
        6: {'nombre': '6 Meses', 'descuento': 8, 'dias': 180},
        9: {'nombre': '9 Meses', 'descuento': 12, 'dias': 270},
        12: {'nombre': '1 Año', 'descuento': 15, 'dias': 365}
    }
    
    MODULOS = {
        'facturas_ilimitadas': {
            'nombre': 'Facturas Ilimitadas (Gastos + Ingresos)',
            'descripcion': 'Sube XMLs de gastos e ingresos con arrastre.',
            'tooltip': 'Incluye Catalogo GRATIS. Procesa XMLs, clasifica gastos, calcula ICE.',
            'precio': 10.00, 'precio_unico': False, 'icono': 'receipt', 'color': 'primary', 'incluye_catalogo': True
        },
        'calculo_ice_simple': {
            'nombre': 'Calculo ICE Simple',
            'descripcion': 'Calculadora individual de ICE.',
            'tooltip': 'Calcula ICE especifico, ad-valorem y PVP final.',
            'precio': 5.00, 'precio_unico': False, 'icono': 'calculator', 'color': 'success'
        },
        'calculo_ice_avanzado': {
            'nombre': 'Calculo ICE Avanzado',
            'descripcion': 'Calculo multiple y mezcla total.',
            'tooltip': 'Multi-Producto y Mezcla Total.',
            'precio': 15.00, 'precio_unico': False, 'icono': 'diagram-3', 'color': 'success'
        },
        'anexos_sri': {
            'nombre': 'Anexos SRI ICE/PVP',
            'descripcion': 'Genera XMLs oficiales para el SRI.',
            'tooltip': 'XMLs listos para cargar al portal del SRI.',
            'precio': 15.00, 'precio_unico': False, 'icono': 'file-earmark-xml', 'color': 'danger'
        },
        'exportar_excel': {
            'nombre': 'Exportar a Excel',
            'descripcion': 'Descarga reportes en Excel profesional.',
            'tooltip': 'Declaraciones, auditorias, resumenes.',
            'precio': 5.00, 'precio_unico': False, 'icono': 'file-earmark-excel', 'color': 'success'
        },
        'descarga_sri': {
            'nombre': 'Descarga Masiva SRI + Bookmarklet',
            'descripcion': 'Descarga facturas desde TXT y Bookmarklet.',
            'tooltip': 'PAGO UNICO. Incluye guia de instalacion.',
            'precio': 15.00, 'precio_unico': True, 'icono': 'cloud-download', 'color': 'dark'
        },
        'soporte': {
            'nombre': 'Soporte Prioritario 24/7',
            'descripcion': 'Atencion personalizada.',
            'tooltip': 'Respuesta en menos de 1 hora.',
            'precio': 5.00, 'precio_unico': False, 'icono': 'headset', 'color': 'info'
        },
        'clasificacion_gastos': {
            'nombre': 'Clasificacion de Gastos SRI',
            'descripcion': 'Clasifica facturas de gasto por RUC. Separa Gastos Personales del Ejercicio.',
            'tooltip': 'Sube mapa Excel. Auto-clasifica por proveedor. Exporta resumenes.',
            'precio': 10.00, 'precio_unico': False, 'icono': 'tags', 'color': 'warning'
        }
    }
    
    UPLOAD_FOLDER = 'uploads/comprobantes'