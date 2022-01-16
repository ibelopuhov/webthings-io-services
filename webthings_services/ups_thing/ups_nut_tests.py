from nut2 import PyNUTClient, PyNUTError
import pytest
from webthings_services.ups_thing.ups_nut_device_thing import UPSDevice


@pytest.fixture(scope='module')
def nut_params() -> dict:
    """
    Change host and port to real IP of your UPS before run test.

    :return:
    """
    return {"host": "127.0.0.1", "port": 3493}


def test_nut_client(nut_params) -> None:
    with PyNUTClient(nut_params['host']) as client:
        print(client.list_ups())
        print(client.list_vars("ups"))
        assert type(client.get_var('ups', 'input.voltage')) == str
        print(client.get_var('ups', 'battery.charge'))
        print(client.get_var('ups', 'output.voltage'))
        with pytest.raises(PyNUTError):
            client.get_var('ups', 'input.volt')


def test_ups_device(nut_params) -> None:
    ups_d = UPSDevice(**nut_params)
    ups_data = ups_d.read_ups_data()
    assert ups_data.get('batt_charge_level')
    assert ups_data.get('batt_charge_level') == 100
