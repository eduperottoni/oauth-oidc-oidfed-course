import time
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

# --- Configuração do Cliente ---
# Estas credenciais DEVEM ser as mesmas configuradas no `auth_server/app.py`
CLIENT_ID = 'meu-cliente-id'
CLIENT_SECRET = 'meu-cliente-secret-super-seguro'

# URL do endpoint de token do servidor de autorização.
# Usamos 'auth-server' como hostname porque é o nome do serviço no docker-compose.
TOKEN_URL = 'http://auth-server:8000/oauth/token'

# URL do recurso protegido que queremos acessar.
RESOURCE_URL = 'http://auth-server:8000/api/dados'

# Escopo que nossa aplicação cliente precisa.
SCOPE = ['read:dados']

def run_client():
    print("--- Aplicação Cliente (PI) Iniciando ---")
    
    # Adiciona um tempo de espera para garantir que o servidor subiu
    time.sleep(5)

    try:
        # 1. Obtenção do Token de Acesso
        print("\n[Passo 1] Solicitando token de acesso...")
        
        # Cria um cliente para o fluxo "Client Credentials"
        client = BackendApplicationClient(client_id=CLIENT_ID, scope=SCOPE)
        
        # Cria uma sessão OAuth2
        oauth = OAuth2Session(client=client)
        
        # Busca o token do servidor de autorização
        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        
        print(f"Token recebido com sucesso! Access Token: {token['access_token'][:20]}...")

        # 2. Acesso ao Recurso Protegido
        print("\n[Passo 2] Acessando o recurso protegido com o token...")
        
        # A sessão `oauth` agora inclui automaticamente o token nas requisições
        response = oauth.get(RESOURCE_URL)
        response.raise_for_status() # Lança uma exceção se a requisição falhar (status != 2xx)
        
        data = response.json()
        
        print("Sucesso! Resposta do servidor de recursos (PS):")
        print(data)

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

    print("\n--- Aplicação Cliente (PI) Finalizada ---")

if __name__ == '__main__':
    run_client()