from flask import (
    Blueprint, current_app, redirect, render_template,
    request, session, url_for,
)

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').lower().strip()
        senha   = request.form.get('senha', '')
        users   = current_app.config.get('USERS', {})
        if usuario in users and users[usuario]['senha'] == senha:
            session['usuario'] = usuario
            session['nome']    = users[usuario]['nome']
            session['perfil']  = users[usuario]['perfil']
            return redirect(request.args.get('next') or url_for('dashboard.dashboard'))
        erro = 'Usuário ou senha incorretos.'
    return render_template('login.html', erro=erro)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
