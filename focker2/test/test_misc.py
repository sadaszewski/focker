from focker.misc.lock import focker_lock, \
    focker_unlock
from focker.misc import load_jailconf, \
    backup_file
from focker.jailconf import JailConf
from focker.jailconf.classes import Value
from focker.jailconf.misc import quote_value


class TestMisc:
    def test01_focker_unlock_fd_none(self):
        if focker_lock.fd is not None:
            focker_lock.fd.close()
            focker_lock.fd = None
        assert focker_lock.fd is None
        focker_unlock()
        assert focker_lock.fd is None

    def test02_load_jailconf_missing(self):
        res = load_jailconf('/this/file/surely/cannot/exist')
        assert isinstance(res, JailConf)

    def test03_backup_file_missing(self):
        res = backup_file('/this/file/surely/cannot/exist')
        assert res == (None, False)

    def test04_jailconf_quote_value_list(self):
        assert quote_value([]) is None
        assert quote_value([Value(1), Value(2)]) == '1,2'
