
import os.path
import os
os.chdir('/home/EsadeAssignment/mysite/groupeng')
from src import controller
import logging

log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('GroupEng.log', mode='w')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)

def process_csv(current_user):

    log.debug('run controller')

    log.debug('allocate sections')
    status, stat, sections = controller.run(current_user, None)

    stats = []
    students = {}
    res = {}

    for stud in sections:
        log.debug(stud)
        sec = sections[stud]
        if sec in res: res[sec].append(str(stud))
        else: res[sec] = [str(stud)]

    [{'section':sec, 'studentID':stud} for stud,sec in res.items()]

    log.debug('allocate groups')

    for count,sec in enumerate(res):
         status_sec, stats_sec, students_sec = controller.run(current_user, res[sec])
         status = status and status_sec
         stats = stats + [stats_sec]
         students[count] = students_sec

    log.debug('ran groupeng')

    if status:
        log.debug("GroupEng Run Succesful\n")
    else:
        log.debug("GroupEng Ran Correctly but not all rules could be met\n")

    return stats,students




