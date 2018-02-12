from flask import Flask, jsonify, request, abort, Response
import json
import psycopg2

app = Flask(__name__)

from datetime import timedelta  
from flask import Flask, make_response, request, current_app  
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator





def getopenconnection(user='postgres', password='password', dbname='gsk'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

conn = getopenconnection()
cur = conn.cursor()

def userq(query, args=(), one=False):
	cur.execute(query,args)
	conn.commit()
	rv = [dict((cur.description[idx][0], value)
	for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv


# Endpoints
@app.route('/registerhcp', methods=['POST'])
@crossdomain(origin='*')
def register():
	req_json = request.get_json()
	email = str(req_json['email'])
	passwd = str(req_json['password'])
	grp = str(req_json['group'])
	companyCode = str(req_json['companyCode'])
	print email,passwd,grp,companyCode
	command = """SELECT count(email) FROM hcp WHERE email = \'""" + email + """\';"""
	print command
	cur.execute(command)
	conn.commit()
    	flag = cur.fetchone()
    	print flag[0]
	#res = "User already exists"
    	if flag[0] == 0:
    		command = """INSERT INTO hcp(email,password,groupp,companyCode) VALUES (\'""" + email + """\',\'""" + passwd + """\',\'""" + grp + """\',\'""" + companyCode + """\');"""
    		print command
		#cur = openconnection.cursor()
    		cur.execute(command)
    		conn.commit()
    		res = "User created"
    		result = {}
    		result['registerhcp'] = res
    		resp = Response(json.dumps(result),status=200,mimetype='application/json')
	else:
		res = "User already exists"
		result = {}
		result['registerhcp'] = res
		resp = Response(json.dumps(result),status=400,mimetype='application/json')
    	return resp	

@app.route('/loginhcp', methods=['POST'])
@crossdomain(origin='*')
def login():
	req_json = request.get_json()
	email = str(req_json['email'])
	command = """SELECT count(password) FROM hcp WHERE email = \'""" + email + """\';"""
	#cur = openconnection.cursor()
    	cur.execute(command)
    	conn.commit()
    	passwd = cur.fetchone()[0]
    	if (passwd > 0 ):
    		res = "Successfully logged in"
		command = """SELECT password FROM hcp WHERE email = \'""" + email + """\';"""
		cur.execute(command)
		conn.commit()
		passwd = cur.fetchone()[0]
		result = {}
        	result['password'] = passwd
        	result['loginhcp'] = res
        	resp = Response(json.dumps(result),status=200,mimetype='application/json')
    	else:
    		res = "Error in User Login"
		passwd = "User does not exist"	
    		result = {}
		result['password'] = passwd
		result['loginhcp'] = res
		resp = Response(json.dumps(result),status=400,mimetype='application/json')
	return resp	

@app.route('/')
@crossdomain(origin='*')
def test():
	return "It works"

@app.route('/showhcp',methods=['GET'])
@crossdomain(origin='*')
def show():
	result = userq("SELECT * FROM hcp;")
	data = json.dumps(result)
	resp = Response(data,status=200,mimetype='application/json')
	return resp

# MAIN FUNCTION CALL
if __name__ == '__main__':
  with getopenconnection() as con:
  	con.autocommit = True
  	app.run()
