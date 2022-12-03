from focker.jailconf import load
from focker.misc.load_jailconf import *


def main():
    jc = load()
    for name, entry in jc.jail_blocks.items():
        print(name)
        entry = entry.to_dict()
        jailconf_add_jail(name=name, entry=entry)
    print('Done.')


if __name__ == '__main__':
    main()
