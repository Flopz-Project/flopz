import argparse
import json
import logging
import signal

from flopz.listener.link import Link
from flopz.listener.flopz_logger import FlopzLogger
from flopz.listener.loggers.all_loggers import get_logger_by_name
from flopz.listener.loggers.console_logger import ConsoleLogger
from flopz.listener.protocol import Protocol
from flopz.listener.links.all_links import get_link_by_name, get_all_links
from flopz.target.all_targets import get_target_by_name


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Process cmd options')
    parser.add_argument('-t', metavar='target', type=str, help='name of the target', required=True)
    parser.add_argument('-l', metavar='link', type=str, help='which link to use (e.g. CAN)', required=True)
    parser.add_argument('-c', metavar='config', type=str, help='the json config file generated using the ghidra plugin', required=True)
    parser.add_argument('--logger', metavar='logger', type=str,
                        help='Which output format to use. Choose from: console, json', required=True)
    parser.add_argument('--output-directory', metavar='output_directory', type=str,
                        help='A path to directory for storing the output files')
    parser.add_argument('--no-console-log', dest='console_log', action='store_false')
    parser.set_defaults(console_log=True)

    for link in get_all_links():
        link.add_argparse(parser)

    return parser


def listener(args, config: dict, link: Link, protocol: Protocol, logger: FlopzLogger):
    # prevent initializing console logger twice
    if isinstance(logger, ConsoleLogger):
        console_logger = logging.getLogger('dummy')
    else:
        console_logger = ConsoleLogger(config)

    try:
        link.start()
        while True:
            data = link.get()
            protocol.feed(data)
            while protocol.has_events():
                event = protocol.get_event()
                if event.is_interactive():
                    event.enter()
                else:
                    logger.log(event)
                    # don't log to the console twice and only log to console if it hasn't been disabled
                    if args.console_log and not isinstance(logger, ConsoleLogger):
                        console_logger.log(event)

    except(KeyboardInterrupt):
        # here, we can close and flush everything properly before exiting
        logging.error("Exiting..")
        link.stop()
        logger.flush()
        logger.close()

def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    config_filename = args.c
    with open(config_filename, 'r') as f:
        config = json.load(f)

    target_cls = get_target_by_name(args.t)
    if target_cls is None:
        logging.error("Failed to look up target! Did you provide a registered target name?")
        return

    # get a link and create the protocol directly from our target class
    link = get_link_by_name(args.l)(config, args)
    protocol = target_cls.get_protocol()(config, link)
    logger = get_logger_by_name(args.logger)(config, args)

    listener(args, config, link, protocol, logger)



if __name__ == "__main__":
    main()
