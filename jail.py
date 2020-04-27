import subprocess
from .zfs import *
import random
import shutil
import json
from tabulate import tabulate
import os
import jailconf
import shlex
from .mount import getmntinfo


def gen_env_command(command, env):
    env = [ 'export ' + k + '=' + shlex.quote(v) \
        for (k, v) in env.items() ]
    command = ' && '.join(env + [ command ])
    return command


def jail_create(path, command, env, mounts, hostname=None):
    name = os.path.split(path)[-1]
    if os.path.exists('/etc/jail.conf'):
        conf = jailconf.load('/etc/jail.conf')
    else:
        conf = jailconf.JailConf()
    conf[name] = blk = jailconf.JailBlock()
    blk['path'] = path
    if command:
        command = gen_env_command(command, env)
        blk['exec.start'] = command
    prestart = [ 'cp /etc/resolv.conf ' +
        shlex.quote(os.path.join(path, 'etc/resolv.conf')) ]
    poststop = []
    if mounts:
        for (from_, on) in mounts:
            if not from_.startswith('/'):
                from_, _ = zfs_find(from_, focker_type='volume')
                from_ = zfs_mountpoint(from_)
            prestart.append('mount -t nullfs ' + shlex.quote(from_) +
                ' ' + shlex.quote(os.path.join(path, on.strip('/'))))
        poststop += [ 'umount -f ' +
            os.path.join(path, on.strip('/')) \
            for (_, on) in reversed(mounts) ]
    if prestart:
        blk['exec.prestart'] = shlex.quote(' && '.join(prestart))
    if poststop:
        blk['exec.poststop'] = shlex.quote(' && '.join(poststop))
    blk['persist'] = True
    blk['interface'] = 'lo1'
    blk['ip4.addr'] = '127.0.1.0'
    blk['mount.devfs'] = True
    blk['exec.clean'] = True
    blk['host.hostname'] = hostname or name
    conf.write('/etc/jail.conf')


def jail_run_v2(path, command, env, mounts):
    name = os.path.split(path)[-1]
    command = gen_env_command(command, env)
    jail_create(path, None, None, mounts)
    subprocess.check_output([ 'jail', '-c', name ])
    subprocess.run([ 'jexec', name, '/bin/sh', '-c', command ])
    subprocess.check_output([ 'jail', '-r', name ])


def get_jid(path):
    data = json.loads(subprocess.check_output(['jls', '--libxo=json']))
    lst = data['jail-information']['jail']
    lst = list(filter(lambda a: a['path'] == path, lst))
    if len(lst) == 0:
        raise ValueError('JID not found for path: ' + path)
    if len(lst) > 1:
        raise ValueError('Ambiguous JID for path: ' + path)
    return str(lst[0]['jid'])


def do_mounts(path, mounts):
    print('mounts:', mounts)
    for (source, target) in mounts:
        if source.startswith('/'):
            name = source
        else:
            name, _ = zfs_find(source, focker_type='volume')
            name = zfs_mountpoint(name)
        while target.startswith('/'):
            target = target[1:]
        subprocess.check_output(['mount', '-t', 'nullfs', name, os.path.join(path, target)])


def undo_mounts(path, mounts):
    for (_, target) in reversed(mounts):
        while target.startswith('/'):
            target = target[1:]
        subprocess.check_output(['umount', '-f', os.path.join(path, target)])


def jail_run(path, command, mounts=[]):
    command = ['jail', '-c', 'host.hostname=' + os.path.split(path)[1], 'persist=1', 'mount.devfs=1', 'interface=lo1', 'ip4.addr=127.0.1.0', 'path=' + path, 'command', '/bin/sh', '-c', command]
    print('Running:', ' '.join(command))
    try:
        do_mounts(path, mounts)
        shutil.copyfile('/etc/resolv.conf', os.path.join(path, 'etc/resolv.conf'))
        res = subprocess.run(command)
    finally:
        try:
            subprocess.run(['jail', '-r', get_jid(path)])
        except ValueError:
            pass
        subprocess.run(['umount', '-f', os.path.join(path, 'dev')])
        undo_mounts(path, mounts)
    if res.returncode != 0:
        # subprocess.run(['umount', os.path.join(path, 'dev')])
        raise RuntimeError('Command failed')


def jail_stop(path):
    try:
        jid = get_jid(path)
        subprocess.run(['jail', '-r', jid])
    except ValueError:
        print('JID could not be determined')
    mi = getmntinfo()
    for m in mi:
        mntonname = m['f_mntonname'].decode('utf-8')
        if mntonname.startswith(path + os.path.sep):
            print('Unmounting:', mntonname)
            subprocess.run(['umount', '-f', mntonname])


def jail_remove(path):
    print('Removing jail:', path)
    jail_stop(path)
    subprocess.run(['zfs', 'destroy', '-r', '-f', zfs_name(path)])
    if os.path.exists('/etc/jail.conf'):
        conf = jailconf.load('/etc/jail.conf')
        name = os.path.split(path)[-1]
        if name in conf:
            del conf[name]
            conf.write('/etc/jail.conf')


def command_jail_create(args):
    image, _ = zfs_find(args.image, focker_type='image', zfs_type='snapshot')
    sha256 = bytes([ random.randint(0, 255) for _ in range(32) ]).hex()
    lst = zfs_list(fields=['focker:sha256'], focker_type='image')
    lst = list(filter(lambda a: a[0] == sha256, lst))
    if lst:
        raise ValueError('Whew, a collision...')
    poolname = zfs_poolname()
    for pre in range(7, 32):
        name = poolname + '/focker/jails/' + sha256[:pre]
        if not zfs_exists(name):
            break
    zfs_run(['zfs', 'clone', '-o', 'focker:sha256=' + sha256, image, name])
    if args.tags:
        zfs_tag(name, args.tags)
    path = zfs_mountpoint(name)
    jail_create(path, args.command,
        { a.split(':')[0]: ':'.join(a.split(':')[1:]) \
            for a in args.env },
        [ [a.split(':')[0], ':'.join(a.split(':')[1:])] \
            for a in args.mounts ],
        args.hostname )
    print(sha256)
    print(path)


def command_jail_run(args):
    base, _ = zfs_snapshot_by_tag_or_sha256(args.image)
    # root = '/'.join(base.split('/')[:-1])
    for _ in range(10**6):
        sha256 = bytes([ random.randint(0, 255) for _ in range(32) ]).hex()
        name = sha256[:7]
        name = base.split('/')[0] + '/focker/jails/' + name
        if not zfs_exists(name):
            break
    zfs_run(['zfs', 'clone', '-o', 'focker:sha256=' + sha256, base, name])
    try:
        mounts = list(map(lambda a: a.split(':'), args.mounts))
        jail_run(zfs_mountpoint(name), args.command, mounts)
        # subprocess.check_output(['jail', '-c', 'interface=lo1', 'ip4.addr=127.0.1.0', 'path=' + zfs_mountpoint(name), 'command', command])
    finally:
        # subprocess.run(['umount', zfs_mountpoint(name) + '/dev'])
        zfs_run(['zfs', 'destroy', '-f', name])
        # raise

def command_jail_list(args):
    lst = zfs_list(fields=['focker:sha256,focker:tags,mountpoint'], focker_type='jail')
    jails = subprocess.check_output(['jls', '--libxo=json'])
    jails = json.loads(jails)['jail-information']['jail']
    jails = { j['path']: j for j in jails }
    lst = list(map(lambda a: [ a[1],
        a[0] if args.full_sha256 else a[0][:7],
        a[2],
        jails[a[2]]['jid'] if a[2] in jails else '-' ], lst))
    print(tabulate(lst, headers=['Tags', 'SHA256', 'mountpoint', 'JID']))


def command_jail_tag(args):
    name, _ = zfs_find(args.reference, focker_type='jail')
    zfs_untag(args.tags, focker_type='jail')
    zfs_tag(name, args.tags)


def command_jail_untag(args):
    zfs_untag(args.tags, focker_type='jail')


def command_jail_prune(args):
    jails = subprocess.check_output(['jls', '--libxo=json'])
    jails = json.loads(jails)['jail-information']['jail']
    used = set()
    for j in jails:
        used.add(j['path'])
    lst = zfs_list(fields=['focker:sha256,focker:tags,mountpoint,name'], focker_type='jail')
    for j in lst:
        if j[1] == '-' and (j[2] not in used or args.force):
            jail_remove(j[2])
