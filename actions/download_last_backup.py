__author__ = "Damien Duransseau"
__version__ = "0.2.0"


from st2actions.runners.pythonrunner import Action
from lib.base import Pexip


class SaveBackup(Action):
    def run(self, path, url, login, password):
        _url = url or self.config.get("url")
        _login = login or self.config.get("login")
        _password = password or self.config.get("password")
        pexip = Pexip(_url, _login, _password)
        pexip.save_last_backup_file(path)