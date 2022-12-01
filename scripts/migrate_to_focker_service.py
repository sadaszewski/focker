from focker import jailconf
from focker.core.config import FOCKER_CONFIG
import os
import json


def main():
    jc = jailconf.load()
    for name, blk in jc.jail_blocks.items():
        if not 'path' in blk:
            continue
        if not blk['path'].startswith(FOCKER_CONFIG.zfs.root_mountpoint + '/jails/'):
            continue
        print(name)
        os.makedirs(os.path.join(blk['path'], '.ssman'), exist_ok=True)
        fname = os.path.join(blk['path'], '.ssman', 'jail_config.json')
        with open(os.open(fname, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600), 'w') as f:
            params = blk.to_dict()
            params['name'] = name
            json.dump(params, f)


if __name__ == '__main__':
    main()
