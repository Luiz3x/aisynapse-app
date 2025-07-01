# =====================================================================
# 1. IMPORTAÇÕES
# =====================================================================
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

# =====================================================================
# 2. CONFIGURAÇÃO DO APP
# =====================================================================
app = Flask(__name__)
app.secret_key = 'chave-super-secreta-para-aisynapse-123'

# =====================================================================
# 3. FUNÇÕES DE AJUDA
# =====================================================================
def carregar_json(nome_arquivo, dados_padrao):
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# =====================================================================
# 4. ROTAS DA APLICAÇÃO
# =====================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usuarios = carregar_json('users.json', {})
        user_data = usuarios.get(username)
        if user_data and check_password_hash(user_data['senha'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenciais inválidas.')
    return render_template('login.html')
    
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
             return "Nome de usuário é obrigatório." # Adicionando validação
        usuarios = carregar_json('users.json', {})
        if username in usuarios:
            return "Este nome de usuário já existe!"
        
        # Simplificando para o teste, usando o username como e-mail
        email = f"{username}@exemplo.com"
        password = generate_password_hash(request.form.get('password'))

        usuarios[username] = {
            "email": email, "senha": password,
            "status_assinatura": "pendente", "data_fim_assinatura": None
        }
        salvar_json('users.json', usuarios)
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    usuarios = carregar_json('users.json', {})
    dados_usuario = usuarios.get(username)
    
    analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
    config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})

    return render_template('dashboard.html', usuario=dados_usuario, analytics=analytics, config=config)

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    novo_titulo = request.form.get('popup_titulo')
    nova_mensagem = request.form.get('popup_mensagem')
    config_atual = carregar_json('config_popup.json', {})
    config_atual['titulo'] = novo_titulo
    config_atual['mensagem'] = nova_mensagem
    salvar_json('config_popup.json', config_atual)
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/get-config')
def get_config():
    config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
    return jsonify(config)

# =====================================================================
# 5. "MOTOR DE ARRANQUE"
# =====================================================================
if __name__ == '__main__':
    app.run(port=5000, debug=True)