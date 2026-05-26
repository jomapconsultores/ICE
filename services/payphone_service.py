import requests
import json
from config import Config

class PayPhoneService:
    API_URL = "https://pay.payphonetodoesposible.com/api"
    
    @staticmethod
    def get_token():
        if Config.PAYPHONE_CLIENT_ID == 'TU_CLIENT_ID':
            return None
        
        try:
            response = requests.post(
                f"{PayPhoneService.API_URL}/v1/auth/token",
                json={
                    "client_id": Config.PAYPHONE_CLIENT_ID,
                    "client_secret": Config.PAYPHONE_CLIENT_SECRET
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('token')
            return None
        except Exception as e:
            print(f"Error PayPhone token: {e}")
            return None
    
    @staticmethod
    def crear_pago(monto, usuario_email, descripcion, transaction_id):
        token = PayPhoneService.get_token()
        
        if not token:
            return None, None
        
        try:
            payload = {
                "amount": monto,
                "amountWithoutTax": round(monto / 1.15, 2),
                "amountWithTax": round(monto * 0.15, 2),
                "tax": round(monto * 0.15, 2),
                "clientTransactionId": transaction_id,
                "responseUrl": f"{Config.BASE_URL}/payments/respuesta_payphone",
                "cancellationUrl": f"{Config.BASE_URL}/payments/planes",
                "reference": descripcion,
                "phoneNumber": "0999999999",
                "email": usuario_email
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{PayPhoneService.API_URL}/v1/button/pay",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('payUrl'), None
            else:
                return None, f"Error PayPhone: {response.text}"
        
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    @staticmethod
    def verificar_pago(transaction_id):
        token = PayPhoneService.get_token()
        if not token:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{PayPhoneService.API_URL}/v1/button/validate/{transaction_id}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None