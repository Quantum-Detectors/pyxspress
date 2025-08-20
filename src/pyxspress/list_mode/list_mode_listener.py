"""
Xspress Mini Mk2 list mode test module

This module is used to test reading list mode events over the TCP streams from the
X3X2 systems.

Each card has its own socket which is used to send all of the events for its channels
and markers.
"""

import ipaddress
import socket
import time
from threading import Thread

from pyxspress.util import Loggable


class ListModeListener(Loggable):
    connection_timeout = 3
    packet_size_bytes = 8192

    def __init__(self, ip_address: str, file_name: str | None):
        """Create a new listener which listens to the TCP port of a single
        X3X2 card for event data (port 30125).

        If given a file name then it will also save all of the data it
        receives.

        Args:
            ip_address (str): IP address of card
            file_name (Optional[str]): Filename to save binary stream to
        """
        super().__init__()

        self.ip_address = ipaddress.ip_address(ip_address)
        self.port = 30125
        self.file_name = file_name

        self.connected = False
        self.printed = False

        self.__connect()

        self.data_task_enabled = False
        self.data_thread = Thread(target=self.__data_task, daemon=True)
        self.data_thread.start()

        self.logger.info(
            f"Listener started for {self.ip_address}:{self.port} (filename {file_name})"
        )

    def __connect(self):
        self.logger.info(f"Connecting to {self.ip_address}:{self.port}")
        try:
            self.__disconnect()

            # Connect using the initial timeout value
            self.socket = socket.create_connection(
                (f"{self.ip_address}", self.port),
                timeout=self.connection_timeout,
            )
            self.logger.info(f"Connected to port: {self.ip_address}:{self.port}")

            # Update the timeout so we can block in the data thread
            self.socket.settimeout(None)
            self.connected = True

        except ConnectionRefusedError:
            self.logger.error(
                f"Could not connect to port: {self.ip_address}:{self.port} (refused)"
            )
        except TimeoutError:
            self.logger.error(
                f"Timeout trying to connect to port: {self.ip_address}:{self.port}"
            )

    def __disconnect(self):
        """Try and disconnect from the socket"""
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except OSError:
            pass
        except AttributeError:
            # Not been created yet
            pass

        self.connected = False

    def __del__(self):
        """Called when deleted"""
        self.data_task_enabled = False
        self.__disconnect()

    def __receive_bytes(self, num_bytes: int) -> bytearray:
        """Block until a requested number of bytes are received over the
        socket.

        Args:
            num_bytes (int): Number of bytes

        Returns:
            bytearray: Byte array
        """
        data = bytearray()
        start_time = time.perf_counter()
        while len(data) < num_bytes:
            new_data = self.socket.recv(num_bytes - len(data))
            if len(new_data) == 0:
                raise ValueError("No data returned from socket")
            else:
                data.extend(new_data)

        self.logger.info(
            f"Got {num_bytes} bytes in {time.perf_counter() - start_time:.6f}s"
        )
        return data

    def __receive_data(self):
        """Receive bytes and write them"""
        packet = self.__receive_bytes(self.packet_size_bytes)
        if self.file_name:
            with open(self.file_name, "ab") as data_file:
                data_file.write(packet)

    def __data_task(self):
        self.logger.info(f"Starting data task for {self.ip_address}:{self.port}")
        self.data_task_enabled = True

        while self.data_task_enabled:
            if self.connected:
                try:
                    self.__receive_data()
                except Exception as e:
                    # We can get an exception if the socket was closed
                    if not self.data_task_enabled:
                        break

                    self.logger.error(f"Failed to get data ({e})")
                    self.connected = False
            else:
                # Try and reconnect
                time.sleep(0.1)
                self.__connect()

        self.logger.info(
            f"Stopping data thread for address {self.ip_address}:{self.port}"
        )

    def stop(self):
        """Disconnect the data socket and set the data thread flag to stop it"""
        self.logger.info(f"Stopping connection to {self.ip_address}:{self.port}")
        self.data_task_enabled = False
        self.__disconnect()
        self.data_thread.join()
