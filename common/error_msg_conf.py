def error_msg_reporting(s, f):
    if s > 2:
        client_error_msg = "Multiple system error.  Please contact Support"
    elif s == 1:
        client_error_msg = "Looks like a Data error.  Please contact Support"
    elif s == 2:
        client_error_msg = "Oops...! Data base (Technical) error occured.  Please contact Support"
    
    print("log message to debug")
    print(f)
    
    return client_error_msg