import re
from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy		# database ORM import
from sqlalchemy.sql import func
from sqlalchemy import desc
from flask_migrate import Migrate			# used by SQLAlchemy to actually create db/tables
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'I drink and I know things' # set a secret key for security purposes
bcrypt = Bcrypt(app)
# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devs_on_deck.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# an instance of the ORM
db = SQLAlchemy(app)
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)
## !!!!!!!!!!!!!!!!!!!!!!!!!! ##
## Always run 'flask db init' ##
## in console to initialize   ##
## DB once per project.		  ##
## !!!!!!!!!!!!!!!!!!!!!!!!!! ##
## -------------------------- ##
## !!!!!!!!!!!!!!!!!!!!!!!!!! ##
## USE WHEN classes are       ##
## changed/added/deleted      ##
## 'flask db migrate' readies ##
## changes					  ##
## 'flask db upgrade' executes##
## the changes                ##
## !!!!!!!!!!!!!!!!!!!!!!!!!! ##


# many-to-many relationships
dev_lang_table = db.Table('dev_langs',
				db.Column('dev_id', db.Integer, db.ForeignKey('devs.id'), primary_key=True),
				db.Column('lang_id', db.Integer, db.ForeignKey('langs.id'), primary_key=True)
				)
pos_lang_table = db.Table('position_langs',
				db.Column('pos_id', db.Integer, db.ForeignKey('positions.id'), primary_key=True),
				db.Column('lang_id', db.Integer, db.ForeignKey('langs.id'), primary_key=True)
				)

dev_frame_lib_table = db.Table('dev_frame_lib',
				db.Column('dev_id', db.Integer, db.ForeignKey('devs.id'), primary_key=True),
				db.Column('framelib_id', db.Integer, db.ForeignKey('framelib.id'), primary_key=True)
				)
pos_frame_lib_table = db.Table('position_frame_lib',
				db.Column('pos_id', db.Integer, db.ForeignKey('positions.id'), primary_key=True),
				db.Column('framelib_id', db.Integer, db.ForeignKey('framelib.id'), primary_key=True)
				)

class Dev(db.Model):	
	__tablename__ = "devs"
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(255))
	last_name = db.Column(db.String(255))
	email = db.Column(db.String(255))
	password = db.Column(db.String(255))
	address = db.Column(db.String(255))
	address_2 = db.Column(db.String(255))
	address_city = db.Column(db.String(255))
	address_state = db.Column(db.Integer)
	profile_bio = db.Column(db.Text)
	status = db.Column(db.Integer)
	date_created = db.Column(db.DateTime, server_default=func.now())    
	date_updated = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
	devs_skills_langs = db.relationship('Language', secondary=dev_lang_table)
	devs_skills_frame_lib = db.relationship('FrameLib', secondary=dev_frame_lib_table)

class Org(db.Model):	
	__tablename__ = "orgs"
	id = db.Column(db.Integer, primary_key=True)
	positions = db.relationship('Position', backref='orgs_pos')
	org_name = db.Column(db.String(255))
	rep_name = db.Column(db.String(255))
	email = db.Column(db.String(255))
	password = db.Column(db.String(255))
	address = db.Column(db.String(255))
	address_2 = db.Column(db.String(255))
	address_city = db.Column(db.String(255))
	address_state = db.Column(db.String(50))
	date_created = db.Column(db.DateTime, server_default=func.now())    
	date_updated = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Position(db.Model):	
	__tablename__ = "positions"
	id = db.Column(db.Integer, primary_key=True)
	org = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
	name = db.Column(db.String(255))
	description = db.Column(db.Text)
	date_created = db.Column(db.DateTime, server_default=func.now())    
	date_updated = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
	pos_skills_langs = db.relationship('Language', secondary=pos_lang_table)
	pos_skills_frame_lib = db.relationship('FrameLib', secondary=pos_frame_lib_table)

class Language(db.Model):	
	__tablename__ = "langs"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	img = db.Column(db.String(255))

class FrameLib(db.Model):	
	__tablename__ = "framelib"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	img = db.Column(db.String(255))

class State(db.Model):	
	__tablename__ = "states"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	abbrev = db.Column(db.String(4))


################
## ROOT ROUTE ##
################
@app.route('/')
def index():
	if 'userid' in session:
		if session['acct_type'] == "dev":
			return redirect('/devs/dashboard')
		else:
			return redirect('/orgs/dashboard')
	# Dev registration always default
	else:
		return redirect('/devs/register')


#########################################
## VALIDATE FORM DATA and REGISTER DEV ##
#########################################
@app.route('/devs/signup', methods=['POST'])
def devs_signup():
	is_valid = True
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
	# Password regex - uppercase, lowercase, and number required
	PW_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).*$')

	# Validate name fields
	if len(request.form['fname']) < 2 or len(request.form['lname']) < 2:
		flash("Both your first and last name must be at least 2 characters long.", 'reg_error')
		is_valid = False
	else:
		if NAME_REGEX.match(request.form['fname']) is None or NAME_REGEX.match(request.form['lname']) is None:
			flash("Your name can only contain letters.", 'reg_error')
			is_valid = False

	if EMAIL_REGEX.match(request.form['email']):
		checkEmail = Dev.query.filter_by(email=request.form['email']).first()
		if checkEmail:
			flash("Account already exists with this Email.", 'reg_error')
			is_valid = False
	else:
		flash("Email address not valid.", 'reg_error')
		is_valid = False

	# Validate Password
	if len(request.form['password']) < 5:
		flash("Password must be a minimum of 5 characters.", 'reg_error')
		is_valid = False
	elif PW_REGEX.match(request.form['password']) is None:
		flash("Password requires at least one uppercase, one lowercase letter, and a number.", 'reg_error')
		is_valid = False
	else:
		if request.form['confirm_password'] != request.form['password']:
			flash("Passwords did not match.", 'reg_error')
			is_valid = False

	# City and State at least required for location
	if len(request.form['addr_city']) < 2 or len(request.form['addr_state']) < 2:
		flash("Must enter at least a City and State for your address.", 'reg_error')
		is_valid = False

	# Record data and flash success
	if is_valid:
		new_instance_of_dev = Dev(first_name=request.form['fname'], last_name=request.form['lname'], email=request.form['email'], password=bcrypt.generate_password_hash(request.form['password']), address=request.form['addr_street'], address_2=request.form['addr_2'], address_city=request.form['addr_city'], address_state=request.form['addr_state'], status=1)		
		db.session.add(new_instance_of_dev)
		db.session.commit()
		session['userid'] = new_instance_of_dev.id
		session['name'] = request.form['fname'] + " " + request.form['lname']
		session['acct_type'] = "dev"

		return redirect('/devs/skills/languages')

	return redirect('/')


#######################################
## VALIDATE FORM DATA and UPDATE DEV ##
#######################################
@app.route('/devs/profile/edit/update', methods=['POST'])
def dev_update_profile():
	if 'userid' not in session:
		return redirect('/')

	is_valid = True
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

	cur_user = Dev.query.get(session['userid'])

	# Validate name fields
	if len(request.form['fname']) < 2 or len(request.form['lname']) < 2:
		flash("Both your first and last name must be at least 2 characters long.", 'reg_error')
		is_valid = False
	else:
		if NAME_REGEX.match(request.form['fname']) is None or NAME_REGEX.match(request.form['lname']) is None:
			flash("Your name can only contain letters.", 'reg_error')
			is_valid = False

	if cur_user.email != request.form['email']:
		if EMAIL_REGEX.match(request.form['email']):
			checkEmail = Dev.query.filter_by(email=request.form['email']).first()
			if checkEmail:
				flash("Account already exists with this Email.", 'reg_error')
				is_valid = False
		else:
			flash("Email address not valid.", 'reg_error')
			is_valid = False

	# City and State at least required for location
	if len(request.form['addr_city']) < 2 or len(request.form['addr_state']) < 2:
		flash("Must enter at least a City and State for your address.", 'reg_error')
		is_valid = False

	# Record data and flash success
	if is_valid:
		cur_user.first_name = request.form['fname']
		cur_user.last_name = request.form['lname']
		cur_user.email = request.form['email']
		cur_user.address = request.form['addr_street']
		cur_user.address_2 = request.form['addr_2']
		cur_user.address_city = request.form['addr_city']
		cur_user.address_state = request.form['addr_state']
		db.session.commit()

		return redirect('/devs/dashboard')

	return redirect('/devs/profile/edit')


#########################################
## VALIDATE FORM DATA and REGISTER ORG ##
#########################################
@app.route('/orgs/signup', methods=['POST'])
def orgs_signup():
	is_valid = True
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	NAME_REGEX = re.compile(r'^[a-zA-Z\s]+$')
	# Password regex - uppercase, lowercase, and number required
	PW_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).*$')

	# Validate Org name
	if len(request.form['org_name']) < 2:
		flash("Your Organization's name must be at least 2 characters long.", 'reg_error')
		is_valid = False

	# Validate Rep name
	if len(request.form['rep_name']) < 2:
		flash("Your Organization's name must be at least 2 characters long.", 'reg_error')
		is_valid = False
	else:
		if NAME_REGEX.match(request.form['rep_name']) is None:
			flash("Your representative's name can only contain letters.", 'reg_error')
			is_valid = False

	if EMAIL_REGEX.match(request.form['email']):
		checkEmail = Org.query.filter_by(email=request.form['email']).first()
		if checkEmail:
			flash("Account already exists with this Email.", 'reg_error')
			is_valid = False
	else:
		flash("Email address not valid.", 'reg_error')
		is_valid = False

	# Validate Password
	if len(request.form['password']) < 5:
		flash("Password must be a minimum of 5 characters.", 'reg_error')
		is_valid = False
	elif PW_REGEX.match(request.form['password']) is None:
		flash("Password requires at least one uppercase, one lowercase letter, and a number.", 'reg_error')
		is_valid = False
	else:
		if request.form['confirm_password'] != request.form['password']:
			flash("Passwords did not match.", 'reg_error')
			is_valid = False

	# Full address required for organization
	if len(request.form['addr_street']) < 5:
		flash("Your Organization's street address does not appear valid.", 'reg_error')
		is_valid = False
	
	if len(request.form['addr_city']) < 2:
		flash("Must enter a City for your address.", 'reg_error')
		is_valid = False

	if len(request.form['addr_state']) < 2:
		flash("Must enter a State for your address.", 'reg_error')
		is_valid = False

	# Record data and flash success
	if is_valid:
		new_instance_of_org = Org(org_name=request.form['org_name'], rep_name=request.form['rep_name'], email=request.form['email'], password=bcrypt.generate_password_hash(request.form['password']), address=request.form['addr_street'], address_2=request.form['addr_2'], address_city=request.form['addr_city'],address_state=request.form['addr_state'])		
		db.session.add(new_instance_of_org)
		db.session.commit()
		session['userid'] = new_instance_of_org.id
		session['name'] = request.form['org_name']
		session['acct_type'] = "org"

		return redirect('/orgs/dashboard')

	return redirect('/orgs/register')


############################################
## VALIDATE FORM DATA and CREATE POSITION ##
############################################
@app.route('/orgs/jobs/create', methods=['POST'])
def create_position():
	if 'userid' not in session:
		return redirect('/')
	elif session['acct_type'] != 'org':
		return redirect('/')

	is_valid = True

	# Validate Org name
	if len(request.form['pos_name']) < 2:
		flash("The Job title must be at least 2 characters long.", 'reg_error')
		is_valid = False

	# Validate Rep name
	if len(request.form['pos_desc']) < 15:
		flash("Your description must be at least 15 characters long.", 'reg_error')
		is_valid = False

	# Record data and flash success
	if is_valid:
		new_instance_of_pos = Position(org=session['userid'], name=request.form['pos_name'], description=request.form['pos_desc'])
		db.session.add(new_instance_of_pos)
		db.session.commit()

		curPos = Position.query.get(new_instance_of_pos.id)

		if len(request.form.getlist('dev_lang_input')) > 0:
			for langID in request.form.getlist('dev_lang_input'):
				curLang = Language.query.get(langID)
				curPos.pos_skills_langs.append(curLang)
			db.session.commit()

		if ( len(request.form.getlist('dev_framework_input')) > 0 ):
			for frmwrkID in request.form.getlist('dev_framework_input'):
				curFrmwrk = FrameLib.query.get(frmwrkID)
				curPos.pos_skills_frame_lib.append(curFrmwrk)
			db.session.commit()

		return redirect('/orgs/dashboard')

	return redirect('/orgs/jobs/new')


####################
## DEVS DASHBOARD ##
####################
@app.route('/devs/dashboard')
def devs_dashboard():
	if 'userid' not in session:
		return redirect('/')

	cur_user = Dev.query.get(session['userid'])
	cur_state = State.query.get(cur_user.address_state)
	all_jobs = Position.query.all()

	return render_template("devs_dashboard.html", cur_dev=cur_user, dev_langs=cur_user.devs_skills_langs, dev_frmwrks=cur_user.devs_skills_frame_lib, loc_state=cur_state.abbrev, jobs=all_jobs)


#######################
## VIEW DEVS PROFILE ##
#######################
@app.route('/devs/profile/<dev_id>')
def devs_profile(dev_id):
	if 'userid' not in session:
		return redirect('/')

	cur_user = Dev.query.get(dev_id)
	cur_state = State.query.get(cur_user.address_state)

	return render_template("devs_dashboard.html", cur_dev=cur_user, dev_langs=cur_user.devs_skills_langs, dev_frmwrks=cur_user.devs_skills_frame_lib, loc_state=cur_state.abbrev)


####################
## ORGS DASHBOARD ##
####################
@app.route('/orgs/dashboard')
def orgs_dashboard():
	if 'userid' not in session:
		return redirect('/')

	cur_org = Org.query.get(session['userid'])
	all_devs = Dev.query.all()

	return render_template("orgs_dashboard.html", cur_org=cur_org, all_devs=all_devs, pos_to_fill=cur_org.positions)


#######################
## VIEW ORGS PROFILE ##
#######################
@app.route('/orgs/profile/<org_id>')
def orgs_profile(org_id):
	if 'userid' not in session:
		return redirect('/')

	if int(session['userid']) == int(org_id):
		return redirect('/orgs/dashboard')

	cur_org = Org.query.get(org_id)
	# all_devs = Dev.query.all()

	return render_template("orgs_dashboard.html", cur_org=cur_org, pos_to_fill=cur_org.positions)
	# all_devs=all_devs, 


######################
## VIEW JOB POSTING ##
######################
@app.route('/orgs/jobs/<pos_id>')
def view_position(pos_id):
	if 'userid' not in session:
		return redirect('/')

	if session['acct_type'] == 'dev':
		cur_user = Dev.query.get(session['userid'])
	else:
		cur_user = Org.query.get(session['userid'])

	cur_pos = Position.query.get(pos_id)
	cur_org = Org.query.get(cur_pos.org)

	return render_template("job_post.html", cur_job=cur_pos, cur_org=cur_org, cur_user=cur_user)


#######################
## DEVS REGISTRATION ##
#######################
@app.route('/devs/register')
def devs_register():
	if 'userid' in session:
		return redirect('/')

	state_list = State.query.all()
	return render_template('dev_reg.html', all_states=state_list)


#######################
## ORGS REGISTRATION ##
#######################
@app.route('/orgs/register')
def orgs_register():
	if 'userid' in session:
		return redirect('/')

	state_list = State.query.all()
	return render_template('org_reg.html', all_states=state_list)


################
## USER LOGIN ##
################
@app.route('/devs/login')
def login():
	if 'userid' in session:
		return redirect('/')

	return render_template('dev_login.html')



#########################
## VALIDATE USER LOGIN ##
#########################
@app.route('/devs/validate/login', methods=['POST'])
def validate_login():
	loginUser = Dev.query.filter_by(email=request.form['email']).first()

	if loginUser:
		pw = bcrypt.check_password_hash(loginUser.password, request.form['password'])

		if pw:
			session['userid'] = loginUser.id
			session['name'] = loginUser.first_name + " " + loginUser.last_name
			session['acct_type'] = "dev"
			return redirect('/devs/dashboard')
		else:
			flash("Password incorrect! Please try again.", 'login_error')
	else:
		flash("Email not recognized", 'login_error')

	return redirect('/devs/login')


###############
## ORG LOGIN ##
###############
@app.route('/orgs/login')
def org_login():
	if 'userid' in session:
		return redirect('/')

	return render_template('org_login.html')



########################
## VALIDATE ORG LOGIN ##
########################
@app.route('/orgs/validate/login', methods=['POST'])
def org_validate_login():
	loginOrg = Org.query.filter_by(email=request.form['email']).first()

	if loginOrg:
		pw = bcrypt.check_password_hash(loginOrg.password, request.form['password'])

		if pw:
			session['userid'] = loginOrg.id
			session['name'] = loginOrg.org_name
			session['acct_type'] = "org"
			return redirect('/orgs/dashboard')
		else:
			flash("Password incorrect! Please try again.", 'login_error')
	else:
		flash("Email not recognized", 'login_error')

	return redirect('/orgs/login')


#######################
## NEW POSITION FORM ##
#######################
@app.route('/orgs/jobs/new')
def new_position():
	if 'userid' not in session:
		return redirect('/')
	elif session['acct_type'] != 'org':
		return redirect('/')

	cur_org = Org.query.get(session['userid'])
	langs_list = Language.query.all()
	frmwrk_list = FrameLib.query.all()

	return render_template('org_position.html', cur_org=cur_org, all_langs=langs_list, all_frmwrks=frmwrk_list)


###############################
## UPDATE SKILLS - LANGUAGES ##
###############################
@app.route('/devs/skills/languages')
def skills_languages():
	if 'userid' not in session:
		return redirect('/')

	langs_list = Language.query.all()
	cur_user = Dev.query.get(session['userid'])

	cur_langs_id_list = []
	for lang in cur_user.devs_skills_langs:
		cur_langs_id_list.append(lang.id)

	return render_template("dev_languages.html", all_langs=langs_list, dev_langs=cur_user.devs_skills_langs, dev_langs_id=cur_langs_id_list, cur_dev=cur_user)


################################
## UPDATE SKILLS - FRAMEWORKS ##
################################
@app.route('/devs/skills/frameworks')
def skills_frameworks():
	if 'userid' not in session:
		return redirect('/')

	frmwrk_list = FrameLib.query.all()
	cur_user = Dev.query.get(session['userid'])

	cur_frmwrk_id_list = []
	for frmwrk in cur_user.devs_skills_frame_lib:
		cur_frmwrk_id_list.append(frmwrk.id)

	return render_template("dev_frameworks.html", all_frmwrks=frmwrk_list, dev_frmwrks=cur_user.devs_skills_frame_lib, dev_frmwrks_id=cur_frmwrk_id_list)


#######################
## DEVS EDIT PROFILE ##
#######################
@app.route('/devs/profile/edit')
def dev_edit_profile():
	if 'userid' not in session:
		return redirect('/')

	curDev = Dev.query.get(session['userid'])
	state_list = State.query.all()

	return render_template('dev_edit.html', cur_dev=curDev, all_states=state_list)


###########################
## RECORD SKILLS UPDATES ##
###########################
@app.route('/devs/update_skills', methods=['POST'])
def dev_update_skills():
	if 'userid' not in session:
		return redirect('/')

	curDev = Dev.query.get(session['userid'])

	if ( len(request.form.getlist('dev_lang_input')) > 0 or 'dev_bio' in request.form):
		curDev.profile_bio = request.form['dev_bio']
		curDev.devs_skills_langs = []
		for langID in request.form.getlist('dev_lang_input'):
			curLang = Language.query.get(langID)
			curDev.devs_skills_langs.append(curLang)
		db.session.commit()
		return redirect('/devs/skills/frameworks')

	elif ( len(request.form.getlist('dev_framework_input')) > 0 ):
		curDev.devs_skills_frame_lib = []
		for frmwrkID in request.form.getlist('dev_framework_input'):
			curFrmwrk = FrameLib.query.get(frmwrkID)
			curDev.devs_skills_frame_lib.append(curFrmwrk)
		db.session.commit()
		return redirect('/devs/dashboard')

	# TEMPORARY
	return redirect('/')


############
## LOGOUT ##
############
@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')




if __name__=="__main__":
	app.run(debug=True)

    