__author__ = "Damien Duransseau"
__version__ = "0.1.0"

import logging
from datetime import datetime

import requests

class Pexip:
    def __init__(self, host, user, password):
        """ Initialize the Pexip Monitoring SDK """
        self.datetime_iso_format = "%Y-%m-%dT%H:%M:%S"
        try:
            self.MANAGEMENT_NODE_URL = "HTTPS://%s" % host
        except KeyError:
            logging.critical("Management node host unspecified")
        try:
            self.MANAGEMENT_NODE_CREDENTIALS = (user, password)
        except KeyError:
            logging.critical("Management node credentials unspecified")
        #Command URL
        self.create_backup_url = "/api/admin/command/v1/platform/backup_create/"
        self.snapshot_url = "/api/admin/command/v1/platform/snapshot/"
        #Configuration URL
        self.list_backup_url = "/api/admin/configuration/v1/system_backup/"

    def _get_response_json(self, url, offset=20, full=True):
        """ Retrieve and parse response from API
        :param url: Management Node url
        :param offset: Number of records to retrieve per requests
        :param full: Need to retrieve the full list of records or not
        :return: Result of API request
        """
        response = requests.get(
            self.MANAGEMENT_NODE_URL+url,
            auth=self.MANAGEMENT_NODE_CREDENTIALS
            )
        if response.status_code == 200:
            response_json = response.json()
            if "meta" in response_json.keys():
                if response_json['meta']['next'] is None or full is False:
                    return response_json['objects']
                else:
                    response_list = []
                    response_list.append(response_json['objects'])
                    url = response_json['meta']['next']
                    while url is not None:
                        response = requests.get(
                            self.MANAGEMENT_NODE_URL+url,
                            auth=self.MANAGEMENT_NODE_CREDENTIALS
                            )
                        response_json = response.json()
                        response_list.append(response_json['objects'])
                    return response_list
            else:
                return response_json
        else:
            logging.error("No data retrieved from API")

    def create_system_backup(self, passphrase=''):
        response = requests.post(
            self.MANAGEMENT_NODE_URL+self.create_backup_url,
            auth=self.MANAGEMENT_NODE_CREDENTIALS,
            data={
                'passphrase': passphrase
            }
        )
        if response.status_code == 202:
            logging.info("Backup created")
            return True
        else:
            logging.error("Backup failed")
            return False

    def get_backup_list(self):
        return self._get_response_json(url=self.list_backup_url)

    def get_last_backup(self):
        backup_list = self.get_backup_list()
        last_backup_id = 0
        backup_list[last_backup_id]['date'] = datetime.strptime(backup_list[last_backup_id]['date'],
                                                                self.datetime_iso_format)
        last_backup_date = backup_list[last_backup_id]['date']
        for i, backup in enumerate(backup_list):
            if type(backup_list[i]['date']) is str:
                backup_list[i]['date'] = datetime.strptime(backup['date'], self.datetime_iso_format)
            if backup_list[i]['date'] > last_backup_date:
                last_backup_date = backup_list[i]['date']
                last_backup_id = i
        return backup_list[last_backup_id]
        # last_backup = sorted(self.get_backup_list(), key=lambda k: k['date'])[0]
        # last_backup['date'] = datetime.strptime(last_backup['date'], self.datetime_iso_format)
        # return last_backup

    def download_backup(self, backup_uri):
        response = requests.get(
            self.MANAGEMENT_NODE_URL + backup_uri,
            auth=self.MANAGEMENT_NODE_CREDENTIALS
        )
        if response.status_code == 200:
            return response.content
        else:
            logging.error("Download backup failed")
            raise IOError("Download backup failed")

    def save_last_backup_file(self, path='./', filename=""):
        last_backup = self.get_last_backup()
        if not filename:
            filename = last_backup['filename']
        with open(path+filename, "wb") as backup_file:
            backup_file.write(self.download_backup(last_backup['resource_uri']))
            logging.info("Backup saved")

    def take_snapshot(self, path, limit=4):
        response = requests.post(
            self.MANAGEMENT_NODE_URL+self.snapshot_url,
            auth=self.MANAGEMENT_NODE_CREDENTIALS,
            data={
                'limit': limit
            }
        )
        if response.status_code == 200:
            filename = response.headers['content-disposition'].lstrip("attachment; filename=")
            with open(path+filename, "wb") as snapshot_file:
                snapshot_file.write(response.content)
                logging.info("Snapshot saved")
        else:
            logging.error("Error to take snapshot")