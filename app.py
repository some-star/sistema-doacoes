from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret-key'  # necessário para mensagens flash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------------
# MODELOS
# -------------------------------
class Doador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(100))
    cpf = db.Column(db.String(11))
    endereco = db.Column(db.String(200))
    tipo_pessoa = db.Column(db.String(2), nullable=False)  # PF ou PJ
    cnpj = db.Column(db.String(14))

class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=False)
    data = db.Column(db.String(8), nullable=False)  # agora 8 dígitos
    valor = db.Column(db.Float)
    observacao = db.Column(db.String(200))

    forma_pagamento = db.Column(db.String(20))  # novo
    tipo_doacao = db.Column(db.String(20))      # novo

    doador = db.relationship('Doador', backref=db.backref('doacoes', lazy=True))

# Criar banco
with app.app_context():
    db.create_all()

# -------------------------------
# ROTAS
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar_doador', methods=['GET', 'POST'])
def cadastrar_doador():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form.get('email') or None
        cpf = request.form.get('cpf') or None
        endereco = request.form.get('endereco') or None
        tipo_pessoa = request.form['tipo_pessoa']
        cnpj = request.form.get('cnpj') or None

        novo_doador = Doador(
            nome=nome,
            telefone=telefone,
            email=email,
            cpf=cpf,
            endereco=endereco,
            tipo_pessoa=tipo_pessoa,
            cnpj=cnpj
        )

        db.session.add(novo_doador)
        db.session.commit()

        flash("Doador cadastrado com sucesso!")
        return redirect(url_for('listar_doadores'))

    return render_template('cadastrar_doador.html')

@app.route('/listar_doadores')
def listar_doadores():
    doadores = Doador.query.all()
    return render_template('listar_doadores.html', doadores=doadores)

@app.route('/excluir_doador/<int:id>', methods=['POST'])
def excluir_doador(id):
    doador = Doador.query.get_or_404(id)
    db.session.delete(doador)
    db.session.commit()
    flash("Doador excluído com sucesso!")
    return redirect(url_for('listar_doadores'))

@app.route('/registrar_doacao', methods=['GET', 'POST'])
def registrar_doacao():
    doadores = Doador.query.all()
    if request.method == 'POST':
        doador_id = request.form['doador']
        data = request.form['data']
        valor = request.form.get('valor')
        observacao = request.form.get('observacao')
        forma_pagamento = request.form.get('forma_pagamento') or None
        tipo_doacao = request.form.get('tipo_doacao') or None

        if not valor and not observacao:
            flash("É necessário preencher pelo menos o valor ou a observação!")
            return redirect(url_for('registrar_doacao'))

        valor = float(valor) if valor else None
        nova_doacao = Doacao(
            doador_id=doador_id,
            data=data,
            valor=valor,
            observacao=observacao,
            forma_pagamento=forma_pagamento,
            tipo_doacao=tipo_doacao
        )
        db.session.add(nova_doacao)
        db.session.commit()
        flash("Doação registrada com sucesso!")
        return redirect(url_for('listar_doacoes'))
    return render_template('registrar_doacao.html', doadores=doadores)

@app.route('/listar_doacoes')
def listar_doacoes():
    doacoes = Doacao.query.all()
    return render_template('listar_doacoes.html', doacoes=doacoes)

@app.route('/excluir_doacao/<int:id>', methods=['POST'])
def excluir_doacao(id):
    doacao = Doacao.query.get_or_404(id)
    db.session.delete(doacao)
    db.session.commit()
    flash("Doação excluída com sucesso!")
    return redirect(url_for('listar_doacoes'))

if __name__ == '__main__':
    app.run(debug=True)