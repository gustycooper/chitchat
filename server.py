import psycopg2
import psycopg2.extras

import os
import uuid
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
users = {}

'''
roomsUsers is a dictionary where the key is a room and the value is a list of users
Three functions add, remove, and get the users from a room
Both rooms and users are strings
'''

roomsUsers = {}

def addUserToRoom(u,r):
    roomsUsers[r] = roomsUsers.get(r,[])+[u]

def removeUserFromRoom(u,r):
    roomsUsers[r].remove(u)

def specialUserRemove(u):
    for r,l in roomsUsers.items():
        if u in l:
            l.remove(u)
            break

def getUsersInRoom(r):
    return roomsUsers[r]

def connectToDBchat():
  connectionString = 'dbname=chitchat user=gusty password= host=localhost'
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
            names.append('Not Logged In')
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


    #for message in messages:
        #emit('message', message)

@socketio.on('search', namespace='/chat')
def search(searchString):
    if searchString[0] == '\\': # process command
        listUsers = False
        changedRoom = False
        u = users[session['uuid']]['username'] # get the user name
        l = searchString.split()
        cmdLen = len(l)
        if cmdLen == 2: # join \j room
            cmd,room = searchString.split()
        else: # list room \l or exit room \x
            cmd,room = l[0],'NOT'
        if cmd == '\\j' and cmdLen == 2: 
            # check for joining restricted rooms
            if room in ['COOPERS','CPSC350','CPSC110','CPSC125','RONSFOLKS']: #restricted rooms
                db = connectToDBchat()
                cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
                username = users[session['uuid']]
                username = username['username']
                print "search restricted room check", username
                # select * from users u join rooms r on u.username=r.username where u.username='gusty' and u.password=crypt('gusty',password) and r.roomname='COOPERS'
                query = cur.mogrify("""SELECT * FROM users u JOIN rooms r on u.username = r.username WHERE u.username = %s AND r.roomname = %s""", (username, room))
                cur.execute(query)
                fetchOne = cur.fetchone()
                print "search", fetchOne
                if fetchOne:
                    print "search restricted access allowed"
                else:
                    print "search restricted access not allowed"
                    room = session['room']
        ###
            if session['room'] != None:
                msg = "Joining room "+room+" and exiting room "+session['room']
                leave_room(session['room'])
                removeUserFromRoom(u,session['room'])
            else:
                msg = "Joining room "+room+" No longer in global space."
            join_room(room)
            addUserToRoom(u,room)
            session['room'] = room
            emit('roomUpdate',room)
            print 'search', "joining ", msg
            changedRoom = True
        elif cmd == '\\x' and cmdLen == 1:
            if session['room'] != None:
                msg = "Exiting room "+session['room']+" Now in global space."
                leave_room(session['room'])
                removeUserFromRoom(u,session['room'])
                addUserToRoom(u,'GLOBAL')
                session['room'] = None
                emit('roomUpdate','GLOBAL')
            else:
                msg = "You are not in a room to exit."
            print 'search', "exiting ", msg
            changedRoom = True
        elif cmd == '\\l' and cmdLen == 1:
            listUsers = True
            if session['room'] != None:
                msg = "Current room "+session['room']
                r = session['room']
            else:
                msg = "Current room GLOBAL"
                r = 'GLOBAL'
            print 'search', "listing room", msg
        else:
            msg = searchString+" is an invalid command."
        emit('searchStart')
        tmp = {'text':msg, 'name':'Command Results'}
        print 'search', tmp
        emit('searchResults', tmp, broadcast=False)
        if listUsers:
            for i in getUsersInRoom(r):
                tmp = {'text':i, 'name':r}
                print 'search', 'Users in room', tmp
                emit('searchResults', tmp, broadcast=False)
        # I AM HERE - Fix this to update the messages to reflect room changes
        if changedRoom:
            print "search", "changedRoom"
            emit('messageStart')
            db = connectToDBchat()
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if session['room'] != None:
               query = cur.mogrify("""SELECT * FROM messages WHERE room = %s""", (session['room'],))
            else:
               query = "SELECT * from messages"
            cur.execute(query)
            rows = cur.fetchall()
            #print 'search', "fetchall results", rows
            for i in rows:
                tmp = {'text':i[2], 'name':i[1]}
                #print 'search', 'search match', tmp
                emit('message', tmp, broadcast=False)
            else:
                tmp = {'text':'', 'name':''}
                emit('message', tmp, broadcast=False)
    else: # search for string
        specialSearch = False
        if len(searchString) > 3 and searchString[0] == '%' and searchString[1] == '*':
            searchString = searchString[3:]
            specialSearch = True
            print 'search', "special search"
        searchString = '%'+searchString+'%'
        print 'search',"searchString", searchString
        db = connectToDBchat()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if session['room'] != None and not specialSearch: # search room specific
            query = cur.mogrify("""SELECT * FROM messages WHERE (message LIKE %s OR userid LIKE %s) AND room = %s""", (searchString,searchString,session['room']))
        else: # search entire table without considering room
            query = cur.mogrify("""SELECT * FROM messages WHERE message LIKE %s OR userid LIKE %s""", (searchString,searchString ))
        print 'search',"query",query
        cur.execute(query)
        rows = cur.fetchall()
        print 'search', "fetchall results", rows
        emit('searchStart')
        if rows:
            for i in rows:
                tmp = {'text':i[2], 'name':i[1]}
                print 'search', 'search match', tmp
                emit('searchResults', tmp, broadcast=False)
        else:
            tmp = {'text':'NO MATCHES', 'name':''}
            print 'search', 'search nomatch', tmp
            emit('searchResults', tmp, broadcast=False)
 
@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    username = users[session['uuid']]['username']
    print 'new_message',"message", message
    print 'new_message',"userename", username
    print 'new_message',"tmp", tmp
    if session['room'] != None:
        emit('message', tmp, broadcast=True, room=session['room'])
    else:
        emit('message', tmp, broadcast=True)
    db = connectToDBchat()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if session['room'] != None:
        query = cur.mogrify("""INSERT INTO messages (userid,message,room) VALUES (%s,%s,%s)""", (username, message,session['room']))
    else:
        query = cur.mogrify("""INSERT INTO messages (userid,message,room) VALUES (%s,%s,NULL)""", (username, message))
        
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
def on_login(pwRoom):
    pw,room = pwRoom.split()
    if room == 'undefined':
        room = None
        prRoom = "None"
    else:
        prRoom = room
    print 'on_login pw:'+pw+" prRoom:"+prRoom+" pwRoom:"+pwRoom
    #users[session['uuid']]={'username':message}
    #updateRoster()
    db = connectToDBchat()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    username = users[session['uuid']]
    username = username['username']
    print "on_login", username
    if room in ['COOPERS','CPSC350','CPSC110','CPSC125','RONSFOLKS']: #restricted rooms
        # select * from users u join rooms r on u.username=r.username where u.username='gusty' and u.password=crypt('gusty',password) and r.roomname='COOPERS'
        query = cur.mogrify("""SELECT * FROM users u JOIN rooms r on u.username = r.username WHERE u.username = %s AND u.password = crypt(%s,password) AND r.roomname = %s""", (username, pw, room))
    else: # plain old string rooms 
        query = cur.mogrify("""SELECT * FROM users WHERE username = %s AND password = crypt(%s,password)""", (username, pw))
    print "on_login", username, pw, query
    cur.execute(query)
    fetchOne = cur.fetchone()
    print "on_login", fetchOne
    if fetchOne:
       session['room'] = room
       if room != None:
           join_room(room)
           emit('roomUpdate',room)
           addUserToRoom(username,room)
       else:
           emit('roomUpdate','GLOBAL')
           addUserToRoom(username,'GLOBAL')
       restrictions = fetchOne[3] # for future use
       print "on_login", "login successful", fetchOne, restrictions
       #updateRoster()
       db = connectToDBchat()
       cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
       if session['room'] != None:
          query = cur.mogrify("""SELECT * FROM messages WHERE room = %s""", (room,))
       else:
          query = "SELECT * from messages"
       cur.execute(query)
       rows = cur.fetchall()
       #print 'search', "fetchall results", rows
       for i in rows:
           tmp = {'text':i[2], 'name':i[1]}
           #print 'search', 'search match', tmp
           emit('message', tmp, broadcast=False)
       else:
           tmp = {'text':'', 'name':''}
           emit('message', tmp, broadcast=False)
    else:
       print "on_login", "login unsuccessful"
       users[session['uuid']]={'username':''}
       #updateRoster()
       emit('failedLogin')
    
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'on_disconnect'
    if session['uuid'] in users:
        print 'on_disconnect', users[session['uuid']]
        u = users[session['uuid']]['username'] # get the user name
        print 'on_disconnect', u
        specialUserRemove(u)
        #removeUserFromRoom(u,session['room'])
        del users[session['uuid']]
        updateRoster()
        emit('failedLogin')

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
     
