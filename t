#!/usr/bin/env python3.9

#
# Copyright (C) Stanislaw Adaszewski, 2018
# https://adared.ch
#

from argparse import ArgumentParser
import json
import time
import datetime
import os

def _readableDate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

class Task(object):
    PENDING = 1
    FINISHED = 2
    CANCELLED = 3
    REMOVED = 4

    def __init__(self, id, desc, status,
        cdate=None, mdate=None, fdate=None):
        self.id = id
        self.description = desc
        self.status = status
        self.dateCreated = cdate
        self.dateModified = mdate
        self.dateFinished = fdate

class Database(object):
    def __init__(self, fname):
        self._fname = fname
        self._tasks = {}
        self._nextTaskId = 1
        self._replay_log()

    def _replay_log(self):
        fname = self._fname
        if not os.path.exists(fname):
            return # new database

        with open(fname, 'r') as f:
            log = list(map(json.loads, [x for x in f.read().split('\n') if x != '']))

        for action in log:
            # print 'action: ', action
            self._play_action(action)

    def _play_action(self, action):
        handlers = { 'ADD': self._play_add_task,
            'FINISH': self._play_finish_task,
            'EDIT': self._play_edit_task,
            'CANCEL': self._play_cancel_task,
            'RESTORE': self._play_restore_task,
            'REMOVE': self._play_remove_task }
        handlers[action['type']](action)

    def _play_add_task(self, action):
        id = self._nextTaskId
        if action['taskId'] != id:
            raise ValueError('Incoherence in task IDs')
        self._nextTaskId += 1
        self._tasks[id] = Task(id, action['description'],
            Task.PENDING, action['timestamp'], action['timestamp'])

    def _play_finish_task(self, action):
        id = action['taskId']
        task = self._tasks[id]
        if task.status == Task.FINISHED:
            raise ValueError('Requested task is already finished')
        task.status = Task.FINISHED
        task.dateFinished = action['timestamp']

    def _play_edit_task(self, action):
        id = action['taskId']
        task = self._tasks[id]
        task.dateModified = action['timestamp']
        task.description = action['description']

    def _play_cancel_task(self, action):
        id = action['taskId']
        task = self._tasks[id]
        if task.status != Task.PENDING:
            raise ValueError('Requested task is not in pending state')
        task.dateModified = action['timestamp']
        task.status = Task.CANCELLED

    def _play_restore_task(self, action):
        id = action['taskId']
        task = self._tasks[id]
        if task.status != Task.CANCELLED:
            raise ValueError('Requested task is not in cancelled state')
        task.dateModified = action['timestamp']
        task.status = Task.PENDING

    def _play_remove_task(self, action):
        id = action['taskId']
        task = self._tasks[id]
        if task.status == Task.REMOVED:
            raise KeyError(id) # 'Requested task is already removed')
        task.dateModified = action['timestamp']
        task.status = Task.REMOVED
        del self._tasks[id]

    def _play_and_log_action(self, action):
        self._play_action(action)
        with open(self._fname, 'a') as f:
            f.write(json.dumps(action) + '\n')

    def add_task(self, description):
        action = {
            'type': 'ADD',
            'timestamp': _readableDate(time.time()),
            'description': description,
            'taskId': self._nextTaskId
        }
        self._play_and_log_action(action)
        print('\033[0;31mTask added: %d. %s\033[0;0m' % (action['taskId'],
            action['description']))

    def finish_task(self, taskId):
        action = {
            'type': 'FINISH',
            'timestamp': _readableDate(time.time()),
            'taskId': taskId
        }
        self._play_and_log_action(action)
        desc = self.task_description(taskId)
        print('\033[0;32mTask finished: %d. %s\033[0;0m' % (taskId, desc))

    def edit_task(self, taskId, newDescription):
        action = {
            'type': 'EDIT',
            'timestamp': _readableDate(time.time()),
            'taskId': taskId,
            'description': newDescription
        }
        self._play_and_log_action(action)

    def cancel_task(self, taskId):
        action = {
            'type': 'CANCEL',
            'timestamp': _readableDate(time.time()),
            'taskId': taskId
        }
        self._play_and_log_action(action)
        desc = self.task_description(taskId)
        print('\033[0;35mTask cancelled: %d. %s\033[0;0m' % (taskId, desc))

    def restore_task(self, taskId):
        action = {
            'type': 'RESTORE',
            'timestamp': _readableDate(time.time()),
            'taskId': taskId
        }
        self._play_and_log_action(action)
        desc = self.task_description(taskId)
        print('\033[0;31mTask restored: %d. %s\033[0;0m' % (taskId, desc))

    def remove_task(self, taskId):
        action = {
            'type': 'REMOVE',
            'timestamp': _readableDate(time.time()),
            'taskId': taskId
        }
        self._play_and_log_action(action)
        desc = self.task_description(taskId)
        print('Task removed: %d. %s' % (taskId, desc))

    def task_description(self, taskId):
        tasks = self._tasks
        task = tasks[taskId]
        return task.description

    def task_status(self, taskId):
        task = self._tasks[taskId]
        return task.status

    def finished_tasks(self):
        return list([t for t in list(self._tasks.values()) if t.status == Task.FINISHED])

    def pending_tasks(self):
        return list([t for t in list(self._tasks.values()) if t.status == Task.PENDING])

    def cancelled_tasks(self):
        return list([t for t in list(self._tasks.values()) if t.status == Task.CANCELLED])

    def get_task(self, taskId):
        task = self._tasks[taskId]
        return task

    def print_task(self, task):
        if task.status == Task.PENDING:
            color = '\033[0;31m'
            meaningfulDate = task.dateCreated
        elif task.status == Task.FINISHED:
            color = '\033[0;32m'
            meaningfulDate = task.dateFinished
        elif task.status == Task.CANCELLED:
            color = '\033[0;35m'
            meaningfulDate = task.dateModified
        print('%s%s\t%d.\t%s%s' % (color, meaningfulDate[:10], task.id,
            task.description, '\033[0;0m'))


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('description', type=str, nargs='*',
        help='Add task with this description')
    parser.add_argument('--database-filename', '-db', type=str, default='tasks')
    parser.add_argument('-a', '--add', type=str,
        help='Task description')
    parser.add_argument('-f', '--finish', type=int,
        help='Mark task as finished')
    parser.add_argument('-e', '--edit', type=int,
        help='Edit task description')
    parser.add_argument('-d', '--done', action='store_true',
        help='Show finished tasks')
    parser.add_argument('-c', '--cancel', type=int,
        help='Cancel a task')
    parser.add_argument('-r', '--restore', type=int,
        help='Restore a cancelled task')
    parser.add_argument('-p', '--postponed', action='store_true',
        help='Show cancelled/postponed tasks')
    parser.add_argument('-x', '--remove', type=int,
        help='Remove task from all lists')
    parser.add_argument('-A', '--all', action='store_true',
        help='Display all tasks')
    return parser


def _main():
    parser = create_parser()
    args = parser.parse_args()
    db = Database(args.database_filename)
    if args.add is not None:
        db.add_task(args.add)
    elif args.finish is not None:
        db.finish_task(args.finish)
    elif args.cancel is not None:
        db.cancel_task(args.cancel)
    elif args.restore is not None:
        db.restore_task(args.restore)
    elif args.remove is not None:
        db.remove_task(args.remove)
    elif args.edit is not None:
        taskId = args.edit
        oldDescription = db.task_description(taskId)
        print('Current description:', oldDescription)
        newDescription = input('New description: ') or oldDescription
        if newDescription != oldDescription:
            db.edit_task(taskId, newDescription)
    elif len(args.description) > 0:
        db.add_task(' '.join(args.description))
    else:
        if args.all: lst = list(db._tasks.values())
        elif args.postponed: lst = db.cancelled_tasks()
        elif args.done: lst = db.finished_tasks()
        else: lst = db.pending_tasks()
        for task in lst:
            db.print_task(task)

def main():
    try:
        _main()
    except KeyboardInterrupt:
        print('Cancelled')
    except KeyError as e:
        print('Unknown task ID:', e)
    except Exception as e:
        print('%s: %s' % (e.__class__.__name__, e.message))



if __name__ == '__main__':
    main()
