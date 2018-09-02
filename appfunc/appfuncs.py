from . import bp_appfunc
from flask import redirect, request,make_response, jsonify
#from flask_cors import CORS, cross_origin
from nawalcube.common import dbfunc as db
from nawalcube.common import error_logics as errhand
from nawalcube.common import jwtdecodenoverify as jwtnv
from datetime import datetime
import os
import hashlib
import hmac
import binascii


@bp_appfunc.route("/appregis",methods=["GET","POST","OPTIONS"])
def login():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="POST":
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        userid = jwtnv.validatetoken(request, needtkn = False)
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
                                FROM ncusr.appdetail a
                                WHERE delflg != 'Y'
                                AND (
                                        appname = %s
                                    )
                                AND userid = %s AND entityid = %s AND countryid = %s
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
            appid = create_signature("sha256", "nirunidhaappid" + str(i), userid + cur_time, userid)
            appkey = create_signature("md5", "nirunidhaappkey" + str(i), userid + cur_time, userid)

            command = cur.mogrify("""
                                    SELECT count(1)
                                    FROM ncusr.appdetail
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
                        INSERT INTO ncusr.appdetail (appname, appusertype, redirecturi, postbackuri, description, starmfdet, appid, appkey, expirydate, product, delflg, userid, octime, lmtime, entityid, countryid) 
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
                        UPDATE ncusr.appdetail SET redirecturi = %s, postbackuri = %s, description = %s, starmfdet = %s, lmtime = CURRENT_TIMESTAMP
                        WHERE  appname = %s AND appusertype = %s AND appid =%s AND appkey = %s AND product = %s AND userid = %s AND entityid = %s AND countryid = %s;
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
                        UPDATE ncusr.appdetail SET delflg = 'Y', lmtime = CURRENT_TIMESTAMP
                        WHERE  appname = %s AND appusertype = %s AND appid =%s AND appkey = %s AND product = %s AND userid = %s AND entityid = %s AND countryid = %s;
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
        userid = jwtnv.validatetoken(request, needtkn = False)
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
    print("inside app_detail_fetch common function")
    s = 0
    f = None
    t = None #message to front end
    payload = criteria_json.get("payload",None)
    print(payload)
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
            appid = None
        else:
            if payload.get("appid", None) != None:
                appid = payload['appid']
            else:
                appid = None
                #s, f, t= errhand.get_status(s, 100, f, "cntry code is not provided", t, "yes")
        
    if s <= 0:
        con, cur, s1, f1 = db.mydbopncon()
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        

    if s <= 0:
        if appid != None:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT * FROM ncusr.appdetail                                
                                    WHERE userid = %s AND entityid = %s AND countryid = %s AND appid = %s
                                    AND delflg = 'N'
                                    ) as a
                                """,(userid,entityid,cntryid,appid,))
        else:            
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT * FROM ncusr.appdetail                                
                                    WHERE userid = %s AND entityid = %s AND countryid = %s
                                    AND delflg = 'N'
                                    ) as a
                                """,(userid,entityid,cntryid,))
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
