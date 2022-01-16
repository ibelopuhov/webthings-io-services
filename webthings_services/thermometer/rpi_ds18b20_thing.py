# from __future__ import division, print_function
import os
import logging
import glob
import pathlib
import time
from typing import List, AnyStr
from abc import ABC, abstractmethod

import tornado.ioloop
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)
from webthings_services.app_logging import get_logger

logger = logging


class ThermometerSensor(ABC):
    name = 'ThermometerSensor'

    @abstractmethod
    def _read_temp_raw(self) -> List[AnyStr]:
        """
        Returns temperature in a raw format

        :return: List of data strings from device
        """
        pass

    @abstractmethod
    def read_temp(self) -> tuple[float, float]:
        """
        Return temperature as a tuple (C_temp, F_temp)

        :return: tuple(float, float)
        """
        pass


class DS18B20ThermometerSensor(ThermometerSensor):
    def __init__(self):
        self.name = 'ThermometerSensor DS18B20'
        self.base_dir = '/sys/bus/w1/devices/'

        b_dirs = glob.glob(self.base_dir + '28*')
        if b_dirs and len(b_dirs) > 0:
            device_folder = b_dirs[0]
            self.device_file = device_folder + '/w1_slave'
        else:
            raise FileNotFoundError(self.base_dir + '28*')

        # check if device file exist in the system
        if not pathlib.Path(self.device_file).exists():
            err_msg = f"No sensor device exists by path {self.device_file}"
            raise FileNotFoundError(err_msg)

    def _read_temp_raw(self) -> List[AnyStr]:
        with open(self.device_file, 'r') as dev_fd:
            return dev_fd.readlines()

    def read_temp(self) -> tuple[float, float]:
        lines = self._read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f


class ThermometerSensorThing(Thing):
    """Thermometer Sensor Thing for DS18B20 connected to GPIO of RPI"""
    name = 'ThermometerSensorThing DS18B20'

    def __init__(self, sensor: ThermometerSensor):
        Thing.__init__(
            self,
            'urn:dev:ops:thermometer-sensor-DS18B20',
            'Thermometer Sensor',
            ['MultiLevelSensor'],
            'Thermometer sensor, connected to GPIO of RPI'
        )
        self.sensor = sensor
        self.temp = Value(0.0)

        self.add_property(
            Property(self,
                     'temp',
                     self.temp,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Temperature',
                         'type': 'number',
                         'description': 'The current temperature in C',
                         'minimum': -80,
                         'maximum': 80,
                         'unit': 'celsius',
                         'readOnly': True,
                     }))

        logger.debug('starting the ThermometerSensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.__update_data,
            5000
        )
        self.timer.start()

    def __update_data(self):
        data_dict = self.sensor.read_temp()
        self.temp.notify_of_external_update(data_dict[0])
        logger.debug(f" C_temp={data_dict[0]}; F_temp={data_dict[1]}")

    def cancel_update_level_task(self):
        self.timer.stop()


def run_server(port: int):
    # Create a thing that represents a thermometer sensor
    sensor = ThermometerSensorThing(DS18B20ThermometerSensor())
    server = WebThingServer(MultipleThings([sensor], 'ThermometerDevice'), port=port)

    try:
        logger.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logger.debug('canceling the sensor update looping task')
        sensor.cancel_update_level_task()
        logger.info('stopping the server')
        server.stop()
        logger.info('done')


if __name__ == '__main__':
    wss_log_level = int(os.getenv("WSS_LOG_LEVEL"), logging.INFO)
    logger = get_logger('ThermometerSensorThing', wss_log_level, output_to_file=None)
    wss_port = int(os.getenv("WSS_THERMO_SERVER_PORT", 8884))
    run_server(wss_port)
