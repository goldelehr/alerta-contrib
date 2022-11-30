import os
import logging
import requests

from alerta.plugins import PluginBase
from alertaclient.api import Client

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.forward')

FORWARD_URL = os.environ.get(
    'FORWARD_URL') or app.config.get('FORWARD_URL')
FORWARD_API_KEY = os.environ.get(
    'FORWARD_API_KEY') or app.config.get('FORWARD_API_KEY')
FORWARD_MAX_LENGTH = os.environ.get(
    'FORWARD_MAX_LENGTH') or app.config.get('FORWARD_MAX_LENGTH') or 3

class ForwardAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if not FORWARD_URL or not FORWARD_API_KEY:
            return

        message = "%s: %s alert for %s - %s" %( alert.environment, alert.severity.capitalize(), ','.join(alert.service), alert.resource)
        payload = {
            "source_id": alert.id,            
            "description": message,
            "resource": alert.resource,
            "source": "alerta"
        }    

        try:
            r = requests.post(FORWARD_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("AlertOps connection error: %s" % e)
        LOG.debug('AlertOps response: %s - %s' % (r.status_code, r.text))
        return

    def status_change(self, alert, status, text):
        return
