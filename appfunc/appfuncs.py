from . import bp_appfunc
from flask import redirect, request,make_response, jsonify
#from flask_cors import CORS, cross_origin
from nawalcube_server.common import dbfunc as db
from nawalcube_server.common import error_logics as errhand
from nawalcube_server.common import jwtfuncs as jwtf
from nawalcube_server.common import serviceAccountKey as sak
from nawalcube_server.authentication import auth as myauth
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import os
import hashlib
import hmac
import binascii
import string
import random

@bp_appfunc.route("/appregis",methods=["GET","POST","OPTIONS"])
def login():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="POST":
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        userid = jwtf.decodetoken(request, needtkn = False)
        entityid = request.headers.get("entityid", None)
        cntryid = request.headers.get("countryid", None)
        
        criteria_json = {
            "userid"   : userid,
            "entityid" : entityid,
            "cntryid"  : cntryid,
            "payload" : payload
        }
        res_to_send, response = app_register(criteria_json)

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

def app_register(criteria_json):
    print("inside login GET")
    s = 0
    f = None
    t = None #message to front end
    response = None
    res_to_send = 'fail'
    payload = criteria_json.get("payload",None)
    
    print(s)
    if s <= 0:
        if criteria_json.get("userid", None) != None:
            userid = criteria_json['userid']
        else:
            userid = None
            s, f, t= errhand.get_status(s, 100, f, "user id not provided", t, "yes")

        if criteria_json.get("entityid", None) != None:
            entityid = criteria_json['entityid']
        else:
            entityid = None
            s, f, t= errhand.get_status(s, 100, f, "entity id not provided", t, "yes")

        if criteria_json.get("cntryid", None) != None:
            cntryid = criteria_json['cntryid']
        else:
            cntryid = None
            s, f, t= errhand.get_status(s, 100, f, "cntry code is not provided", t, "yes")
        
        if payload == None:
            s, f, t= errhand.get_status(s, 100, f, "App data not sent.  Please try again", t, "yes")
        else:
            if payload.get("appname", None) != None:
                appname = payload['appname']
            else:
                appname = None
                s, f, t= errhand.get_status(s, 100, f, "No App name provided", t, "yes")

            if payload.get("appusertype", None) != None:
                appusertype = payload['appusertype']
            else:
                appusertype = None
                s, f, t= errhand.get_status(s, 100, f, "App user type not provided", t, "yes")

            if payload.get("redirecturi", None) != None:
                redirecturi = payload['redirecturi']
            else:
                redirecturi = None
                s, f, t= errhand.get_status(s, 100, f, "Redirect URI not provided", t, "yes")
                    
            if payload.get("postbackuri", None) != None:
                postbackuri = payload['postbackuri']
            else:
                postbackuri = None
                s, f, t= errhand.get_status(s, 0, f, "postbackuri not provided", t, "no")

            if payload.get("description", None) != None:
                description = payload['description']
            else:
                description = None
                s, f, t= errhand.get_status(s, -100, f, "description not provided", t, "no")

            if payload.get("starmfdet", None) != None:
                starmfdet = payload['starmfdet']
            else:
                starmfdet = None
                if appusertype not in ['D','A']:
                    s, f, t= errhand.get_status(s, -100, f, "star mf data not provided", t, "yes")       
                else:
                    s, f, t= errhand.get_status(s, -100, f, "star mf data not provided", t, "no")

            if payload.get("product", None) != None:
                product = payload['product']
            else:
                product = None
                s, f, t= errhand.get_status(s, -100, f, "product not provided", t, "no")
            
            if payload.get("operation", None) != None:
                operation = payload['operation']
            else:
                operation = None
                s, f, t= errhand.get_status(s, -100, f, "operation not provided", t, "no")
            # update or create are the values

            if operation == "delete" or operation == "update":
                if payload.get("appid", None) != None:
                    appid = payload['appid']
                else:
                    appid = None
                    s, f, t= errhand.get_status(s, -100, f, "appid not provided", t, "no")
                
                if payload.get("appkey", None) != None:
                    appkey = payload['appkey']
                else:
                    appkey = None
                    s, f, t= errhand.get_status(s, -100, f, "appkey not provided", t, "no")
            else:
                appid = None
                appkey = None
            
    print(appid,"oiipoi", appkey)
    cur_time = datetime.now().strftime('%Y%m%d%H%M%S')
    print(appname,appusertype,redirecturi,postbackuri,description,starmfdet)

    if s <= 0:
        con, cur, s1, f1 = db.mydbopncon()
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        print("connection statment done", s,f,t)
    

    if s <= 0:
        command = cur.mogrify("""
                                SELECT count(1)
                                FROM ncapp.appdetail a
                                WHERE delflg != 'Y'
                                AND (
                                        appname = %s
                                    )
                                AND appuserid = %s AND entityid = %s AND countryid = %s
                            """,(appname, userid, entityid, cntryid,) )
        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        print('----------------')
        print(s)
        print(f)
        print('----------------')
        if s > 0:
            s, f, t = errhand.get_status(s, 200, f, "App Name data fetch failed with DB error", t, "no")
    print(s,f)

    if s <= 0:
        db_rec = cur.fetchall()[0][0]
        print(db_rec)
    
        if db_rec > 0:
            if operation == "create":
                s, f, t= errhand.get_status(s, 100, f, "App name Already exists for this user", t, "yes")
            
        else:
            if operation == "update" or operation == "delete":
                s, f, t= errhand.get_status(s, 100, f, "App name doesn't exists for this user", t, "yes")
            print("no records satifying the current user inputs")
    print(s,f)

    appikset = False
    i = 0
    if s <= 0 and operation == "create":
        while i < 50:
            r = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(6))
            appid = create_signature("sha256", "nirunidhaappid" + r, userid + cur_time, userid)
            appkey = create_signature("md5", "nirunidhaappkey" + r, userid + cur_time, userid)

            command = cur.mogrify("""
                                    SELECT count(1)
                                    FROM ncapp.appdetail
                                    WHERE delflg != 'Y'
                                    AND (
                                            appid = %s OR appkey = %s
                                        )
                                """,(appid, appkey,) )
            print(command)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None
            print('----------------')
            print(s)
            print(f)
            print('----------------')
            if s > 0:
                s, f, t = errhand.get_status(s, 200, f, "App Name data fetch failed with DB error", t, "no")
            print(s,f)

            if s <= 0:
                db_rec = cur.fetchall()[0][0]
                print(db_rec)
            
                if db_rec > 0:
                    s, f, t= errhand.get_status(s, 100, f, "Appid or key Already exists for retrying time: " + i, t, "no")
                    i = i + 1
                    continue
                else:
                    print("no records satifying the current user inputs")
                    appikset = True
                    break
            else:
                # Some error occured, so no point looping
                appikset = False
                break
    print(s,f, t)

    if s <= 0 and operation == "create" and appikset:
        s1, f1 = db.mydbbegin(con, cur)
        print(s1,f1)

        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None

        if s <= 0:
            command = cur.mogrify("""
                        INSERT INTO ncapp.appdetail (appname, appusertype, redirecturi, postbackuri, description, starmfdet, appid, appkey, expirydate, product, delflg, appuserid, octime, lmtime, entityid, countryid) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE + INTERVAL'1 month', %s, 'N',%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s,%s);
                        """,(appname, appusertype, redirecturi, postbackuri, description, starmfdet, appid, appkey, product, userid, entityid, cntryid,))
            print(command)
            print(appname,appusertype,redirecturi,postbackuri,description,starmfdet,userid)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s > 0:
                s, f, t= errhand.get_status(s, 200, f, "SIGNUP update failed", t, "no")

            print('Insert or update is successful')
    
        if s <= 0:
            con.commit()
            #validate PAN adn store PAN number

    if s <= 0 and operation == "update":
        s1, f1 = db.mydbbegin(con, cur)
        print(s1,f1)

        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None

        if s <= 0:
            command = cur.mogrify("""
                        UPDATE ncapp.appdetail SET redirecturi = %s, postbackuri = %s, description = %s, starmfdet = %s, lmtime = CURRENT_TIMESTAMP
                        WHERE  appname = %s AND appusertype = %s AND appid =%s AND appkey = %s AND product = %s AND appuserid = %s AND entityid = %s AND countryid = %s;
                        """,(redirecturi, postbackuri, description, starmfdet, appname, appusertype, appid, appkey, product, userid, entityid, cntryid,))
            print(command)
            print(appname,appusertype,redirecturi,postbackuri,description,starmfdet,userid)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s > 0:
                s, f, t= errhand.get_status(s, 200, f, "APP details update failed", t, "no")

            print('Insert or update is successful')
    
        if s <= 0:
            con.commit()
            print("commit done")
            #validate PAN adn store PAN number


    if s <= 0 and operation == "delete":
        s1, f1 = db.mydbbegin(con, cur)
        print(s1,f1)

        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None

        if s <= 0:
            command = cur.mogrify("""
                        UPDATE ncapp.appdetail SET delflg = 'Y', lmtime = CURRENT_TIMESTAMP
                        WHERE  appname = %s AND appusertype = %s AND appid =%s AND appkey = %s AND product = %s AND appuserid = %s AND entityid = %s AND countryid = %s;
                        """,(appname, appusertype, appid, appkey, product, userid, entityid, cntryid,))
            print(command)
            print(appname,appusertype,redirecturi,postbackuri,description,starmfdet,userid)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s > 0:
                s, f, t= errhand.get_status(s, 200, f, "APP details update failed", t, "no")

            print('Insert or update is successful')
    
        if s <= 0:
            con.commit()
            #validate PAN adn store PAN number
    usrmg_fstr = None
    if s > 0:
        res_to_send = 'fail'
        result_date = []
        response = {
            'result_data' : result_date,
            'status': res_to_send,
            'status_code': s,
            'usrmsg': errhand.error_msg_reporting(s, t)
            }
    else:
        res_to_send = 'success'
        result_date = [{'appname': appname, 'appid': appid}]
        print("**********************")
        print(operation)
        print("**********************")
        if operation == "create":
            usrmg_fstr = ") creation is successful"  
        elif operation == "update":
            usrmg_fstr = ") updation is successful"
        elif operation == "delete":
            usrmg_fstr = ") deletion is successful"

        response = {
                    'result_data' : result_date,
                    'status': res_to_send,
                    'status_code': 0,
                    'usrmsg': 'App (' + appname + usrmg_fstr
        }

    print(res_to_send, response)
    
    return (res_to_send, response)


def create_signature(hastype, more_key_str, key, message):
  d = more_key_str + key
  b = d.encode()

  message = message.encode()
  if hastype == "md5":
    return hmac.new(b, message, hashlib.md5).hexdigest()
  elif hastype == "sha256":
    return hmac.new(b, message, hashlib.sha256).hexdigest()



@bp_appfunc.route("/appdetail",methods=["POST","OPTIONS"])
@bp_appfunc.route("/appnldetail",methods=["POST","OPTIONS"])
def appdetail():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="POST":        
        payload = request.get_json()
        print("---------------------3443-----")
        print(payload)
        print("---------------------3443-----")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        userid = jwtf.decodetoken(request, needtkn = False)
        entityid = request.headers.get("entityid", None)
        cntryid = request.headers.get("countryid", None)
        #appid = payload.get("appid", None)

        print("iamback")
        print(userid)
        print(entityid)
        criteria_json = {
            "userid"   : userid,
            "entityid" : entityid,
            "cntryid"  : cntryid,
            "payload" : payload
        }

        res_to_send, response = app_detail_fetch(criteria_json)

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps


def app_detail_fetch(criteria_json):
# Payload structure
# payload = {'appid': xyz, 'login': <[noauth] to get data without user id>}
# entity id and country id will come in header which are mandatory
# user id comes in jwt

    print("inside app_detail_fetch common function")
    s = 0
    f = None
    t = None #message to front end
    payload = criteria_json.get("payload",None)
    print(payload)

    if s <= 0:
        if payload == None:
            appid = None
            login = None
            # s, f, t= errhand.get_status(s, 100, f, "no payload provided", t, "yes")
        else:
            if payload.get("appid", None) != None:
                appid = payload['appid']
            else:
                appid = None

            if payload.get("login", None) != None:
                login = payload['login']
            else:
                login = None
        print(appid, login, s)
    
    if s <= 0:
        if criteria_json.get("entityid", None) != None:
            entityid = criteria_json['entityid']
        else:
            entityid = None
            s, f, t= errhand.get_status(s, 100, f, "entity id not provided", t, "yes")

        if criteria_json.get("cntryid", None) != None:
            cntryid = criteria_json['cntryid']
        else:
            cntryid = None
            s, f, t= errhand.get_status(s, 100, f, "cntry code is not provided", t, "yes")

        if login != "nologin":
            if criteria_json.get("userid", None) != None:
                userid = criteria_json['userid']
            else:
                # To get app details before login for entity and cntry
                userid = None
                s, f, t= errhand.get_status(s, 100, f, "user id not provided", t, "yes")
        else:
                userid = None
                
       
    if s <= 0:
        con, cur, s1, f1 = db.mydbopncon()
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        

    if s <= 0:
        if appid == None:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT * FROM ncapp.appdetail                                
                                    WHERE appuserid = %s AND entityid = %s AND countryid = %s
                                    AND delflg = 'N'
                                    ) as a
                                """,(userid,entityid,cntryid,))
        elif userid == None:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT * FROM ncapp.appdetail                                
                                    WHERE appid = %s AND entityid = %s AND countryid = %s
                                    AND delflg = 'N'
                                    ) as a
                                """,(appid,entityid,cntryid,))
        else:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT * FROM ncapp.appdetail                                
                                    WHERE appuserid = %s AND entityid = %s AND countryid = %s AND appid = %s
                                    AND delflg = 'N'
                                    ) as a
                                """,(userid,entityid,cntryid,appid,))

        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        print('----------------')
        print(s)
        print(f)
        print('----------------')
        if s > 0:
            s, f, t = errhand.get_status(s, 200, f, "APP data fetch failed with DB error", t, "no")
    print(s,f)

    if s <= 0:
        db_json_rec = cur.fetchall()[0][0]
        print(db_json_rec)


    if s > 0:
        res_to_send = 'fail'
        response = {
            'result_data' : "",
            'status': res_to_send,
            'status_code': s,
            'usrmsg': errhand.error_msg_reporting(s, t)
            }
    else:
        res_to_send = 'success'
        response = {
                    'result_data' : db_json_rec,
                    'status': res_to_send,
                    'status_code': 0,
                    'usrmsg': ''
        }

    print(res_to_send, response)
    
    return (res_to_send, response)


#http://localhost:8080/appsignup?type=signup&appid=12323235565656&home=http://localhost:4200

@bp_appfunc.route("/ncappsignup",methods=["GET","POST","OPTIONS"])
def appregresp():
    if request.method=="OPTIONS":
        print("inside appregresp options")
        return "inside appregresp options"

    elif request.method=="GET":
        print("inside appregresp post")
        payload = request.args
        #payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    
        criteria_json = {
            "userid"   : None,
            "entityid" : 'NAWALCUBE',
            "cntryid"  : 'IN',
            "payload" : payload
        }
        res_to_send, appname = other_app_register(criteria_json)

        if res_to_send == 'success':
            return redirect("http://localhost:4200/login/signup?type=signup&appid="+payload["appid"]+"&appname="+appname["appname"]+"&home="+payload["home"], code=302)
            # resps = make_response(jsonify(response), 200)
            # resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            print(appname["usrmsg"])
            return redirect(payload["redirecturi"]+"?type=signup&regdata=401&msg="+appname["usrmsg"], code=302)

def other_app_register(criteria_json):
    print("inside other_app_register")
    s = 0
    f = None
    t = None #message to front end
    ret_resp_data = None
    res_to_send = 'fail'
    parameters = criteria_json.get("payload",None)
    print(parameters['type'])
    payload = {
        'appid':  parameters['appid'],
        'login':  'nologin'
    }
    print(payload)
    print(criteria_json)
    criteria_json = {
            "userid"   : None,
            "entityid" : criteria_json['entityid'],
            "cntryid"  : criteria_json['cntryid'],
            "payload" : payload
        }
    resp_status, app_data = app_detail_fetch(criteria_json)
    usrmg = None
    #resp_status = "success"#testcode
    #app_data["result_data"] = {"appname": "kumar"}#testcode
    print(resp_status, app_data)
    if resp_status == "success":
        if app_data["result_data"] != None:
            app_details = app_data["result_data"][0]
            if app_details["appusertype"] == "T":
                res_to_send = "success"
                ret_resp_data = {"appname": app_details["appname"]}
                usrmsg = app_data["usrmsg"]
            else:
                res_to_send = "fail"
                usrmsg = "App is not a Trusted app"
        else:
            usrmsg = "This is not a registered app"
    if res_to_send != "success":
        res_to_send = "fail"
        ret_resp_data = {"usrmsg": usrmsg}

    print(res_to_send, ret_resp_data)
    return res_to_send, ret_resp_data


@bp_appfunc.route("/ncappsingupres",methods=["GET","POST","OPTIONS"])
def ncappsingupres():
    if request.method=="OPTIONS":
        print("inside ncappsingupres options")
        return "inside ncappsingupres options"

    elif request.method=="POST":
        print("inside ncappsingupres get")
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # firebase auth setup
        try:
            print('inside try')
            default_app = firebase_admin.get_app('natfbappsingup')
            print('about inside try')
        except ValueError:
            print('inside value error')
            #cred = credentials.Certificate(os.path.dirname(__file__)+'/serviceAccountKey.json')
            cred = credentials.Certificate(sak.SERVICEAC)
            default_app = firebase_admin.initialize_app(credential=cred,name='natfbappsingup')
        else:
            pass

        print('app ready')        
        email = payload["email"]            
        user = auth.get_user_by_email(email,app=default_app)
        print('Successfully fetched user data: {0}'.format(user.uid))
        userid = user.uid

        #dtoken = dtoken[0]
        entityid = request.headers.get("entityid", None)
        cntryid = request.headers.get("countryid", None)
        appid = payload["appid"]
        payload_to = {"appid": appid, "login": "nologin"}
        criteria_json = {
            "userid"   : None,
            "entityid" : entityid,
            "cntryid"  : cntryid,
            "payload" : payload_to
        }
        resp_status, app_data = app_detail_fetch(criteria_json)
        app_details = app_data["result_data"][0]
        usrmsg = None

        if resp_status == "success":
            if app_data["result_data"] != None:
                res_to_send = "success"
                redir_ur = app_details["redirecturi"]
                usrmsg = app_data["usrmsg"]

        if res_to_send != "success":
            res_to_send = "fail"
            redir_ur = app_data["redirecturi"]
            if app_data["usrmsg"] == '' or app_data["usrmsg"] == None:
                usrmsg = "App id not registered with nawalcube"
            else:
                usrmsg = app_data["usrmsg"]

        if res_to_send == "success":
            # Generate authtoken for the user as this is trusted app.  
            # This is to be send by trusted app whenever they communicate
            criteria_json = {
                "entityid" : entityid,
                "cntryid"  : cntryid,
                "payload" : {"appid": appid,"redirecturi": redir_ur,"userid": userid}
            }
            ath_tkn_status, ath_tkn_detail = myauth.app_userauth(criteria_json)

            if ath_tkn_status == "success":
                return redirect(redir_ur + '?type=signup&regdata={"uid":"' + userid + '","email":"' + email + '","authtkn":"' + ath_tkn_detail['result_data']['authtkn'] + '"}&msg=' + usrmsg, code=302)

        if res_to_send != "success" or ath_tkn_status != "success":
            return redirect(redir_ur + "?type=signup&regdata=401&msg="+ usrmsg, code=302)
            
def other_app_regi_resp(resp_data):
    return 'success','ok'
