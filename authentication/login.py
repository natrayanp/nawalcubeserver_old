from . import bp_auth, bp_login

@bp_auth.route('/login')
@bp_login.route('/login')
def login():
    return 'login'