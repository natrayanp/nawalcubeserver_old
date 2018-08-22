from flask import request, make_response, jsonify, Response, redirect
from nawalcube.common import error_logics as errhand

import psycopg2
import psycopg2.extras

def mydbfunc(con,cur,command):
    s = 0
    f = None
    t = None
    try:
        cur.execute(command)
    except psycopg2.Error as e:
        print(e)
        """
        print(type(e))
        print(e.diag)
        print(e.args)
        print(e.cursor)
        print(e.pgcode)
        print(e.pgerror)
        myerror= {'natstatus':'error','statusdetails':''}
        """
        s, f, t = errhand.get_status(s, 200, f, e.pgcode + e.pgerror, t , "no")
    except psycopg2.Warning as e:
        print(e)
        #myerror={'natstatus':'warning','statusdetails':''}
        #myerror = {'natstatus':'warning','statusdetails':e}
        s, f = errhand.get_status(s, -100, f, e.pgcode + e.pgerror, t , "no")
    finally:
        if s > 0:    
            con.rollback()
            cur.close()
            con.close()
    return cur, s, f

def mydbopncon():
    s = 0
    f = None
    t = None
    try:
        con
    except NameError:
        print("con not defined so assigning as null")
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        #conn_string = "host='mysb1.c69yvsbrarzb.us-east-1.rds.amazonaws.com' dbname='mysb1db' user='natrayan' password='Nirudhi1'"
        con=psycopg2.connect(conn_string)
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    else:            
        if con.closed:
            conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
            con=psycopg2.connect(conn_string)
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    return con,cur, s, f

def mydbcloseall(con,cur):
#close cursor and connection before exit
    con.commit()
    cur.close()
    con.close()

def mydbbegin(con,cur):
    s = 0
    f = None
    t = None
    command = cur.mogrify("BEGIN;")
    cur, s, f = mydbfunc(con,cur,command)
    
    if cur.closed == True:
        s, f = errhand.get_status(s, 200, f, "BEGIN statement execution failed", t , "no")
    else:
        print("BEGIN statment execution successful")
    
    return s, f 