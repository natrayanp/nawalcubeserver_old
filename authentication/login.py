from . import bp_auth, bp_login
#from flask import redirect, request,make_response
#from flask_cors import CORS, cross_origin
from nawalcube.common import setstatus stat
from nawalcube.common import dbfunc db
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth


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
        payload = request.get_json()
        print(payload)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        #firebase auth setup
        cred = credentials.Certificate("/home/natrayan/project/AwsProject/Python/nawalcubebackend/nawalcube/authentication/serviceAccountKey.json")
        default_app = firebase_admin.initialize_app(cred)
        
        #custom_token = auth.create_custom_token(uid, additional_claims)        

        try:
            decoded_token = auth.verify_id_token(id_token)
        except ValueError:
            s, f = stat.get_status(s, 1, f, "Not a valid user properties" )
        except AuthError:
            s, f = stat.get_status(s, 1, f, "Not a valid user credentials")
        else:
            uid = decoded_token.get("uid", None)
            exp = decoded_token.get("exp", None)
            iat = decoded_token.get("iat", None)
            email = decoded_token.get("email", None)
            # set entity id to the token
            entityid = request.headers.get("entityid", None)
            if entityid != None:
                try:
                    auth.set_custom_user_claims(uid, {"entityid": entityid})
                except ValueError:
                    s, f = stat.get_status(s, 1, f, "Not a valid user properties")
                except AuthError:
                    s, f = stat.get_status(s, 1, f, "Not a valid user credentials")
            else:
                s, f = stat.get_status(s, 1, f, "No entity id from client" )
        
        if s < 1:
            userid = uid if uid != None else (s, f = stat.get_status(s, 1, f, "No user id from client" ))
            sinupusername = payload['name'] if payload("name", None) != None else (s, f = stat.get_status(s, 1, f, "No user name from client" ))
            sinupadhaar= payload['adhaar'] if payload("adhaar", None) != None else (s, f = stat.get_status(s, 1, f, "No adhaar from client" ))
            sinuppan = payload['pan'] if payload("pan", None) != None else (s, f = stat.get_status(s, 1, f, "No pan from client" ))
            sinupmobile = payload['mobile'] if payload("mobile", None) != None else (s, f = stat.get_status(s, 1, f, "No mobile data from client" ))
            sinupemail = email if email != None else (s, f = stat.get_status(s, 1, f, "No email data from client" ))
            usertype='W'
            userstatus = 'S'
            cur_time = datetime.now().strftime('%Y%m%d%H%M%S')

        if s < 1:
            con, cur, s1, f1 = db.mydbopncon()
            s, f = stat.get_status(s, s1, f, f1)
            s1, f1 = None * 2
        
        if s < 1:
            command = cur.mogrify("""
                                    SELECT json_agg(a) FROM (
                                    SELECT l.userid,l.username,l.usertype,l.entityid, 
                                    d.sinupusername, d.sinupadhaar, d.sinuppan, d.sinupmobile, d.sinupemail
                                    FROM ncusr.userlogin l
                                    LEFT JOIN ncusr.userdetails d ON l.userid = d.userid AND l.entityid = d.entityid
                                    WHERE l.userstatus != "I"
                                    AND (
                                            l.userid = %s OR d.sinupadhaar = %s OR d.sinuppan = %s d.sinupmobile OR d.sinupemail = %s
                                        )
                                    ) as a
                                """,(uid,entityid) )

            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f = stat.get_status(s, s1, f, f1)
            s1, f1 = None * 2

            if s > 0:
                s, f = stat.get_status(s, 2, f, "User data fetch failed with DB error")

        if s < 1:
            db_json_rec = cur.fetchall()[0][0]
            print(db_json_rec)
        
            for rec in db_json_rec:
                s, f = stat.get_status(s, 1, f, "Userid Already exists") if rec['userid'] == userid
                s, f = stat.get_status(s, 1, f, "Adhaar Already registered") if rec['sinupadhaar'] == sinupadhaar
                s, f = stat.get_status(s, 1, f, "PAN Already registered") if rec['sinuppan'] == sinuppan
                s, f = stat.get_status(s, 1, f, "Mobile Already registered") if rec['sinupmobile'] == sinupmobile
                s, f = stat.get_status(s, 1, f, "Email Already registered") if rec['sinupemail'] == sinupemail
        
        if s < 1:
            s1, f1 = db.mydbbegin(con, cur)
            s, f = stat.get_status(s, s1, f, f1)
            s1, f1 = None * 2

        if s < 1:
            command = cur.mogrify("""
                        INSERT INTO ncusr.userlogin (userid, usertype, userstatus, userstatusupdt, octime, lmtime, entityid) 
                        VALUES (%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s);
                        """,(userid, usertype, userstatus, entityid,))

            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f = stat.get_status(s, s1, f, f1)
            s1, f1 = None * 2

            if s > 0:
                s, f = stat.get_status(s, 2, f, "SIGNUP update failed")
            print('Insert or update is successful')

        if s < 1:
            command = cur.mogrify("""
                        INSERT INTO ncusr.userdetails (userid, sinupusername, sinupadhaar, sinuppan, sinupmobile, sinupemail, octime, lmtime, entityid) 
                        VALUES (%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s);
                        """,(userid, sinupusername, sinupadhaar, sinuppan, sinupmobile, sinupemail, entityid,))

            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f = stat.get_status(s, s1, f, f1)
            s1, f1 = None * 2

            if s > 0:
                s, f = stat.get_status(s, 2, f, "SIGNUP update failed")

            print('Insert or update is successful')
    
        if s < 1:
            con.commit()
        
        msg_to_client = error_msg_reporting(s, f)

        response = {
            'status': 
            'error_msg' : msg_to_client
        }


            

        
