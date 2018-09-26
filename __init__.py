from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app,supports_credentials=True,headers='Content-Type,countryid')

from nawalcube_server import authentication


#app.config.from_object('settings')

from nawalcube_server.flows import bp_flow
from nawalcube_server.flows import flow
from nawalcube_server.authentication import bp_auth, bp_login
from nawalcube_server.authentication import auth
from nawalcube_server.authentication import login
from nawalcube_server.appfunc import appfuncs, appauth, bp_appfunc

app.register_blueprint(bp_flow)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_login)
app.register_blueprint(bp_appfunc)


