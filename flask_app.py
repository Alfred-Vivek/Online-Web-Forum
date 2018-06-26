from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from sqlalchemy import Table
import json
import datetime
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecRetKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forumDB.db'

db=SQLAlchemy(app)
class Logindetails(db.Model):
	email=db.Column(db.String(100), primary_key=True)
	username=db.Column(db.String(100))
	password=db.Column(db.String(100))

	def __init__(self,email,username,password):
		self.email=email
		self.username=username
		self.password=password

class Topicdetails(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email=db.Column(db.String(100), db.ForeignKey('logindetails.email'))
	title = db.Column(db.String, nullable=False)
	message = db.Column(db.String, nullable=False)
	category = db.Column(db.String, nullable=False)
	time_stamp = db.Column(db.String, nullable=False)
	approval = db.Column(db.Integer)
	replies = db.Column(db.Integer)
	views = db.Column(db.Integer)
	likes = db.Column(db.Integer)
	dislikes = db.Column(db.Integer)

	def __init__(self,email,title,message,category,time_stamp,approval,replies,views,likes,dislikes):
		self.email=email
		self.title=title
		self.message=message
		self.category=category
		self.time_stamp=time_stamp
		self.approval = approval
		self.replies = replies
		self.views = views
		self.likes=likes
		self.dislikes=dislikes

class Replydetails(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email=db.Column(db.String(100), db.ForeignKey('logindetails.email'))
	quesid=db.Column(db.Integer, db.ForeignKey('topicdetails.id'))
	message = db.Column(db.String, nullable=False)
	time_stamp = db.Column(db.String, nullable=False)
	likes = db.Column(db.Integer)
	dislikes = db.Column(db.Integer)

	def __init__(self,email,quesid,message,time_stamp,likes,dislikes):
		self.email=email
		self.quesid=quesid
		self.message=message
		self.time_stamp=time_stamp
		self.likes=likes
		self.dislikes=dislikes
db.create_all()

def authenticate(e,p):
	data=Logindetails.query.filter_by(email=e).filter_by(password=p).all()
	if len(data)>0:
		return True
	return False

def categories():
	category={}
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	for i in alltopics:
		if i.category not in category.keys():
			category[i.category] = 1
		else:
			category[i.category] += 1
	return category

@app.route('/')
def homepage():
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	category = categories()
	return render_template('homepage.html',alltopics=alltopics, category=category)

@app.route('/admin')
def admin():
	try:
		if session['logged_in'] == True:
			alltopics = Topicdetails.query.all()
			category = categories()
			return render_template('admin.html',alltopics=alltopics, category=category)
	except:
		return render_template('login.html',error="Please Login!!")
@app.route('/myprofile')
def myprofile():
	try:
		if session['logged_in'] == True:
			alltopics = Topicdetails.query.filter_by(email=session['logged_email']).all()
			category = categories()
			return render_template('myprofile.html',alltopics=alltopics, category=category)
	except:
		return render_template('login.html',error="Please Login!!")

@app.route('/approve', methods=['GET', 'POST'])
def approve():
	error=""
	if request.method == 'POST':
		topicdata=Topicdetails.query.filter_by(id=request.form['entry']).one()
		topicdata.approval = 1	
		db.session.commit()
	return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error=""
	if request.method == 'POST':
		if request.form['email']=="admin" and request.form['password']=="123456":
			session['logged_in'] = True
			session['logged_email'] = request.form['email']			
			return redirect(url_for('admin'))
		if authenticate(request.form['email'],request.form['password']):			
			session['logged_in'] = True
			session['logged_email'] = request.form['email']		
			return redirect(url_for('homepage'))
		else:
			error = "Invalid Credentials"
	return render_template('login.html',error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	error = ""
	if request.method == 'POST':
		session['logged_in'] = True
		newUser = Logindetails(email=request.form['email'],username=request.form['username'],password=request.form['password'])
		db.session.add(newUser)
		db.session.commit()
		return render_template('login.html', error=error)
	return render_template('login.html', error=error)

@app.route('/changepass', methods=['GET', 'POST'])
def changepass():
	try:
		if session['logged_in'] == True:
			if request.method == 'POST':		
				if request.form['pass'] == request.form['cpass']:
					data=Logindetails.query.filter_by(email=session['logged_email']).one()
					data.password = request.form['pass']
					db.session.commit()
					return redirect(url_for('homepage'))
				else:
					error = "Passwords do not match"
					return render_template('changepass.html', error=error)
			else:
				return render_template('changepass.html', error="")
	except:
		return render_template('login.html',error="Please login to continue!")

@app.route('/newtopic')
def newtopic():
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	category = categories()
	return render_template('newtopic.html',alltopics=alltopics, category=category)

@app.route('/uploadtopic', methods=['GET', 'POST'])
def uploadtopic():
	if request.method == 'POST':
		try:
			if session['logged_in'] == True:
				date = str(datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
				newTopic = Topicdetails(email=session['logged_email'],title=request.form['title'],message=request.form['message'],category=request.form['category'],time_stamp=date,approval=0,replies=0,views=0,likes=0,dislikes=0)
				db.session.add(newTopic)
				db.session.commit()
				alltopics = Topicdetails.query.filter_by(approval=1).all()
				category = categories()
				return render_template('newtopic.html',alltopics=alltopics, category=category)
			else:
				return render_template('login.html',error="Please login to continue!")

		except:
			return render_template('login.html',error="Please login to continue!")

@app.route('/deletetopic/<id>')
def deletetopic(id):
	try:
		if session['logged_in'] == True:
			alltopics = Topicdetails.query.filter_by(id=id).delete()
			db.session.commit()
			return redirect(url_for('homepage'))
	except:
		return render_template('login.html',error="Please login to continue!")

@app.route('/postreply', methods=['GET', 'POST'])
def postreply():
	if request.method == 'POST':
		try:
			if session['logged_in'] == True:
				date = str(datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
				newReply = Replydetails(email=session['logged_email'],quesid=request.form['quesid'],message=request.form['reply'],time_stamp=date,likes=0,dislikes=0)
				db.session.add(newReply)
				topicreply=Topicdetails.query.filter_by(id=request.form['quesid']).one()
				topicreply.replies = topicreply.replies + 1
				db.session.commit()
			alltopics = Topicdetails.query.filter_by(approval=1).all()
			topic = Topicdetails.query.filter_by(id=request.form['quesid']).one()
			allreplies = Replydetails.query.filter_by(quesid=request.form['quesid']).all()
			category = categories()
			return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)
		except:
			return render_template('login.html',error="Please login to continue!")

@app.route('/deletereply/<id>')
def deletereply(id):
	quesid = Replydetails.query.filter_by(id=id).one().quesid
	reply = Replydetails.query.filter_by(id=id).delete()	
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	topic = Topicdetails.query.filter_by(id=quesid).one()
	topic.replies = topic.replies - 1
	db.session.commit()
	allreplies = Replydetails.query.filter_by(quesid=quesid).all()
	category = categories()
	return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)

@app.route('/topicpage/<id>')
def topicpage(id):
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	topic = Topicdetails.query.filter_by(id=id).one()
	topic.views = topic.views +1
	db.session.commit()
	allreplies = Replydetails.query.filter_by(quesid=id).all()
	category = categories()
	return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)

@app.route('/like', methods = ['GET','POST'])
def handlevote1():
	topiclike = Topicdetails.query.filter_by(id = request.form['topic_id']).one()
	topiclike.likes = topiclike.likes + 1
	db.session.commit()
	data = topiclike.likes
	return jsonify({'data': data})

@app.route('/dislike', methods = ['GET','POST'])
def handlevote2():
	topicdislike = Topicdetails.query.filter_by(id = request.form['topic_id']).one()
	topicdislike.dislikes = topicdislike.dislikes + 1
	db.session.commit()
	data = topicdislike.dislikes
	return jsonify({'data': data})

@app.route('/rlike', methods = ['GET','POST'])
def handlevote3():
	replylike = Replydetails.query.filter_by(id = request.form['i_id']).one()
	replylike.likes = replylike.likes + 1
	db.session.commit()
	data = replylike.likes
	return jsonify({'data': data})

@app.route('/rdislike', methods = ['GET','POST'])
def handlevote4():
	replydislike = Replydetails.query.filter_by(id = request.form['i_id']).one()
	replydislike.dislikes = replydislike.dislikes + 1
	db.session.commit()
	data = replydislike.dislikes
	return jsonify({'data': data})

@app.route('/updatereply', methods = ['GET','POST'])
def updatereply():
	reply = Replydetails.query.filter_by(id = request.form['replyid']).one()
	reply.message = request.form['message']
	db.session.commit()
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	topic = Topicdetails.query.filter_by(id=request.form['quesid']).one()
	allreplies = Replydetails.query.filter_by(quesid=request.form['quesid']).all()
	category = categories()
	return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)

@app.route('/updatetopic', methods = ['GET','POST'])
def updatetopic():
	topic = Topicdetails.query.filter_by(id = request.form['quesid']).one()
	topic.title = request.form['title']
	topic.message = request.form['message']
	db.session.commit()
	alltopics = Topicdetails.query.filter_by(approval=1).all()
	topic = Topicdetails.query.filter_by(id=request.form['quesid']).one()
	allreplies = Replydetails.query.filter_by(quesid=request.form['quesid']).all()
	category = categories()
	return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)

@app.route('/category/<id>')
def category(id):
	alltopics = Topicdetails.query.filter_by(category=id).all()
	category = categories()
	return render_template('homepage.html', alltopics=alltopics, category=category)

@app.route('/searchedtopic', methods=['GET', 'POST'])
def searchedtopic():
	if request.method == 'POST':
		if len(Topicdetails.query.filter_by(title=request.form['topic']).all()) > 0:
			alltopics = Topicdetails.query.filter_by(approval=1).all()
			topic = Topicdetails.query.filter_by(title=request.form['topic']).one()
			topic.views = topic.views +1
			db.session.commit()
			id = Topicdetails.query.filter_by(title=request.form['topic']).one().id
			allreplies = Replydetails.query.filter_by(quesid=id).all()
			category = categories()
			return render_template('replies.html', topic=topic, alltopics=alltopics, allreplies=allreplies, category=category)
		else:
			return redirect(url_for('homepage'))
	else:
		return render_template('login.html',error="Please login to continue!")

@app.route('/logout')
def logout():
	session['logged_in'] = False
	session['logged_email'] = ""
	return redirect(url_for('homepage'))

if __name__ == '__main__':
	app.run(debug=True)