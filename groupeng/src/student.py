# Copyright 2011, Thomas G. Dimiduk
#
# This file is part of GroupEng.
#
# GroupEng is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GroupEng is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with GroupEng.  If not, see <http://www.gnu.org/licenses/>.

"""
Student record.  Creating Student record from a csv (excel) file.

.. moduleauthor:: Thomas G. Dimiduk tgd8@cornell.edu
"""
from .utility import numberize

import os,sys,inspect
import pandas as pd
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0,parentdir)
import flask_app
from flask_migrate import Migrate
group_number = 'Group Number'

import logging
log = logging.getLogger('log')

class Student(object):
    """
    """

    def __init__(self, data = {}, headers = [], identifier=None):
        """

        Arguments:
        :param attributes:
        :type attributes:

        """
        self.identifier = identifier
        if identifier == None:
            # if they don't give us an identifier, just use the first column
            self.identifier = headers[0]

        self.data = data
        for key, val in self.data.items():
            if val in ['', '0']:
                self.data[key] = None
            else:
                self.data[key] = numberize(val)

        self.group = None
        self.headers = list(headers)
        if group_number not in self.headers:
            self.headers.append(group_number)

    @property
    def group_number(self):
        return self.group.group_number

    def __getitem__(self, x):
        if x == group_number:
            return self.group.group_number
        else:
            return self.data[x]
    def __str__(self):
        return "<Student : {0}>".format(self.data)

    def __repr__(self):
        return "Student(data={0}, headers={1}, identifier={2})".format(
            self.data, self.headers, self.identifier)

    def full_record(self):
        return [str(self[h]) for h in self.headers]

def attribute_match(attribute, value):
    if isinstance(value, (list, tuple)):
        return lambda x: x[attribute] in value
    else:
        return lambda x: x[attribute] == value

def attribute_differs(attribute, value):
    return lambda x: x[attribute] != value


def load_classlist(current_user, identifier, studentIds):

    classroom = pd.read_sql(
            flask_app.db.session.query(flask_app.Classroom).\
            filter(flask_app.Classroom.manager == current_user).statement,
            flask_app.db.session.bind)

    headers = classroom.key.unique()
    headers = np.append(headers, 'studentID')
    classroom = classroom.pivot(index='studentID', columns='key', values='value')

    students = []

    for index, row in classroom.iterrows():
        d = row.to_dict()
        d['studentID'] = index

        if (studentIds is None) or (index in studentIds):

            students.append(Student(d, list(headers), identifier))

    return students
