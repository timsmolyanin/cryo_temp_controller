import time
from threading import Thread
import serial
import struct
import os
import meta_funcs


class NextionReader(Thread):
    """
    """
    def __init__(self, comport_status, comport, parent=None):
        super(NextionReader, self).__init__(parent)
        self.comport_status = comport_status
        self.comport = comport


    def run(self) -> None:
        while True:
            serial_read(self.comport_status, self.comport, self.cb)
    

    def cb(self, data):
        print(data)
        data_list = data.split("/")
        match data_list[0]:
            case "Heater":
                match data_list[1]:
                    case "State":
                        match data_list[-1]:
                            case "OFF":
                                meta_funcs.switch_heater_state(0)
                            case "ON":
                                meta_funcs.switch_heater_state(1)
                    case "Voltage":
                        set_voltage = float(data_list[-1])
                        

def serial_connect(com: str, baud: int) -> list:
    """
    """
    print("Connect to COM-port")
    serial_port_open_flag = False
    serial_port = None
    while not serial_port_open_flag:
        time.sleep(1)
        try:
            serial_port = serial.Serial(port=com,
                                        baudrate=baud,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=1)

            serial_port_open_flag = serial_port.isOpen()
        except serial.serialutil.SerialException as exc:
            # TODO: log error
            print(exc)
            serial_port_open_flag = False

        return [serial_port_open_flag, serial_port]


def serial_read(st, com, cb):
    """
    """
    while st:
        if not st:
            break
        response = ""
        try:
            response = com.readline()
            if response == b'':
                # Nextion send empty string every second
                pass
            else:
                decode_data = response.decode('Ascii')
                if str(decode_data[-2:]).encode('Ascii') == b'\r\n':
                    # убираем /r/n в конце строки, получается список [decode_data], поэтому отдаем нулевой id
                    cb(decode_data.splitlines()[0])
                    response = ""
        except Exception as exc:
            print("Exception while serial_read method.", exc)


def serial_write(sp, cmd):
    """
    """

    eof = struct.pack('B', 0xff)
    try:
        sp.write(cmd.encode())
        sp.write(eof)
        sp.write(eof)
        sp.write(eof)
    except Exception as exc:
        print("Exception while serial_write method.", exc)


def _test_main():
    serial_port = serial.Serial(port="COM5",
                                baudrate=115200,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS,
                                timeout=1)

    nextion_reader = NextionReader(True, serial_port)
    nextion_reader.run()
    


if __name__ == "__main__":
    _test_main()
