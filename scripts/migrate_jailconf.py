from focker.jailconf import load
from focker.misc.load_jailconf import *
from focker.core import FOCKER_CONFIG


def main():
    jc = load()
    for name, entry in jc.jail_blocks.items():
        if not entry.safe_get('path', '').startswith(FOCKER_CONFIG.zfs.root_mountpoint + '/jails/'):
            print(f'Skipping non-Focker jail: {name}')
            continue
        print(name)
        entry = entry.to_dict()
        jailconf_add_jail(name=name, entry=entry)
    print('Done.')


if __name__ == '__main__':
    main()
