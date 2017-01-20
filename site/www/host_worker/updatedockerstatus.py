from .tasks import dockerStatus
import threading
import time
import logging
from celery.worker import state


class UpdateDockerStatus(threading.Thread):
    update_interval = 10

    def run(self):
        logger = logging.getLogger('UpdateDockerStatus')
        logger.debug("Start update docker status thread:" + str(state.should_stop))
        counter = self.update_interval
        while not state.should_stop:
            counter -= 1
            if counter == 0:
                logging.debug("Update docker status")
                try:
                    dockerStatus(None, {"update_interval": self.update_interval})
                except Exception as e:
                    logging.error('Update failed with:' + str(e))
                counter = self.update_interval
            time.sleep(1)

UpdateDockerStatus().start()
