############
# IMPORTS  #
############

import pandas as pd
import numpy as np
from flask import Flask, redirect, render_template, request, \
                    url_for,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, LoginManager, logout_user, \
                        UserMixin, current_user
from werkzeug.security import check_password_hash #, generate_password_hash
from flask_migrate import Migrate
from collections import OrderedDict
import matplotlib
matplotlib.use("Agg")
import os.path
from datetime import datetime
import pytz
import csv
import json
import logging
from difflib import SequenceMatcher
log = logging.getLogger('log')

from groupeng.process_inputs import process_csv

########################
# BACKGROUND SETTINGS  #
########################

keys = {}
with open("../keys.txt") as f:
    for line in f:
       (key, val) = line.split()
       keys[key] = val

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SQLALCHEMY_DATABASE_URI = \
"mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=keys["username"],
    password=keys["password"],
    hostname=keys["hostname"],
    databasename=keys["databasename"],
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db,compare_type=True)
app.secret_key = keys["secret_key"]

########################
# BACKGROUND SETTINGS  #
########################

login_manager = LoginManager()
login_manager.init_app(app)

#Update databases with export FLASK_APP=flask_app.py,
#flask db migrate, flask db upgrade
#Add user with u = User(username="abcd",
#password_hash=generate_password_hash("8fwe5jYCE98lXl0ZovYW"))
#db.session.add(u), db.session.commit()

###########################
# DATABASE TABLE SETTINGS #
###########################

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username

class Classroom(db.Model):

    __tablename__ = "class"

    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.String(32))
    key = db.Column(db.String(32))
    value = db.Column(db.String(32))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=manager_id)

class Specification(db.Model):

    __tablename__ = "specifications"

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=manager_id)
    header = db.Column(db.String(32))
    value  = db.Column(db.String(32))
    priority = db.Column(db.Integer)

class Statistic(db.Model):

    __tablename__ = "statistics"

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=manager_id)
    section = db.Column(db.Integer)
    output = db.Column(db.Text)

class GroupedStudents(db.Model):

    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=manager_id)
    studentID = db.Column(db.String(32))
    section = db.Column(db.Integer)
    group = db.Column(db.Integer)

##############
# LOGIN CODE #
##############
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#########################
# LANDING PAGE: UPLOAD #
########################

@app.route("/", methods=["GET", "POST"])
def index():
    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None):
        return render_template("main_page.html",
                        student_csv=None, csv_present = False)

    # Display page using the csv info uploaded
    if request.method == "GET":

        students = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)

        students = students.pivot(index='studentID',
        columns='key', values='value')

        return render_template("main_page.html",
                student_csv=students.to_html(), csv_present = True)


    # Post request: Upload file into database
    try:
        upload_csv()
    except:
        try:
            upload_csv(delimiter =";")
        except Exception as e:
            log.debug(str(e))
    return redirect(url_for('index'))

#######################
# PARAMETER PAGE     #
######################

@app.route("/parameters/", methods=["GET", "POST"])
def parameters():
    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None):
        return render_template("parameters.html", specifications=None,
                                headers = None, status = None)

    # Display page with the latest status of groupeng and the specifications
    if request.method == "GET":
        statuss = []
        for t in Statistic.query.filter_by(manager=current_user).all():
            statuss.append(t.output.replace('<','[').\
                replace('>',']').replace('\n', '<br />'))

        properties = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)

        # ignore id column
        cols = properties.key.unique()

        return render_template("parameters.html", specifications=Specification\
                            .query.filter_by(manager=current_user).all(),
                            headers = cols, statuss = statuss)


    return redirect(url_for('parameters'))

#background process happening on the parameter page for button clicks
@app.route('/background_process_test/', methods=['GET', 'POST'])
def background_process_test():
    data = json.loads(request.data)
    if data['button'] == 'process':
        run_groupeng()

    if data['button'] == 'reset':
        reset_defaults()

    return redirect(url_for('parameters'))

#change parameters when they are changed on the site
@app.route('/parameter_update/', methods=['GET', 'POST'])
def parameter_update():

    data = json.loads(request.data)
    value = str(data['value'])
    header = str(data['header'])
    try:
        priority = Specification.query.filter_by(header=header)\
                .filter_by(manager=current_user).first().priority
    except:
        priority = 5

    if value == 'group_size':
        if (header[-1] in ['+','-']) and (header[:-1].isdigit()):
            Specification.query.filter_by(value='group_size')\
                .filter_by(manager=current_user)\
                .update(dict(header = str(int(header[:-1])) + header[-1]))

    elif value == 'n_sections':
        if (header.isdigit()):
            Specification.query.filter_by(value='n_sections')\
                .filter_by(manager=current_user)\
                .update(dict(header = str(int(header))))

    else:
        Specification.query.filter_by(header=header)\
            .filter_by(manager=current_user).delete()
        if value != 'none':
            # Post request: read specification
            specification = Specification(manager = current_user,
                                    header=header,
                                    value=value,
                                    priority = priority)
            db.session.add(specification)
    db.session.commit()

    return redirect(url_for('parameters'))

#change priority of parameters when they are changed on the site
@app.route('/priority_update/', methods=['GET', 'POST'])
def priority_update():
    try:
        data = json.loads(request.data)
        header = str(data['header'])
        priority = str(int(data['priority']))

        Specification.query.filter_by(header=header)\
                .filter_by(manager=current_user).update(dict(priority=priority))
        db.session.commit()
    except:
        pass
    return redirect(url_for('parameters'))

#############################
# MODIFY STUDENT/GROUP PAGE #
#############################

@app.route("/modify/", methods=['GET', 'POST'])
def modify():
    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None) or\
      (db.session.query(GroupedStudents).filter(\
        GroupedStudents.manager == current_user).first() is None):
        return render_template("modify.html", groups = None, message = None)

    # Post request to switch 2 students or groups
    if request.method == "POST":
        message = switch_ids(request.form["from"], request.form["to"])

    student_query = GroupedStudents.query\
                    .filter_by(manager = current_user).all()
    all_students = []
    for sq in student_query:
        all_students.append([sq.studentID,int(sq.group),int(sq.section)])

    res = OrderedDict()
    for i, g, s in all_students:
        k = str(s) + ":" + str(g)
        if k in res: res[k].append(i)
        else: res[k] = [i]

    [{'group':k, 'studentID':v} for k,v in res.items()]

    res = OrderedDict(sorted(res.items()))

    # Display page with table containing grouping info
    if request.method == "GET":
        message = None

    return render_template("modify.html", groups = res, message = message)

#########################
# DISPLAY GROUPS PAGE   #
#########################

@app.route("/groups/", methods=['GET', 'POST'])
def groups():

    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None):
        return render_template("groups.html",by_section = False,
                            tables = None)

    # Show summary tables
    if request.method == "GET":
        by_section = False
    else:
        by_section = len(request.form.getlist('slider'))>0

    return render_template("groups.html", by_section = by_section,
                            tables = create_tables(by_section),
                            manager_id = current_user.id)

#########################
# GROUP/SECTION SUMMARY #
#########################

@app.route("/summary/", methods=['GET', 'POST'])
def summary():
    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None):
        return render_template("summary.html", by_section = False,
                            tables = None)

    # Show summary tables
    if request.method == "GET":
        by_section = False
    else:

        by_section = len(request.form.getlist('slider'))>0

    return render_template("summary.html", by_section = by_section,
                            tables = create_tables(by_section,summary=True),
                            manager_id = current_user.id)

    #return redirect(url_for('summary'))


#########################
# VISUALIZE GROUPS PAGE #
#########################

@app.route("/visualize/", methods=['GET', 'POST'])
def visualize():
    # Empty parameters if no data available or user not logged in
    if not current_user.is_authenticated or\
      (request.method == "GET" and db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is None) or\
      (db.session.query(GroupedStudents).filter(\
        GroupedStudents.manager == current_user).first() is None):
        return render_template("visualize.html",headers = None)

    properties = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)
    cols = properties.key.unique()
    # Display visualization page using csv headers as possible inputs
    if request.method == "GET":
        return render_template("visualize.html", headers = cols, exists = False,
                                manager_id = current_user.id, selected = None)

    selected = visualize_user_plot()

    return render_template("visualize.html", headers = cols, exists = True,
                            manager_id = current_user.id, selected = selected)

####################
# DOWNLOAD BUTTON #
###################

@app.route("/download/")
def download():
    groups = pd.read_sql(
        db.session.query(GroupedStudents)\
                .filter(GroupedStudents.manager == current_user).statement,
                db.session.bind)

    filename = "%s.csv" % ('groups' + \
          datetime.now(pytz.timezone('CET')).strftime("%Y-%b-%d (%H:%M:%S.%f)"))

    resp = make_response(
            groups[['studentID','group','section']].to_csv(index = False))
    resp.headers["Content-Disposition"] = ("attachment; filename=%s" % filename)
    resp.headers["Content-Type"] = "text/csv"
    return resp

###########
# METHODS #
###########

# Extract unique values from list while maintaining the order
def unique_maintain_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def upload_csv(delimiter = ","):

    file= request.files["students"]
    file.seek(0)
    reader = csv.reader(file, delimiter = delimiter)

    header_line = reader.next()

    headers = [h.strip() for h in header_line if h.strip() != '']
    headers.pop(0)

    if len(headers)<2:
        raise ValueError('Wrong csv format. Trying with different delimiter.')

    if db.session.query(Classroom.id).\
      filter(Classroom.manager == current_user).first() is not None:
        log.debug('delete old csv')
        Classroom.query.filter_by(manager=current_user).delete()

    students = []
    for line,s in enumerate(reader):
        if set(s).issubset(set(['', ' ', None])):
            # skip blank lines
            pass
        else:
           # d = {}
            studentID = s[0]
            for i, h  in enumerate(headers):
                students.append( Classroom(
                    studentID = studentID,
                    key = h,
                    value = s[i+1],
                    manager = current_user
                    ))
    log.debug('upload new csv')
    db.session.add_all(students)
    db.session.commit()

    #Delete old specifications etc.
    Statistic.query.filter_by(manager=current_user).delete()
    GroupedStudents.query.filter_by(manager=current_user).delete()
    reset_defaults()

def run_groupeng():
    Statistic.query.filter_by(manager=current_user).delete()
    GroupedStudents.query.filter_by(manager=current_user).delete()

    stats,student_dic = process_csv(current_user)

    for sec, stat in enumerate(stats):
        statistic = Statistic(manager = current_user,
                                section = sec,
                                output=stat)
        db.session.add(statistic)
        db.session.commit()


    # Map sections in groupeng to actual sections based on preferences
    sec_map = {}
    pref_query = Specification.query.filter_by(manager=current_user)\
                        .filter_by(value='section_preference').first()
    if pref_query is None:
        for sec, groups in student_dic.iteritems():
            sec_map[sec] = sec +1
    else:

        students = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)

        students = students.pivot(index='studentID',
                                    columns='key', values='value')

        pref_col = pref_query.header
        identifier = 'studentID'

        #check if we need to convert preference to integer
        if not pd.to_numeric(
                        students[pref_col], errors='coerce').notnull().all():

            students.loc[:,pref_col] = [ord(sec_letter.lower()) - 96 for \
                            sec_letter in students[pref_col].values.tolist()]

        fr = {}

        for sec, groups in student_dic.iteritems():
            preferences = []
            #loop through students and add their preference
            for stud in groups:
                preferences.append(int(students[students[identifier] == \
                                        str(stud)][pref_col].values[0]))
            fr[sec] = {x:preferences.count(x) for x in preferences}

        #Make sure all section have mapping
        for new_sec in range(len(student_dic)):
            # per section, get amount of preferences for sec
            f = [fr[x][new_sec+1] if (new_sec+1) in fr[x] else 0  for x in fr]
            order = [i[0] for i in \
                        sorted(enumerate(f), key=lambda x:x[1],reverse=True)]

            for o in order:
                if not (o in sec_map):
                    sec_map[o] = new_sec+1
                    break

    for sec, groups in student_dic.iteritems():
        for key, value in groups.iteritems():
            new = GroupedStudents(manager = current_user,
                                section=sec_map[sec],
                                studentID=key,
                                group = value)
            db.session.add(new)
            db.session.commit()


def reset_defaults():
    Specification.query.filter_by(manager=current_user).delete()
    db.session.commit()
    db.session.add(Specification(manager = current_user,
                        header='6+',
                        value='group_size'))
    db.session.commit()
    db.session.add(Specification(manager = current_user,
                        header='2',
                        value='n_sections'))
    db.session.commit()

    properties = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind).key.unique()

    search_distribute = ["gender","nationality","academicbackground", "programme","past group"]
    search_balance = ["gmat","age"]

    count = 1
    for p in properties:
        for d in search_distribute:
            if SequenceMatcher(None, p.lower(), d.lower()).ratio() >0.75:
                db.session.add(Specification(manager = current_user,
                        header=p,
                        value='distribute',
                        priority=str(count)))
                db.session.commit()
                count = count + 1
                continue
        for b in search_balance:
            if SequenceMatcher(None, p.lower(), b.lower()).ratio() >0.75:
                db.session.add(Specification(manager = current_user,
                        header=p,
                        value='balance',
                        priority='30'))
                db.session.commit()
                count = count + 1
                continue
    if count == 0:
        db.session.add(Specification(manager = current_user,
                        header=properties[0],
                        value='distribute',
                        priority='5'))
        db.session.commit()

def switch_ids(from_id, to_id):

     # Identify group with split
    if len(from_id.split(":"))>1:
        from_section   = from_id.split(":")[0]
        from_group = from_id.split(":")[1]
        to_section    = to_id.split(":")[0]
        to_group   = to_id.split(":")[1]
        froms = GroupedStudents.query.filter_by(manager = current_user). \
           filter_by(group = from_group).filter_by(section = from_section).all()
        tos = GroupedStudents.query.filter_by(manager = current_user).\
           filter_by(group = to_group).filter_by(section = to_section).all()
        if (len(froms) == 0) or (len(tos) == 0):
            return "Invalid input"
        for f in froms:
            f.group = to_group
            f.section = to_section
            db.session.commit()

        for t in tos:
            t.group = from_group
            t.section = from_section
            db.session.commit()
        message = "Switched group " + str(from_id) + " and " + str(to_id)
    else:

        from_student = GroupedStudents.query.filter_by(manager = current_user).\
           filter_by(studentID = from_id).first()
        to_student = GroupedStudents.query.filter_by(manager = current_user).\
           filter_by(studentID = to_id).first()
        if (from_student is None) or (to_student is None):
            return "Invalid input"
        from_student.studentID = to_id
        db.session.commit()
        to_student.studentID = from_id
        db.session.commit()
        message = "Switched student " + str(from_id) + " and " + str(to_id)


    return message

def create_tables(by_section = False, summary = False):
    students = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)

    students = students.pivot(index='studentID', columns='key', values='value')

    groups = pd.read_sql(
            db.session.query(GroupedStudents).\
            filter(GroupedStudents.manager == current_user).statement,
            db.session.bind)
    if len(groups)<1:
        return None
    students = students.merge(groups, on='studentID')

    sectionCol = students.columns[-2]
    groupCol = students.columns[-1]

    students['sec:group'] = students[sectionCol].astype(str) + \
                                ":" + students[groupCol].astype(str)

    spec = pd.read_sql(
            db.session.query(Specification).\
            filter(Specification.manager == current_user).\
            filter(Specification.value.in_(
                    ("cluster","aggregate","distribute","balance"))).statement,
                    db.session.bind)

    columns = list(spec.header.unique())
    tables = []
    group_by = sectionCol if by_section else 'sec:group'
    if summary:
        stylestr = "table, td, tr, th{text-align: center;border-color: black;"+\
                    "border-width:thin;border-style:solid; border-width: 2px;"+\
                    "padding: 5px; border-collapse:collapse}"
        for c in columns:
            table = students.loc[:,[group_by,c]].copy()
            if (spec[spec.header == c].value.iloc[0] == 'balance'):
                table[c] = pd.to_numeric(table[c], errors='coerce')

                grouped = pd.pivot_table(table,index=[group_by], values = [c],
                   aggfunc=[np.mean,np.std], margins=True,
                           dropna=True, fill_value=0).round(0)
                grouped.columns = grouped.columns.droplevel(0)
                grouped.columns.name = None
                grouped = grouped.reset_index()
                grouped.columns = [c, "mean", "std"]

                html = grouped.style.background_gradient(axis = 0,cmap='Blues')\
                                    .hide_index().render()


            else:
                grouped = pd.pivot_table(table,index=[c],
                   columns=[group_by],
                   aggfunc=len, margins=True,
                           dropna=True, fill_value=0)
                grouped = grouped.div( grouped.iloc[-1,:], axis=1 ).round(2)*100
                grouped.drop(grouped.tail(1).index,inplace=True)
                grouped = grouped.reset_index().rename_axis(None, axis=1)\
                                .set_index(c).transpose()

                html = grouped.style.background_gradient(
                    axis = 0,cmap='Blues').render()
                html = html.replace("</td>","%</td>")

            html = html[0:27] + stylestr + html[27:len(html)]
            tables.append(("",html))

    else:
        loop = sorted(students[group_by].unique())
        for gr in loop:

            table = students.loc[students[group_by]==gr,["studentID"]+columns]

            if by_section:
                description = "Section: " + str(gr)
            else:
                description = "Section: {0} | Group: {1}".\
                            format(gr.split(":")[0],gr.split(":")[1])


            tables.append((description,table.to_html(index=False)))

    return tables

def visualize_user_plot():

    selected = request.form["header"]
    students = pd.read_sql(
            db.session.query(Classroom).\
            filter(Classroom.manager == current_user).statement,
            db.session.bind)

    students = students.pivot(index='studentID', columns='key', values='value')
    # Post request to visualize a column
    groups = pd.read_sql(
        db.session.query(GroupedStudents).filter(
            GroupedStudents.manager == current_user).statement, db.session.bind)

    identifier = 'studentID'

    groups['studentID'] = groups['studentID'].apply(str)
    students = students.merge(groups,
                            left_on = identifier, right_on = "studentID")

    flag = False
    spec = Specification.query.filter_by(manager = current_user)\
                        .filter_by(header = selected).first()
    if spec is not None:
        flag = spec.value == 'balance'

    if  flag:
        kind = 'hist'
        students[selected] = pd.to_numeric(students[selected])
        groupplot = students[[selected,'group','section']].\
                                    groupby(['group','section']).mean()
        sectionplot = students[[selected,'section']].\
                                    groupby('section').mean()

    else:
        kind = 'bar'
        groupplot = students[[selected,'group','section']].\
                      pivot_table(index=['group','section'],
                      columns=selected, aggfunc=len, fill_value=0)
        sectionplot = students[[selected,'section']].\
                      pivot_table(index='section',
                      columns=selected, aggfunc=len, fill_value=0)

    fig = groupplot.plot(kind=kind).get_figure()
    fig.savefig('../static/images/group_plot'+ str(current_user.id) + '.png')
    fig = sectionplot.plot(kind=kind).get_figure()
    fig.savefig('../static/images/section_plot'+ str(current_user.id) + '.png')
    return selected
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = \
     'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

