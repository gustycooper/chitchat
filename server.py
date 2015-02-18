import psycopg2
import psycopg2.extras

import os
import uuid
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
users = {}

def connectToDBchat():
  connectionString = 'dbname=chat user=gusty password= host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")


'''
The general pattern is to have two functions connected via the socket.
Called server functions:
On the Python side, functions decorated with @socketio.on() are called from the
browser.  For example, the server function new_message() is called from the 
browser's function $scope.send = function send()

Called browser functions:
Python can call browser function by using the emit() function.  For example, the 
updateRoser() performs emit('roster',names,broadcast=True) in order to call the 
browswer function socket.on('roster', function(names))
'''


'''
updateRoster() keeps track of users that are logged on the chat room.
The emit('roster', namees, broadcast=True) passes the list names (of users)
to the socket.on('roster', function(names)) code in the browser.
The broadcast=True causes all browswers to update their list of users.
'''
def updateRoster():
    names = []
    for user_id in  users:
        print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    emit('roster', names, broadcast=True)
    
'''
test_connect() is called from the broswer via the 
var socket = io.connect('http://' + document.domain, location.port)
I think this performs a handshake to also call the browswer function.
socket.on('connect', function())
'''
@socketio.on('connect', namespace='/chat')
def test_connect():
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()


    for message in messages:
        emit('message', message)

@socketio.on('search', namespace='/chat')
def search(searchString):
    searchString = '%'+searchString+'%'
    print 'search',"searchString", searchString
    db = connectToDBchat()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.mogrify("""SELECT * FROM messages WHERE message LIKE %s OR userid LIKE %s""", (searchString,searchString ))
    print 'search',"query",query
    cur.execute(query)
    rows = cur.fetchall()
    print 'search', "fetchall results", rows
    for i in rows:
        tmp = {'text':i[2], 'name':i[1]}
        print 'search', 'search match', tmp
        emit('message', tmp, broadcast=False)
 
@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    username = users[session['uuid']]['username']
    print 'new_message',"message", message
    print 'new_message',"userename", username
    print 'new_message',"tmp", tmp
    emit('message', tmp, broadcast=True)
    db = connectToDBchat()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.mogrify("""INSERT INTO messages (userid,message) VALUES (%s,%s)""", (username, message))
    print 'new_message',"query",query
    cur.execute(query)
    print 'new_message', "query status", cur.statusmessage
    db.commit()
 
    
    
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'identify' + message
    users[session['uuid']]={'username':message}
    print "users", users
    updateRoster()


@socketio.on('login', namespace='/chat')
def on_login(pw):
    print 'on_login '  + pw
    #users[session['uuid']]={'username':message}
    #updateRoster()
    db = connectToDBchat()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    username = users[session['uuid']]
    username = username['username']
    print "on_login", username
    query = cur.mogrify("""SELECT * FROM users WHERE username = %s AND password = crypt(%s,password)""", (username, pw))
    print "on_login", username, pw, query
    cur.execute(query)
    fetchOne = cur.fetchone()
    print "on_login", fetchOne
    if fetchOne:
       restrictions = fetchOne[3] # for future use
       print "on_login", "login successful", fetchOne, restrictions
       #updateRoster()
    else:
       print "on_login", "login unsuccessful"
       emit('failedLogin')
    
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()

@app.route('/')
def hello_world():
    print 'in hello world'
    return app.send_static_file('index.html')
    return 'Hello World!'

@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
     
