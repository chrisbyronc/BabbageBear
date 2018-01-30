from flask import Flask, render_template, Response, flash, redirect, request, session, abort, url_for
from flask_socketio import SocketIO
from flask_uwsgi_websocket import GeventWebSocket
from camera import VideoCamera
from flask_bootstrap import Bootstrap
import enc
import os

# @ToDo pass in error for login
# @ToDo clean up


app = Flask(__name__)
websocket = GeventWebSocket(app)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('pages/login.html')
    else:
        return render_template('pages/index.html')
 
@app.route('/login', methods=['POST'])
def do_admin_login():
	if enc.decipher(request.form['username'], request.form['password']):
		session['logged_in'] = True
		return redirect(url_for('home'))
	else:
		flash('wrong password!')
	return home()

@app.errorhandler(404)
def page_not_found(e):
	return render_template('errors/error404.html')

@app.errorhandler(405)
def page_not_found(e):
	return render_template('errors/error405.html')

@app.errorhandler(500)
def page_not_found(e):
	return render_template('errors/error500.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	if not session.get('logged_in'):
		return redirect(url_for('home'))
	else:
		return Response(gen(VideoCamera()),
			mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0')