# LIVE = 0
# UAT = 1
LIVE = 1

SIGNUPURL = ["","http://localhost:4200/login/signup"]
PANVALURL = ["","http://localhost:8082/panvali"]

INSTALLDATA = [{},
{
    "entityid": "NAWALCUBE",
    "countryid": "IN"
}]

# gunicorn --reload --bind=127.0.0.1:8080 nawalcube_server:app