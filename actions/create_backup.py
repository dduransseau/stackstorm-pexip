__author__ = "Damien Duransseau"
__version__ = "0.1.0"


from st2actions.runners.pythonrunner import Action
from lib.base import Pexip


class SaveBackup(Action):
    def run(self, passphrase, url, login, password):
        _url = url or self.config.get("url")
        _login = login or self.config.get("login")
        _password = password or self.config.get("password")
        pexip = Pexip(_url, _login, _password)
        pexip.create_system_backup(passphrase)