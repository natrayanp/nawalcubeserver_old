from datetime import datetime

import jwt
import requests
import json
      
def validatetoken(request):
    print('inside validatetoken',request.headers)
    if 'Authorization' in request.headers:
        print('inside aut')
        token_full = request.headers.get('Authorization')
        if token_full.startswith("Bearer "):
            token =  token_full[7:]
        natjwtdecoded = jwt.decode(token, verify=False)        
        userid = natjwtdecoded['uid']
        entityid = natjwtdecoded['entityid']
        print('getting value')
        print(userid,entityid)
        #entityid=natjwtdecoded['entityid']
        if  (not userid) or (userid ==""):
            status = 'failed'
        return userid,entityid