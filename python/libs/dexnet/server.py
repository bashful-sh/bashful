# dexnet/server.py
import time
import json
import redis
import logging
import asyncio
import websockets

# Server Host
SERVER_PROTOCOL = "ws"
SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 9501

# Redis connection details
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


async def handle_user_request(websocket, data: dict) -> None:
    """
    validates a user request object and caches valid requests.

    requests then wait for a worker to be assigned to them.
    """
    if "deviceId" in data and "history" not in data:
        redis_key = "dexnet-request-" + str(data["deviceId"])
        r = redis_client.get(redis_key)
        r = json.loads(r)
        if "status" in r and r["status"] == "done":
            await websocket.send(json.dumps(r))
    elif "deviceId" in data and "history" in data:
        redis_key = "dexnet-request-" + str(data["deviceId"])
        r = redis_client.get(redis_key)
        if r:
            r = json.loads(r)
            if r["workerId"] is not None:
                logging.info(
                    f"Did not cache user client request because previous request is being processed: {redis_key}"
                )
                return
        if len(data["history"]) > 0:
            if "role" in data["history"][-1] and data["history"][-1]["role"] == "user":
                data["timestamp"] = time.time()
                data["workerId"] = None
                data["status"] = "waiting"
                redis_client.set(redis_key, json.dumps(data), ex=600)
                logging.info(f"Cached a user client request: {redis_key}")
            else:
                logging.info(f"Client sent request without new user input: {data}")
        else:
            logging.info(f"Client sent request without history: {data}")
    else:
        logging.info(f"Client sent request without a deviceId: {data}")


async def purge_bad_redis_key_value_pair(key: bytes | str) -> None:
    """
    called when a bad redis key/value pair is discovered.

    deletes the key/value pair immediately.
    """
    logging.info(f"Found a bad dexnet-request key/value: {key}")
    redis_client.delete(key)
    logging.info(f"Deleted a bad dexnet-request key/value: {key}")


async def handle_worker_request(websocket, data: dict) -> None:
    """
    if the data request is for a completed work load, cache the new session data.

    otherwise get the oldest request without an assigned worker from the cache and
    return it to the worker for processing.

    while scanning for a request to assign, cleans bad requests that it
    comes across.
    """
    if (
        "deviceId" not in data
        or "clientType" not in data
        or data["clientType"] != "worker"
    ):
        logging.info(f"Received invalid worker request: {data}")
        return

    if (
        "clientType" in data
        and "deviceId" in data
        and "history" in data
        and "workerId" in data
        and "status" in data
    ):
        logging.info(
            f"Received submission from worker ({data['workerId']}) for user ({data['deviceId']}): {data}"
        )
        data["clientType"] = "user"
        data["workerId"] = None
        data["status"] = "done"
        redis_key = "dexnet-request-" + str(data["deviceId"])
        redis_client.set(redis_key, json.dumps(data), ex=600)
        await websocket.send(json.dumps({"data": "successful data submission."}))
        return

    request_keys = redis_client.keys("dexnet-request-*")
    if not request_keys or not isinstance(request_keys, list):
        await websocket.send(json.dumps({"data": "no task available."}))
        return

    oldest_req_without_assigned_worker: dict | None = None
    oldest_key_without_assigned_worker: str | None = None
    for k in request_keys:
        r = redis_client.get(k)
        if r:
            try:
                r = json.loads(r)
            except Exception:
                await purge_bad_redis_key_value_pair(k)
                continue
        else:
            await purge_bad_redis_key_value_pair(k)
            continue
        # If the key results in a bad request
        if (
            not r
            or not isinstance(r, dict)
            or "deviceId" not in r
            or "history" not in r
            or "status" not in r
            or "timestamp" not in r
            or "workerId" not in r
            or not len(r["history"]) > 0
            or "role" not in r["history"][-1]
            or "content" not in r["history"][-1]
        ):
            await purge_bad_redis_key_value_pair(k)
            continue
        # If the key results in a request that already has an assigned worker
        if r["workerId"] is not None:
            continue
        elif r["status"] != "waiting":
            continue
        # If the key results in a request that has no assigned worker
        elif (
            oldest_req_without_assigned_worker is None
            or oldest_req_without_assigned_worker["timestamp"] > r["timestamp"]
        ):
            oldest_key_without_assigned_worker = "dexnet-request-" + str(r["deviceId"])
            oldest_req_without_assigned_worker = r
            continue

    # If no request without an assigned worker was found
    if oldest_key_without_assigned_worker is None:
        await websocket.send(
            json.dumps({"data": "no task without an assigned worker available."})
        )
        return

    # If the oldest request without an assigned worker was found
    if (
        oldest_key_without_assigned_worker is not None
        and oldest_req_without_assigned_worker is not None
    ):
        logging.info(
            f"Discovered oldest request without an assigned worker: {oldest_key_without_assigned_worker}"
        )
        oldest_req_without_assigned_worker["workerId"] = data["deviceId"]
        oldest_req_without_assigned_worker["status"] = "processing"

        json_dump = json.dumps(oldest_req_without_assigned_worker)
        redis_client.set(
            "dexnet-request-" + str(oldest_req_without_assigned_worker["deviceId"]),
            json_dump,
            ex=600,
        )

        logging.info(
            f"Assigned request ({oldest_key_without_assigned_worker}) to worker: {data['deviceId']}"
        )

        await websocket.send(json_dump)

        logging.info(
            f"Sent request ({oldest_key_without_assigned_worker}) to worker: {data['deviceId']}"
        )
        return


async def handle_unknown_request(client_address, message) -> None:
    """logs an error whenever an unknown request type is received."""
    logging.info(f"Received a bad request from {client_address}: {message}")


async def handler(websocket):
    client_address = websocket.remote_address
    logging.info(f"Client connected: {client_address}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if "keepAlive" in data:
                    continue
                elif "clientType" in data and data["clientType"] == "user":
                    await handle_user_request(websocket, data)
                elif "clientType" in data and data["clientType"] == "worker":
                    await handle_worker_request(websocket, data)
                else:
                    await handle_unknown_request(client_address, message)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON received from {client_address}: {message}")

            except redis.exceptions.ConnectionError as e:
                logging.error(f"Redis connection error: {e}")

            except Exception as e:
                logging.exception(f"An unexpected server error occured: {e}")

    except websockets.ConnectionClosed:
        logging.info(f"Client disconnected: {client_address}")


async def main():
    async with websockets.serve(handler, SERVER_HOSTNAME, SERVER_PORT):
        logging.info(
            f"WebSocket server started on {SERVER_PROTOCOL}://{SERVER_HOSTNAME}:{SERVER_PORT}"
        )
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
