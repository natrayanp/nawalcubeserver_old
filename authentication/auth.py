from . import bp_auth, bp_login

@bp_auth.route('/auth')
def auth():
    return 'auth'

def nat():
    print("inside auth nat function")