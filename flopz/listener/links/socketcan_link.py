import multiprocessing
import queue
from multiprocessing import Process
from socket import *
import struct
import select
import argparse
import socket
import logging

from flopz.listener.link import Link


class SocketcanLinkException(Exception):
    pass

class SocketCanRxProcess(Process):
    """
    Use a separate process to handle reading from the raw socket
    """
    def __init__(self, bound_socket, rx_queue: multiprocessing.Queue,
                 stop_event: multiprocessing.Event):
        super().__init__()

        # socket must be bound and closed by calling class
        self.socket = bound_socket

        self.active = True
        self.started = None

        self.rx_queue = rx_queue
        self.stop_event = stop_event

    def run(self):
        inputs = [self.socket]
        outputs = [self.socket]

        # socketcan standard format, 4byte id, 1byte data length, 3byte padding, up to 8 byte data
        # modify for FD
        fmt = '<IB3x8s'

        while self.active:
            # wait until input becomes readable. we don't care about writing, as that's done elsewhere
            readable, writeable, errors = select.select(inputs, [], [], 1)

            for r in readable:
                message = r.recv(16)
                if message:
                    can_id, length, data = struct.unpack(fmt, message)
                    can_id &= CAN_EFF_MASK
                    data = data[:length]
                    self.rx_queue.put((can_id, length, data))

            for e in errors:
                if e in inputs:
                    inputs.remove(e)
                if e in outputs:
                    outputs.remove(e)
                logging.error("Something went wrong!")


class SocketcanLink(Link):
    def __init__(self, flopz_config: dict, arg_parser: argparse.Namespace):
        super().__init__(flopz_config, arg_parser)
        if not arg_parser.socketcan_interface:
            raise SocketcanLinkException("No socketcan interface specified!")

        self.socketcan_inteerface = arg_parser.socketcan_interface
        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.rx_queue = multiprocessing.Queue()
        self.stop_rx_event = multiprocessing.Event()
        self.logger_process = None

    def start(self) -> None:
        try:
            self.socket.bind((self.socketcan_inteerface,))
            self.logger_process = SocketCanRxProcess(self.socket, self.rx_queue, self.stop_rx_event)
            self.logger_process.start()
        except OSError:
            raise SocketcanLinkException(f"Could not bind to socketcan interface {self.socketcan_inteerface}!")

    def stop(self) -> None:
        self.stop_rx_event.set()
        self.socket = None

    def get(self) -> bytes:
        """
        No matter if FD or not, the return value of this will always be the same binary format
        Protocols need to handle decoding the ID, length etc.
        :return: [4 byte id][1 byte lenght][$length bytes payload]
        """
        try:
            q_data = self.rx_queue.get(timeout=0.05) # block at most 50ms
            if q_data:
                can_id, length, data = q_data
                return struct.pack('IB', can_id, length) + data
        except queue.Empty:
            return b''

    def put(self, payload: bytes) -> int:
        """
        Send some data over CAN. Make sure to format extended IDs correctly (needs arb_id |= 0x80000000)
        :param payload: bytes in the same binary format as get() returns
        :return: number of bytes transferred
        """
        self.socket.send(payload)

    @staticmethod
    def add_argparse(parser: argparse.ArgumentParser):
        group = parser.add_argument_group("SocketCan Options")
        group.add_argument("--socketcan-interface", metavar="socketcan_interface", type=str,
                           help="Which socketcan interface to use, for example: vcan0")

    @staticmethod
    def name() -> str:
        return 'socketcan'