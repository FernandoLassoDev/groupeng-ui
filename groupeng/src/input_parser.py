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

import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0,parentdir)
import flask_app

import logging
log = logging.getLogger('log')

def read_input(current_user, studentIds):

    dek = {}
    rules = []
    general = flask_app.Specification.query.filter_by(manager=current_user)

    dek['student_identifier'] = 'studentID'
    if studentIds is None:
        dek['number_of_groups'] = int(general.filter_by(value='n_sections').first().header)
    else:
        dek['group_size'] = general.filter_by(value='group_size').first().header

    header_specs = flask_app.Specification.query.filter_by(manager=current_user).\
            filter(flask_app.Specification.value !='group_size').\
            filter(flask_app.Specification.value !='n_sections').\
            order_by(flask_app.Specification.priority).all()

    rules = []
    for h in header_specs:
        log.debug(h.header)
        if h.value == 'section_preference':
            if studentIds is None:
                rule = {}
                rule['name'] = 'aggregate'
                rule['attribute'] = h.header
                rules.append(rule)

        else:

            #In section assignments, everything is distributed
            if studentIds is None and h.value != 'balance':
                val = 'distribute'
            else:
                val = h.value


            rule = {}
            rule['name'] = val
            rule['attribute'] = h.header
            rules.append(rule)

    dek['rules'] = rules

    return dek
