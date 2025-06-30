import time
from flask import Flask, jsonify
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.oauth2.rfc6749.grants import ClientCredentialsGrant
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from authlib.jose.jwk import dumps as jwk_dumps
# Importamos o gerador de token JWT
from authlib.oauth2.rfc6750.token import BearerTokenGenerator

app = Flask(__name__)
# app.config['AUTHLIB_INSECURE_TRANSPORT'] = True

# --- Chave e Dicionário JWK ---
JWT_SECRET_KEY = "minha-chave-secreta-para-jwt"
private_key_dict = jwk_dumps(JWT_SECRET_KEY, kty='oct')

# --- Configuração do Servidor de Autorização ---
# Agora, o gerador de token é configurado na inicialização do servidor.
authorization = AuthorizationServer(
    app,
    # Passamos uma instância do gerador de token JWT
    generate_token=BearerTokenGenerator(
        key=private_key_dict,
        alg='HS256',
        # issuer='https://auth.example.com',
    )
)

def query_client(client_id):
    # Esta função agora é chamada pelo gerador de token,
    # então a definimos antes de registrar o grant.
    return CLIENT_DB.get(client_id)

def save_token(token, request):
    pass

# Agora que o servidor está totalmente configurado, podemos
# registrar o query_client e save_token nele.
authorization.query_client = query_client
authorization.save_token = save_token

# Registramos o grant sem nenhuma extensão. O formato do token
# já foi definido globalmente no servidor.
authorization.register_grant(ClientCredentialsGrant)


# --- Dicionário de Clientes (definido após as funções que o usam) ---
CLIENT_DB = {
    "meu-cliente-id": {
        "client_secret": "meu-cliente-secret-super-seguro",
        "client_name": "Aplicação Cliente PI",
        "scope": "read:dados",
    }
}


# --- Configuração do Servidor de Recursos ---
require_oauth = ResourceProtector()
jwt_validator = JWTBearerTokenValidator(
    public_key=private_key_dict,
    claims_options={
        'iss': {'essential': True, 'value': 'https://auth.example.com'},
        'aud': {'essential': True, 'value': 'https://api.example.com'},
    }
)
require_oauth.register_token_validator(jwt_validator)


# --- Definição dos Endpoints ---
@app.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()

@app.route('/api/dados', methods=['GET'])
@require_oauth('read:dados')
def dados_protegidos():
    client_id = require_oauth.token.get('client_id')

    return jsonify({
        "message": "AGORA SIM! Você conseguiu acessar os dados protegidos!",
        "timestamp": time.time(),
        "dados": [{"id": 1, "info": "Dado secreto 1"}, {"id": 2, "info": "Dado secreto 2"}],
        "acessado_pelo_cliente": client_id
    })

@app.route('/')
def index():
    return "Servidor de Autorização e Recursos (PS) está no ar."