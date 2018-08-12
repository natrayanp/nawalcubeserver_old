from flask import Flask

app = Flask(__name__)
#CORS(app)

from nawalcube import authentication

#app.config.from_object('settings')

from nawalcube.flows import bp_flow
from nawalcube.flows import flow
from nawalcube.authentication import bp_auth, bp_login
from nawalcube.authentication import auth
from nawalcube.authentication import login


app.register_blueprint(bp_flow)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_login)