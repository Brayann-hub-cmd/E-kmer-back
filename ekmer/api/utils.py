import jwt
from django.conf import settings
from .models import Users
import requests

CHECKOUT_BASE_URL = "https://api-checkout.cinetpay.com/v2"
TRANSFER_BASE_URL = "https://client.cinetpay.com/v1"
def verifier_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None,"Token Manquant,connectez vous!"
    if not auth_header.startswith('Bearer '):
        return None, "Format du token invalide"
    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        user = Users.objects.get(id=payload['id'])
        return user,None
    except Exception as e:
        return None,str(e)
    except jwt.ExpiredSignatureError:
        return None,"Token expiré, reconnectez vous ..."
    except jwt.DecodeError:
        return None,"Token invalide !"
    except Users.DoesNotExist:
        return None, "Utilisateur introuvable"

class CinetPayError(Exception):
    pass


def get_payment_client():
   
    if getattr(settings, 'PAIEMENT_MODE', 'simulation') == 'production':
        return CinetPayClient()
    return SimulateurPaiementClient()


class CinetPayClient:
    def __init__(self):
        self.apikey = settings.CINETPAY_API_KEY
        self.site_id = settings.CINETPAY_SITE_ID
        self.transfer_login = settings.CINETPAY_TRANSFER_LOGIN
        self.transfer_password = settings.CINETPAY_TRANSFER_PASSWORD

    def initier_paiement(self, transaction_id, montant, description, client, notify_url, return_url):
        payload = {
            "apikey": self.apikey,
            "site_id": self.site_id,
            "transaction_id": transaction_id,
            "amount": int(montant),
            "currency": "XAF",
            "description": description,
            "customer_name": client.get("nom", ""),
            "customer_surname": client.get("prenom", ""),
            "customer_phone_number": client.get("telephone", ""),
            "customer_email": client.get("email", ""),
            "customer_address": client.get("adresse", "Douala"),
            "customer_city": client.get("ville", "Douala"),
            "customer_country": "CM",
            "customer_state": "CM",
            "customer_zip_code": "00000",
            "notify_url": notify_url,
            "return_url": return_url,
            "channels": "MOBILE_MONEY",
        }
        response = requests.post(f"{CHECKOUT_BASE_URL}/payment", json=payload, timeout=15)
        data = response.json()
        if data.get("code") != "201":
            raise CinetPayError(data.get("description", "Échec initialisation paiement"))
        return data["data"]  # contient payment_token et payment_url

    def verifier_paiement(self, transaction_id):
        payload = {
            "apikey": self.apikey,
            "site_id": self.site_id,
            "transaction_id": transaction_id,
        }
        response = requests.post(f"{CHECKOUT_BASE_URL}/payment/check", json=payload, timeout=15)
        return response.json()

    def _get_transfer_token(self):
        payload = {"apikey": self.transfer_login, "password": self.transfer_password}
        response = requests.post(f"{TRANSFER_BASE_URL}/auth/login", data=payload, timeout=15)
        data = response.json()
        if data.get("code") != 0:
            raise CinetPayError(data.get("message", "Échec authentification transfert"))
        return data["data"]["token"]

    def initier_remboursement(self, client_transaction_id, montant, numero_telephone, notify_url):
        token = self._get_transfer_token()
        payload = [{
            "prefix": "237",
            "phone": numero_telephone,
            "amount": int(montant),
            "client_transaction_id": client_transaction_id,
            "notify_url": notify_url,
        }]
        response = requests.post(
            f"{TRANSFER_BASE_URL}/transfer/money/send/contact",
            params={"token": token},
            json=payload,
            timeout=15,
        )
        data = response.json()
        if data.get("code") != 0:
            raise CinetPayError(data.get("message", "Échec initiation remboursement"))
        return data["data"][0]  # contient transaction_id CinetPay, treatment_status...


class SimulateurPaiementClient:

    def initier_paiement(self, transaction_id, montant, description, client, notify_url, return_url):
        return {
            "payment_token": f"SIMU-TOKEN-{transaction_id}",
            "payment_url": f"http://simulation.local/paiement/{transaction_id}",
        }

    def verifier_paiement(self, transaction_id):
        return {
            "code": "00",
            "data": {"status": "ACCEPTED", "payment_method": "SIMULATION"},
        }

    def initier_remboursement(self, client_transaction_id, montant, numero_telephone, notify_url):
        return {
            "transaction_id": f"SIMU-REMB-{client_transaction_id}",
            "treatment_status": "VAL",  # simulé comme déjà validé
        }
    