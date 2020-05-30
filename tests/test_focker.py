from focker.focker import *
import focker.focker
from collections import defaultdict
import sys
import pytest


def test_parser_bootstrap():
    parser = create_parser()

    args = parser.parse_args(['bootstrap', '--empty', '--tags', 'a', 'b', 'c'])
    assert args.func == command_bootstrap
    assert args.tags == ['a', 'b', 'c']
    assert args.empty


def test_parser_image():
    parser = create_parser()

    args = parser.parse_args(['image', 'build', '.', '--squeeze', '--tags', 'a', 'b', 'c'])
    assert args.func == command_image_build
    assert args.focker_dir == '.'
    assert args.tags == ['a', 'b', 'c']
    assert args.squeeze

    args = parser.parse_args(['image', 'tag', 'deadbee', 'a', 'b', 'c'])
    assert args.func == command_image_tag
    assert args.reference == 'deadbee'
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['image', 'untag', 'a', 'b', 'c'])
    assert args.func == command_image_untag
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['image', 'list', '--full-sha256', '--tagged-only'])
    assert args.func == command_image_list
    assert args.full_sha256
    assert args.tagged_only

    args = parser.parse_args(['image', 'prune'])
    assert args.func == command_image_prune

    args = parser.parse_args(['image', 'remove', 'a', '--remove-dependents', '--force'])
    assert args.func == command_image_remove
    assert args.reference == 'a'
    assert args.remove_dependents
    assert args.force


def test_parser_jail(monkeypatch):
    parser = create_parser()

    counter = [0]
    def count_calls(fun, counter):
        def inner(*args, **kwargs):
            counter[0] += 1
            return fun(*args, **kwargs)
        return inner
    monkeypatch.setattr(parser, 'parse_args', count_calls(parser.parse_args, counter))

    args = parser.parse_args(['jail', 'create', 'freebsd-latest', '--command', '/test-command', '--tags', 'a', 'b', 'c', '--env', 'd:1', 'e:2', '--mounts', 'mount-A:/a', 'mount-B:/b', '--hostname', 'xyz'])
    assert args.func == command_jail_create
    assert args.command == '/test-command'
    assert args.tags == ['a', 'b', 'c']
    assert args.env == ['d:1', 'e:2']
    assert args.mounts == ['mount-A:/a', 'mount-B:/b']
    assert args.hostname == 'xyz'

    args = parser.parse_args(['jail', 'start', 'jail-A'])
    assert args.func == command_jail_start
    assert args.reference == 'jail-A'

    args = parser.parse_args(['jail', 'stop', 'jail-A'])
    assert args.func == command_jail_stop
    assert args.reference == 'jail-A'

    args = parser.parse_args(['jail', 'remove', 'jail-A', '--force'])
    assert args.func == command_jail_remove
    assert args.reference == 'jail-A'
    assert args.force

    args = parser.parse_args(['jail', 'exec', 'jail-A', '/bin/sh', '-c', 'ls', '-al'])
    assert args.func == command_jail_exec
    assert args.reference == 'jail-A'
    assert args.command == ['/bin/sh', '-c', 'ls', '-al']

    args = parser.parse_args(['jail', 'oneshot', '--env', 'd:1', 'e:2', '--mounts', 'mount-A:/a', 'mount-B:/b', '--', 'image-A', '/bin/sh', '-c', 'ls', '-al'])
    assert args.func == command_jail_oneshot
    assert args.image == 'image-A'
    assert args.env == ['d:1', 'e:2']
    assert args.mounts == ['mount-A:/a', 'mount-B:/b']
    assert args.command == ['/bin/sh', '-c', 'ls', '-al']

    args = parser.parse_args(['jail', 'list', '--full-sha256'])
    assert args.func == command_jail_list
    assert args.full_sha256

    args = parser.parse_args(['jail', 'tag', 'deadbee', 'a', 'b', 'c'])
    assert args.func == command_jail_tag
    assert args.reference == 'deadbee'
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['jail', 'untag', 'a', 'b', 'c'])
    assert args.func == command_jail_untag
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['jail', 'prune', '--force'])
    assert args.func == command_jail_prune
    assert args.force

    assert counter[0] == 10


def test_parser_volume(monkeypatch):
    parser = create_parser()

    counter = [0]
    def count_calls(fun, counter):
        def inner(*args, **kwargs):
            counter[0] += 1
            return fun(*args, **kwargs)
        return inner
    monkeypatch.setattr(parser, 'parse_args', count_calls(parser.parse_args, counter))

    args = parser.parse_args(['volume', 'create', '--tags', 'a', 'b', 'c'])
    assert args.func == command_volume_create
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['volume', 'prune'])
    assert args.func == command_volume_prune

    args = parser.parse_args(['volume', 'list', '--full-sha256'])
    assert args.func == command_volume_list
    assert args.full_sha256

    args = parser.parse_args(['volume', 'tag', 'deadbee', 'a', 'b', 'c'])
    assert args.func == command_volume_tag
    assert args.reference == 'deadbee'
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['volume', 'untag', 'a', 'b', 'c'])
    assert args.func == command_volume_untag
    assert args.tags == ['a', 'b', 'c']

    args = parser.parse_args(['volume', 'remove', 'volume-A', 'volume-B', '--force'])
    assert args.func == command_volume_remove
    assert args.references == ['volume-A', 'volume-B']
    assert args.force

    args = parser.parse_args(['volume', 'set', 'volume-A', 'rdonly=on', 'quota=1G'])
    assert args.func == command_volume_set
    assert args.reference == 'volume-A'
    assert args.properties == ['rdonly=on', 'quota=1G']

    args = parser.parse_args(['volume', 'get', 'volume-A', 'rdonly', 'quota'])
    assert args.func == command_volume_get
    assert args.reference == 'volume-A'
    assert args.properties == ['rdonly', 'quota']

    assert counter[0] == 8


def test_parser_compose():
    parser = create_parser()

    args = parser.parse_args(['compose', 'build', '--squeeze', '/a/b/c/focker-compose.yml'])
    assert args.func == command_compose_build
    assert args.filename == '/a/b/c/focker-compose.yml'
    assert args.squeeze

    args = parser.parse_args(['compose', 'run', '/a/b/c/focker-compose.yml', 'noop'])
    assert args.func == command_compose_run
    assert args.filename == '/a/b/c/focker-compose.yml'
    assert args.command == 'noop'


def test_focker_main_01(monkeypatch):
    log = defaultdict(list)
    def log_call(fun):
        def inner(*args, **kwargs):
            log[fun.__name__].append((args, kwargs))
            return fun(*args, **kwargs)
        return inner
    monkeypatch.setattr(focker.focker, 'focker_lock', log_call(focker_lock))
    monkeypatch.setattr(focker.focker, 'zfs_init', log_call(zfs_init))
    monkeypatch.setattr(focker.focker, 'create_parser', log_call(create_parser))
    monkeypatch.setattr(focker.focker, 'command_image_list', log_call(command_image_list))
    monkeypatch.setattr(sys, 'argv', ['focker', 'image', 'list'])
    main()
    assert len(log) == 4
    assert 'focker_lock' in log
    assert 'zfs_init' in log
    assert 'create_parser' in log
    assert 'command_image_list' in log


def test_focker_main_02(monkeypatch):
    log = defaultdict(list)
    def log_call(fun):
        def inner(*args, **kwargs):
            log[fun.__name__].append((args, kwargs))
            return fun(*args, **kwargs)
        return inner
    monkeypatch.setattr(sys, 'argv', ['focker'])
    monkeypatch.setattr(sys, 'exit', log_call(sys.exit))
    with pytest.raises(SystemExit):
        main()
    assert len(log) == 1
    assert 'exit' in log
