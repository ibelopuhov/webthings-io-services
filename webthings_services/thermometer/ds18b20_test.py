from webthings_services.thermometer.rpi_ds18b20_thing import DS18B20ThermometerSensor


def test_18b20_thermometer_availability() -> None:
    ds_thermo = DS18B20ThermometerSensor()
    data = ds_thermo.read_temp()
    assert type(data[0]) == float and type(data[1]) == float
