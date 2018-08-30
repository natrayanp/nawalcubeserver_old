from . import bp_apifunc
from flask import redirect, request,make_response, jsonify
#from flask_cors import CORS, cross_origin
from nawalcube.common import dbfunc as db
from nawalcube.common import error_logics as errhand
from nawalcube.common import jwtdecodenoverify as jwtnv
from datetime import datetime
import os
import hashlib


@bp_apifunc.route("/appregis",methods=["GET","POST","OPTIONS"])
def login():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="POST":
        res_to_send, response = log_common(request, 'nc')
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

def log_common(request, site):
    print("inside login GET")
    s = 0
    f = None
    t = None #message to front end
    response = None
    res_to_send = 'fail'
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

  
    res_to_send = 'success'
    response = {
                'status_code': 0,
                'usrmsg': ''
    }

    print(response)
    
    return (res_to_send, response)