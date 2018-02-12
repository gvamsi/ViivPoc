from flask import Flask, jsonify, request, abort, Response
import json
import psycopg2

app = Flask(__name__)


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

#def getopenconnection(user='postgres', password='password', dbname='gsk'):
#    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")


# Endpoints
@app.route('/registerhcp', methods=['POST'])
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
	res = "User already exists"
    	if flag[0] == 0:
    		command = """INSERT INTO hcp(email,password,groupp,companyCode) VALUES (\'""" + email + """\',\'""" + passwd + """\',\'""" + grp + """\',\'""" + companyCode + """\');"""
    		print command
		#cur = openconnection.cursor()
    		cur.execute(command)
    		conn.commit()
    		res = "User created"
    	result = {}
    	result['registerhcp'] = res
    	resp = Response(json.dumps(result),status=202,mimetype='application/json')
    	return resp	

@app.route('/loginhcp', methods=['POST'])
def login():
	req_json = request.get_json()
	email = str(req_json['email'])
	#password = str(req_json['password'])
	#group = str(req_json['group'])
	#companyCode = str(req_json['companyCode'])
	command = """SELECT password FROM hcp WHERE email = \'""" + email + """\';"""
	#cur = openconnection.cursor()
    	cur.execute(command)
    	conn.commit()
    	res = cur.fetchone()[0]
    	if (len(res) != 0 ):
    		res = "Successfully logged in"
    	else:
    		res = "Error in User Login"	
    	result = {}
	result['loginhcp'] = res
	resp = Response(json.dumps(result),status=202,mimetype='application/json')
	return resp	

@app.route('/')
def test():
	return "It works"

@app.route('/showhcp',methods=['GET'])
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
