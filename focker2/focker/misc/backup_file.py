import os
import time
import shutil


def backup_file(fname, interval=24*3600, chmod=0o600):
    if not os.path.exists(fname):
        return None, False

    bakname = f'{fname}.bak'
    if os.path.exists(bakname):
        st = os.stat(bakname)
        if time.time() - st.st_mtime < interval:
            return bakname, False

    shutil.copyfile(fname, bakname)
    os.chmod(bakname, chmod)
    return bakname, True
