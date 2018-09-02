from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app,supports_credentials=True)

from nawalcube import authentication


#app.config.from_object('settings')

from nawalcube.flows import bp_flow
from nawalcube.flows import flow
from nawalcube.authentication import bp_auth, bp_login
from nawalcube.authentication import auth
from nawalcube.authentication import login
from nawalcube.appfunc import appfuncs, bp_appfunc


app.register_blueprint(bp_flow)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_login)
app.register_blueprint(bp_appfunc)