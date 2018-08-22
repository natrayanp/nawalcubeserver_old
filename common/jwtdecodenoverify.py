from datetime import datetime

import jwt
import requests
import json
      
def validatetoken(request, needtkn = False):
    print('inside validatetoken',request.headers)
    if 'Authorization' in request.headers:
        print('inside aut')
        token_full = request.headers.get('Authorization')
        if token_full.startswith("Bearer "):
            token =  token_full[7:]
            
        print(token)
        natjwtdecoded = jwt.decode(token, verify=False)      
        print(natjwtdecoded)  
        userid = natjwtdecoded['user_id']
        entityid = natjwtdecoded.get('entityid','')
        cntryid =  natjwtdecoded.get('countryid','')
        print('getting value')
        print(userid, entityid, cntryid)
        #entityid=natjwtdecoded['entityid']
        if  (not userid) or (userid ==""):
            status = 'failed'

        if needtkn:
            if token:
                return token, userid, entityid, cntryid
            else:
                return None * 3
        else:
            return userid, entityid, cntryid