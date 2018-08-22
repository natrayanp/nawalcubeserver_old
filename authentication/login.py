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


@bp_auth.route("/login")
@bp_login.route("/login")
def login():
    return "login"


@bp_login.route("/signup",methods=["GET","POST","OPTIONS"])
def signup():
    if request.method=="OPTIONS":
            print("inside signup options")
            return "inside signup options"

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
        if s < 100:

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
        

        if s < 100:
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
        
        
        if s < 100:
            con, cur, s1, f1 = db.mydbopncon()
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None
        

        if s < 100:
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

        if s < 100:
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
        if s < 100:
            s1, f1 = db.mydbbegin(con, cur)
            print(s1,f1)

            s, f, t= errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

        if s < 100:
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

        if s < 100:
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
    
        if s < 100:
            con.commit()
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