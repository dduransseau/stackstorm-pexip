__author__ = "Damien Duransseau"
__version__ = "0.1.0"


from st2actions.runners.pythonrunner import Action
from lib.base import Pexip


class TakeSnapshot(Action):
    def run(self, path, url, user, password):
        _url = url or self.config.get("url")
        _user = user or self.config.get("user")
        _password = password or self.config.get("password")
        pexip = Pexip(_url, _user, _password)
        pexip.take_snapshot(path)