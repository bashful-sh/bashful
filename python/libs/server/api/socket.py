import time
import json
import logging


class ClientManager:
    """
    The ClientManager is the server side interface for (in/out)bound
    websocket connections.

    Using the websocket interface allows the client/sever to
    send and receive messages in a managed, cached, and scalable manner.
    """

    def __init__(self, max_clients: int = 2, max_connection_time: int = 10) -> None:
        """
        Initialize the ClientManager with specified limits on client
        connections and connection durations.
        """
        self.clients = {}
        self.start_times = {}
        self.max_clients = max_clients
        self.max_connection_time = max_connection_time

    def add_client(self, websocket, client) -> None:
        """
        Adds a client and their connection start time to the tracking
        dictionaries.
        """
        self.clients[websocket] = client
        self.start_times[websocket] = time.time()

    def get_client(self, websocket) -> object | bool:
        """
        Retrieves a client associated with the given websocket.
        """
        if websocket in self.clients:
            return self.clients[websocket]
        return False

    def remove_client(self, websocket) -> None:
        """
        Removes a client and their connection start time from the
        tracking dictionaries. Performs cleanup on the client if necessary.
        """
        client = self.clients.pop(websocket, None)
        if client:
            client.cleanup()
        self.start_times.pop(websocket, None)

    def get_wait_time(self) -> int | float:
        """
        Calculates the estimated wait time for new clients based on
        the remaining connection times of current clients.
        """
        wait_time = None
        for start_time in self.start_times.values():
            current_client_time_remaining = self.max_connection_time - (
                time.time() - start_time
            )
            if wait_time is None or current_client_time_remaining < wait_time:
                wait_time = current_client_time_remaining
        return wait_time / 60 if wait_time is not None else 0

    def is_server_full(self, websocket, options) -> bool:
        """
        Checks if the server is at its maximum client capacity and
        sends a wait message to the client if necessary.
        """
        if len(self.clients) >= self.max_clients:
            wait_time = self.get_wait_time()
            response = {"uid": options["uid"], "status": "WAIT", "message": wait_time}
            websocket.send(json.dumps(response))
            return True
        return False

    def is_client_timeout(self, websocket) -> bool:
        """
        Checks if a client has exceeded the maximum allowed connection time
        and disconnects them if so, issuing a warning.
        """
        elapsed_time = time.time() - self.start_times[websocket]
        if elapsed_time >= self.max_connection_time:
            self.clients[websocket].disconnect()
            logging.warning(
                f"Client with uid '{self.clients[websocket].client_uid}' disconnected due to overtime."
            )
            return True
        return False
