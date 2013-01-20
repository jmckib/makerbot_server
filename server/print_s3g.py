import argparse
import os
import sys

lib_path = os.path.abspath(os.path.dirname(__file__) + '/../thirdparty/s3g')
sys.path.append(lib_path)
import makerbot_driver

import RawFileReader


def print_s3g(s3g_file):
    md = makerbot_driver.MachineDetector()
    md.scan()
    port = md.get_first_machine()
    if port is None:
        raise RuntimeError("Can't Find 3D Printer")

    obj = makerbot_driver.MachineFactory().build_from_port(port)

    reader = RawFileReader()
    reader.file = s3g_file
    for command, params in reader.ReadFile():
        obj.s3g.writer.send_action_payload(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send an s3g (or x3g) file to a 3D printer via USB.')
    parser.add_argument('s3g_file', type=argparse.FileType('rb'))
    args = parser.parse_args()

    print_s3g(args.s3g_file)
