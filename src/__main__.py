import argparse
import telemetry

def main():
    parser = argparse.ArgumentParser(description='Kerbal Space Program Telemetry System')
    parser.add_argument('command', type=str, choices=['capture', 'dump'])

    args = parser.parse_args()

    if args.command == 'capture':
        telemetry.capture()
    elif args.command == 'dump':
        telemetry.dump()