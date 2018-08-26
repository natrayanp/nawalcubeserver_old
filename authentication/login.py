from . import bp_auth, bp_login
from flask import redirect, request,make_response, jsonify
#from flask_cors import CORS, cross_origin
from nawalcube.common import dbfunc as db
from nawalcube.common import error_logics as errhand
from nawalcube.common import jwtdecodenoverify as jwtnv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import os
import hashlib



@bp_auth.route("/login")
@bp_login.route("/login",methods=["GET","OPTIONS"])
def login():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="GET":
        res_to_send, response = login_common(request, 'nc')

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

@bp_login.route("/dvlogin",methods=["GET","OPTIONS"])
def dvlogin():
    if request.method=="OPTIONS":
        print("inside login options")
        return "inside login options"

    elif request.method=="GET":
        res_to_send, response = login_common(request, 'dv')

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps


def login_common(request, site):
    print("inside login GET")
    s = 0
    f = None
    t = None #message to front end
    response = None
    res_to_send = 'fail'
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    userid = jwtnv.validatetoken(request, needtkn = False)
    entityid = request.headers.get("entityid", None)
    cntryid = request.headers.get("countryid", None)

    print("iamback")
    print(userid)
    print(entityid)

    if userid == None:
        s, f, t= errhand.get_status(s, 100, f, "No user details sent from client", t, "yes")
    if entityid == None:
        s, f, t= errhand.get_status(s, 100, f, "No entity details sent from client", t, "yes")
    if cntryid == None:
        s, f, t= errhand.get_status(s, 100, f, "No country details sent from client", t, "yes")
    
    ipaddress = ''

    
    if s <= 0:
        sh = session_hash( userid + datetime.now().strftime("%Y%m%d%H%M%S%f"))
        print("session_has", sh)

        con, cur, s1, f1 = db.mydbopncon()
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
    
    if s <= 0:
        command = cur.mogrify("""
                                SELECT COUNT(1) FROM ncusr.loginh WHERE
                                userid = %s AND entityid = %s AND countryid = %s
                                AND logoutime IS NULL AND sessionid != %s AND site = %s;
                            """,(userid, entityid, cntryid, sh, site,) )
        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None
        print('----------------')
        print(s)
        print(f)
        print('----------------')
        if s > 0:
            s, f, t = errhand.get_status(s, 200, f, "session data fetch failed with DB error", t, "no")
    print(s,f)

    if s <= 0:
        session_cnt = cur.fetchall()[0][0]
        print(session_cnt)

        if session_cnt > 0:
            s, f, t = errhand.get_status(s, 401, f, "User already have a active session.  Kill all and proceed?",t,"yes")
            res_to_send = 'fail'
            response = {
                'uid' : userid,
                'sessionid' : sh,
                'status': res_to_send,
                'status_code': s,
                'usrmsg': errhand.error_msg_reporting(s, t)
                }

        else:
            s1, f1 = db.mydbbegin(con, cur)
            print(s1,f1)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s <= 0:
                command = cur.mogrify("""
                            INSERT INTO ncusr.loginh (userid, ipaddress, sessionid, site, logintime, entityid, countryid) 
                            VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP,%s,%s);
                            """,(userid, ipaddress, sh, site, entityid, cntryid,))
                print(command)
                cur, s1, f1 = db.mydbfunc(con,cur,command)
                s, f, t= errhand.get_status(s, s1, f, f1, t, "no")  
                s1, f1 = 0, None

                if s > 0:
                    s, f, t= errhand.get_status(s, 200, f, "SIGNUP update failed", t, "no")
                print('Insert or update is successful')

            if s > 0:
                res_to_send = 'fail'
                response = {
                    'uid' : userid,
                    'sessionid' : '',
                    'status': res_to_send,
                    'status_code': s,
                    'usrmsg': errhand.error_msg_reporting(s, t)
                    }
            else:
                res_to_send = 'success'
                response = {
                            'uid' : userid,
                            'sessionid' : sh,
                            'status': res_to_send,
                            'status_code': 0,
                            'usrmsg': ''
                }

    con.commit()
    print(response)
    
    return (res_to_send, response)
    

def session_hash(password):
    salt = 'sesstkn'
    print(password)
    print(salt)
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest()


@bp_auth.route("/loginks")
@bp_login.route("/dvloginks",methods=["GET","OPTIONS"])
def loginks():
    if request.method=="OPTIONS":
        print("inside loginks options")
        return "inside loginks options"

    elif request.method=="GET":
        res_to_send, response = loginsk_common(request, 'nc')

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

@bp_login.route("/dvloginks",methods=["GET","OPTIONS"])
def dvloginks():
    if request.method=="OPTIONS":
        print("inside loginks options")
        return "inside loginks options"

    elif request.method=="GET":
        res_to_send, response = loginsk_common(request, 'dv')

        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

def loginsk_common(request, site):

    print("inside loginks GET")
    s = 0
    f = None
    t = None #message to front end
    response = None
    res_to_send = 'fail'
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    userid = jwtnv.validatetoken(request, needtkn = False)
    entityid = request.headers.get("entityid", None)
    cntryid = request.headers.get("countryid", None)

    print("iamback")
    print(userid)
    print(entityid)

    if userid == None:
        s, f, t= errhand.get_status(s, 100, f, "No user details sent from client", t, "yes")
    if entityid == None:
        s, f, t= errhand.get_status(s, 100, f, "No entity details sent from client", t, "yes")
    if cntryid == None:
        s, f, t= errhand.get_status(s, 100, f, "No country details sent from client", t, "yes")
    
    ipaddress = ''

    
    if s <= 0:
        sh = session_hash( userid + datetime.now().strftime("%Y%m%d%H%M%S%f"))
        print("session_has", sh)

    con, cur, s1, f1 = db.mydbopncon()
    s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
    s1, f1 = 0, None

    if s <= 0:
        s1, f1 = db.mydbbegin(con, cur)
        print(s1,f1)
        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None


    if s <= 0:
        command = cur.mogrify("""
                    UPDATE ncusr.loginh SET logoutime = CURRENT_TIMESTAMP
                    WHERE userid = %s AND entityid = %s AND countryid = %s
                    AND logoutime IS NULL AND sessionid != %s and site = %s;
                    """,(userid, entityid, cntryid, sh, site,) )
        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")  
        s1, f1 = 0, None

        if s > 0:
            s, f, t= errhand.get_status(s, 200, f, "INVALIDATING other active session failed", t, "no")
        print('Insert or update is successful')

    if s <= 0:
        command = cur.mogrify("""
                    INSERT INTO ncusr.loginh (userid, ipaddress, sessionid, site, logintime, entityid, countryid) 
                    VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP,%s,%s);
                    """,(userid, ipaddress, sh, site, entityid, cntryid,))
        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")  
        s1, f1 = 0, None

        if s > 0:
            s, f, t= errhand.get_status(s, 200, f, "SIGN IN WITH NEW session failed", t, "no")
        print('Insert or update is successful')

    if s > 0:
        res_to_send = 'fail'
        response = {
            'uid' : userid,
            'sessionid' : '',
            'status': res_to_send,
            'status_code': s,
            'usrmsg': errhand.error_msg_reporting(s, t)
            }
    else:
        res_to_send = 'success'
        response = {
                    'uid' : userid,
                    'sessionid' : sh,
                    'status': res_to_send,
                    'status_code': 0,
                    'usrmsg': ''
        }

    con.commit()
    print(response)

    return (res_to_send, response)





@bp_auth.route("/logout")
@bp_login.route("/logout",methods=["GET","OPTIONS"])
def logout():
    if request.method=="OPTIONS":
        print("inside logout options")
        return "inside logout options"

    elif request.method=="GET":
        res_to_send, response = logout_common(request, 'nc')
        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps


@bp_login.route("/dvlogout",methods=["GET","OPTIONS"])
def dvlogout():
    if request.method=="OPTIONS":
        print("inside logout options")
        return "inside logout options"

    elif request.method=="GET":
        res_to_send, response = logout_common(request, 'dv')
        if res_to_send == 'success':
            resps = make_response(jsonify(response), 200)    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            resps = make_response(jsonify(response), 400)
        
        return resps

def logout_common(request, site):

    print("inside logout GET")
    s = 0
    f = None
    t = None #message to front end
    response = None
    res_to_send = 'fail'
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    userid = jwtnv.validatetoken(request, needtkn = False)
    entityid = request.headers.get("entityid", None)
    cntryid = request.headers.get("countryid", None)
    sh = request.headers.get("mysession", None)

    print("iamback")
    print(userid)
    print(entityid)

    if userid == None:
        s, f, t= errhand.get_status(s, 100, f, "No user details sent from client", t, "yes")
    if entityid == None:
        s, f, t= errhand.get_status(s, 100, f, "No entity details sent from client", t, "yes")
    if cntryid == None:
        s, f, t= errhand.get_status(s, 100, f, "No country details sent from client", t, "yes")
    if sh == None:
        s, f, t= errhand.get_status(s, 100, f, "No session details sent from client", t, "yes")
    
    ipaddress = ''

    con, cur, s1, f1 = db.mydbopncon()
    s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
    s1, f1 = 0, None

    if s <= 0:
        s1, f1 = db.mydbbegin(con, cur)
        print(s1,f1)
        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
        s1, f1 = 0, None


    if s <= 0:
        command = cur.mogrify("""
                    UPDATE ncusr.loginh SET logoutime = CURRENT_TIMESTAMP
                    WHERE userid = %s AND entityid = %s AND countryid = %s
                    AND logoutime IS NULL AND site = %s;
                    """,(userid, entityid, cntryid, site,) )
        print(command)
        cur, s1, f1 = db.mydbfunc(con,cur,command)
        s, f, t= errhand.get_status(s, s1, f, f1, t, "no")  
        s1, f1 = 0, None

        if s > 0:
            s, f, t= errhand.get_status(s, 200, f, "LOGOUT UPDATE failed", t, "no")
        print('Insert or update is successful')


    if s > 0:
        res_to_send = 'fail'
        response = {
            'uid' : userid,
            'sessionid' : '',
            'status': res_to_send,
            'status_code': s,
            'usrmsg': errhand.error_msg_reporting(s, t)
            }
    else:
        res_to_send = 'success'
        response = {
                    'uid' : userid,
                    'sessionid' : '',
                    'status': res_to_send,
                    'status_code': 0,
                    'usrmsg': ''
        }

    con.commit()
    print(response)
    print('logout successful')
    return (res_to_send, response)




@bp_login.route("/signup",methods=["GET","POST","OPTIONS"])
def signup():
    if request.method=="OPTIONS":
            print("inside signup options")
            response = "inside signup options"
            return make_response(jsonify(response), 200)

    elif request.method=="POST":
        print("inside signup POST")
        s = 0
        f = None
        t = None #message to front end
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
        token, userid, entityid, cntryid = jwtnv.validatetoken(request, needtkn = True)
        print('iamback')
        print(token)
        print(userid)
        print(entityid)
        
        print(s)
        if s <= 0:

            if payload.get("custtype", None) != None:
                usercusttype = payload['custtype']['value']
            else:
                usercusttype = None
                s, f, t= errhand.get_status(s, 100, f, "No user customer type from client", t, "yes")

            if payload.get("name", None) != None:
                sinupusername = payload['name']
            else:
                sinupusername = None
                s, f, t= errhand.get_status(s, 100, f, "No user name from client", t, "yes")

            if payload.get("adhaar", None) != None:
                sinupadhaar = payload['adhaar']
            else:
                sinupadhaar = None
                s, f, t= errhand.get_status(s, 100, f, "No adhaar from client", t, "yes")

            if payload.get("pan", None) != None:
                sinuppan = payload['pan']
            else:
                sinuppan = None
                s, f, t= errhand.get_status(s, 100, f, "No pan from client", t, "yes")

            if payload.get("mobile", None) != None:
                sinupmobile = payload['mobile']
            else:
                sinupmobile = None
                s, f, t= errhand.get_status(s, 100, f, "No mobile data from client", t, "yes")       

            usertype='W'
            userstatus = 'S'
            cur_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # firebase auth setup
        print(os.path.dirname(__file__)+'/serviceAccountKey.json')
        try:
            print('inside try')
            default_app=firebase_admin.get_app('natfbloginsingupapp')
            print('about inside try')
        except ValueError:
            print('inside value error')
            cred = credentials.Certificate(os.path.dirname(__file__)+'/serviceAccountKey.json')
            default_app = firebase_admin.initialize_app(credential=cred,name='natfbloginsingupapp')
        else:
            pass

        print('app ready')
        
        try:
            print('start decode')
            decoded_token = auth.verify_id_token(token,app=default_app)
            print('decoded')
        except ValueError:
            print('valuererror')
            s, f, t = errhand.get_status(s, 100, f, "Not a valid user properties", t, "yes")            
        except AuthError:
            print('AuthError')
            s, f, t = errhand.get_status(s, 100, f, "Not a valid user credentials", t, "yes")     
        else:
            print('inside', decoded_token)
            uid = decoded_token.get("user_id", None)
            exp = decoded_token.get("exp", None)
            iat = decoded_token.get("iat", None)
            email = decoded_token.get("email", None)
            # set entity id to the token
            entityid = request.headers.get("entityid", None)
            cntryid = request.headers.get("countryid", None)
            
            if entityid != None:
                try:
                    print('start set custom')
                    auth.set_custom_user_claims(uid, {"entityid": entityid, "countryid": cntryid, "custtype": usercusttype},app=default_app)
                    print('end set custom')
                except ValueError:
                    print('valuererror')
                    s, f, t = errhand.get_status(s, 100, f, "Not a valid user properties", t, "yes")
                except AuthError:
                    print('AuthError')
                    s, f, t = errhand.get_status(s, 100, f, "Not a valid user credentials", t, "yes")
            else:
                print('else after autherror')
                s, f, t = errhand.get_status(s, 100, f, "No entity id from client", t, "yes")

            print('apppa mudichachu')
            print(uid)
            print(decoded_token)
        

        if s <= 0:
            if email != None:
                sinupemail = email
            else:
                sinupemail = None
                s, f, t = errhand.get_status(s, 100, f, "No email data from client", t, "yes")

            if uid != None:
                userid = uid
            else:
                userid = None
                s, f, t = errhand.get_status(s, 100, f, "No user id from client" , t, "yes")
        
        
        if s <= 0:
            con, cur, s1, f1 = db.mydbopncon()
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None
        

        if s <= 0:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT l.userid, l.username, l.usertype, l.usercusttype, l.entityid, 
                                    d.sinupusername, d.sinupadhaar, d.sinuppan, d.sinupmobile, d.sinupemail
                                    FROM ncusr.userlogin l
                                    LEFT JOIN ncusr.userdetails d ON l.userid = d.userid AND l.entityid = d.entityid
                                    WHERE l.userstatus != 'I'
                                    AND (
                                            l.userid = %s OR d.sinupadhaar = %s OR d.sinuppan = %s OR d.sinupmobile = %s OR d.sinupemail = %s
                                        )
                                    AND l.entityid = %s AND l.countryid = %s
                                    ) as a
                                """,(uid,sinupadhaar,sinuppan,sinupmobile,sinupemail,entityid,cntryid,) )
            print(command)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None
            print('----------------')
            print(s)
            print(f)
            print('----------------')
            if s > 0:
                s, f, t = errhand.get_status(s, 200, f, "User data fetch failed with DB error", t, "no")
        print(s,f)

        if s <= 0:
            db_json_rec = cur.fetchall()[0][0]
            print(db_json_rec)

            if db_json_rec:
                for rec in db_json_rec:
                    if rec['userid'] == userid:
                        s, f, t= errhand.get_status(s, 100, f, "Userid Already exists", t, "yes") 

                    if rec['sinupadhaar'] == sinupadhaar:
                        s, f, t= errhand.get_status(s, 100, f, "Adhaar Already registered", t, "yes")
                    
                    if rec['sinuppan'] == sinuppan:
                        s, f, t= errhand.get_status(s, 100, f, "PAN Already registered", t, "yes")
                    
                    if rec['sinupmobile'] == sinupmobile:
                        s, f, t= errhand.get_status(s, 100, f, "Mobile Already registered", t, "yes")

                    if rec['sinupemail'] == sinupemail:
                        s, f, t= errhand.get_status(s, 100, f, "Email Already registered", t, "yes")
            else:
                print("no records satifying the current user inputs")
        print(s,f)
        if s <= 0:
            s1, f1 = db.mydbbegin(con, cur)
            print(s1,f1)

            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

        if s <= 0:
            command = cur.mogrify("""
                        INSERT INTO ncusr.userlogin (userid, usertype, usercusttype, userstatus, userstatlstupdt, octime, lmtime, entityid, countryid) 
                        VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s,%s);
                        """,(userid, usertype, usercusttype, userstatus, entityid, cntryid,))
            print(command)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s > 0:
                s, f, t= errhand.get_status(s, 200, f, "SIGNUP update failed", t, "no")
            print('Insert or update is successful')

        if s <= 0:
            command = cur.mogrify("""
                        INSERT INTO ncusr.userdetails (userid, sinupusername, sinupadhaar, sinuppan, sinupmobile, sinupemail, octime, lmtime, entityid, countryid) 
                        VALUES (%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s,%s);
                        """,(userid, sinupusername, sinupadhaar, sinuppan, sinupmobile, sinupemail, entityid, cntryid,))
            print(command)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

            if s > 0:
                s, f, t= errhand.get_status(s, 200, f, "SIGNUP update failed", t, "no")

            print('Insert or update is successful')
    
        if s <= 0:
            con.commit()
            #validate PAN adn store PAN number

            response = {
                'status': 'success',
                'error_msg' : ''
            }
            resps = make_response(jsonify(response), 200)
        else:
            response = {
                'status': 'fail',
                'error_msg' : errhand.error_msg_reporting(s, t)
            }
            resps = make_response(jsonify(response), 400)
        
        return resps