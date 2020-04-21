from argparse import ArgumentParser
import yaml
import os
from weir import zfs, process


def clone(self, name, props={}, force=False):
    url = zfs._urlsplit(self.name)
    url_1 = zfs._urlsplit(name)
    if url.netloc != url_1.netloc:
        raise ValueError('Clone has to happen on the same host')
    cmd = ['zfs', 'clone']
    for prop, value in props.items():
        cmd.append('-o')
        cmd.append(prop + '=' + str(value))
    cmd.append(url.path)
    cmd.append(url_1.path)
    process.check_call(cmd, netloc=url.netloc)

zfs.ZFSSnapshot.clone = clone


def process_step(step, name):
    cmd=['jail', '-c']
    cmd.append('path=' + '/focker/' + name)


def process_steps(steps, name):
    if isinstance(steps, list):
        for step in steps:
            process_step(step, name)
    else:
        process_step(steps, name)


def build(args):
    fname = os.path.join(args.focker_dir, 'Fockerfile.yml')
    print('fname:', fname)
    if not os.path.exists(fname):
        raise ValueError('No Fockerfile.yml could be found in the specified directory')
    with open(fname, 'r') as f:
        spec = yaml.safe_load(f)
    print('spec:', spec)
    if 'from' not in spec:
        raise ValueError('Missing base specification')
    from_ = zfs.findprops('/', props=['focker:tags'])
    from_ = filter(lambda a: a['value'] == spec['from'] \
        and '@' in a['name'], from_)
    from_ = list(from_)
    if len(from_) == 0:
        raise ValueError('Requested base not found')
    if len(from_) > 1:
        raise ValueError('Ambiguous base specification')
    base = from_[0]['name']
    root = '/'.join(base.split('/')[:-1])
    print('base:', base)
    print('root:', root)
    base = zfs.open(base)
    name = '/'.join([root, 'x y z'])
    base.clone(name)
    process_steps(args['steps'], name)


def run(args):
    pass


def create_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_build = subparsers.add_parser('build')
    parser_build.set_defaults(func=build)
    parser_build.add_argument('focker_dir', type=str)
    parser_run = subparsers.add_parser('run')
    parser_run.set_defaults(func=run)
    parser_rm = subparsers.add_parser('rm')
    parser_rmi = subparsers.add_parser('rmi')
    parser_ps = subparsers.add_parser('ps')
    parser_images = subparsers.add_parser('images')
    return parser


parser = create_parser()
args = parser.parse_args()
args.func(args)
