# chitchat
This Flask-based web-server implements a simple chit-chat service.  Users can login and then send messages to everyone else that is logged in.

The login panel allows for thee entries:

Username:
Password:
Room:

You have to have a user account with a password to login.  You can examine the file chitchat.sql to see the list of users and their passwords.

There are two types of rooms.

1. Restricted rooms.  I created 5 restricted rooms: COOPERS, RONSFOLKS, CPSC110, CPSC125, and CPSC350.  I added the following users to these rooms. Only these users can login and join (/j) these rooms.
COOPERS gusty jerrianne jeremy brandalee zachary emily
RONSFOLKS raz ann lazy gusty
CPSC110 gusty sepher shana shehan
CPSC125 tyler campbell eric zach gusty
CPSC350 gusty taka ron chris thomas shehan shana tyler campbell sepehr zach eric

2. String rooms.  All other rooms are simply strings.  As long as two users agree on a string, they can enter a room and chat.  For example gusty and raz can login and /j room B.  If you do not provide a room on the initial login you are placed in a room GLOBAL.  When in GLOBAL, your messages to to everyone; however, you do not see messages from other rooms.

The messages entry allows users to send messages.  When you login and /j a room, all of the messages from that room are displayed.

The search entry allows for searching strings and entering commands.  The search is restricted to the room you are in.  The commands are th following:

\x - exit current room into room GLOBAL
\j <room> - join the room <room> (and exit current room).  You cannot join a restricted room if you are not a member.  You can join any string room.
\l - list all of the people in your room
%* <string> - special search.  Search the entire DB for <string>.  Not restricted by the current room.
