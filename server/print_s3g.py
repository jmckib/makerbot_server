from __future__ import absolute_import
import argparse
import sys
sys.path.append('/Users/jeremy/src/make-me/vendor/s3g')

import makerbot_driver

import RawFileReader


def print_s3g(input_file):
    md = makerbot_driver.MachineDetector()
    md.scan()
    port = md.get_first_machine()
    if port is None:
        raise RuntimeError("Can't Find 3D Printer")

    factory = makerbot_driver.MachineFactory()
    obj = factory.build_from_port(port)

    s3g = getattr(obj, 's3g')
    reader = RawFileReader()
    reader.file = input_file
    for command, params in reader.ReadFile():
        s3g.writer.send_action_payload(command)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send an s3g (or x3g) file to a 3D printer via USB.')
    parser.add_argument('input_file', type=argparse.FileType('rb'))
    args = parser.parse_args()

    print_s3g(args.input_file)
