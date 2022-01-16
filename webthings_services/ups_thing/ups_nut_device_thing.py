# from __future__ import division, print_function
import os
import logging

import tornado.ioloop
from nut2 import PyNUTClient
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)

from webthings_services.app_logging import get_logger

logger = logging


class UPSDevice:
    def __init__(self, host='localhost', port=3493):
        self.host = host
        self.port = port

    def read_ups_data(self) -> dict:
        data_dict = {'in_volt': 0.0, 'out_volt': 0.0, 'batt_charge_level': 0, 'load': 0, 'freq': 0.0}

        with PyNUTClient(host=self.host, port=self.port) as client:
            data_dict['in_volt'] = float(client.get_var('ups', 'input.voltage'))
            data_dict['out_volt'] = float(client.get_var('ups', 'output.voltage'))
            data_dict['batt_charge_level'] = int(client.get_var('ups', 'battery.charge'))

            return data_dict


class UPSDeviceThing(Thing):
    """UPS Device Thing """

    def __init__(self, upsdev: UPSDevice):
        Thing.__init__(
            self,
            'urn:dev:ops:my-nut-ups-device',
            'UPS Device',
            ['MultiLevelSensor'],
            'A web connected UPS Device'
        )

        self.__upsdev = upsdev
        self.voltageout = Value(0.0)
        self.voltagein = Value(0)
        self.batterycharge = Value(0)

        self.add_property(
            Property(self,
                     'voltagein',
                     self.voltagein,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Voltage In',
                         'type': 'number',
                         'description': 'The current input voltage in V',
                         'minimum': 0,
                         'maximum': 380,
                         'unit': 'volt',
                         'readOnly': True,
                     }))

        self.add_property(
            Property(self,
                     'voltageout',
                     self.voltageout,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Voltage Out',
                         'type': 'number',
                         'description': 'The UPS output voltage in V',
                         'minimum': 0,
                         'maximum': 380,
                         'unit': 'volt',
                         'readOnly': True,
                     }))

        self.add_property(
            Property(self,
                     'batterycharge',
                     self.batterycharge,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Battery Charge',
                         'type': 'number',
                         'description': 'The current battery charge level in %',
                         'minimum': 0,
                         'maximum': 100,
                         'unit': 'percent',
                         'readOnly': True,
                     }))

        logger.debug('starting the sensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.__update_data,
            5000
        )
        self.timer.start()

    def __update_data(self) -> None:
        data_dict = self.__upsdev.read_ups_data()
        logger.debug('updating new ups values: %s', data_dict)
        self.batterycharge.notify_of_external_update(data_dict['batt_charge_level'])
        self.voltagein.notify_of_external_update(data_dict['in_volt'])
        self.voltageout.notify_of_external_update(data_dict['out_volt'])

    def cancel_update_data_task(self):
        self.timer.stop()


def run_server(ups_host: str, ups_port: int = 3493, wss_port=8888) -> None:
    # Create an UPS device
    ups_device = UPSDeviceThing(UPSDevice(host=ups_host, port=ups_port))
    # Create WebThingServer
    server = WebThingServer(MultipleThings([ups_device], 'UpsDevice'), port=wss_port)
    try:
        logger.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logger.debug('canceling the sensor update looping task')
        ups_device.cancel_update_data_task()
        logger.info('stopping the server')
        server.stop()
        logger.info('done')


if __name__ == '__main__':
    wss_log_level = int(os.getenv("WSS_LOG_LEVEL"), logging.INFO)
    logger = get_logger('UPSDeviceThing_logger', wss_log_level, output_to_file=None)
    ups_host = os.getenv("WS_UPS_HOST", "localhost")
    ups_port = int(os.getenv("WS_UPS_PORT", 3493))
    wss_port = int(os.getenv("WSS_UPS_SERVER_PORT", 8888))
    logger.debug(f"Current envs {ups_host} {ups_port} {wss_port}")

    run_server(ups_host, ups_port, wss_port)
