# dexnet/worker.py
import time
import json
import argparse
import logging
import asyncio
import aiohttp
import websockets

from uuid import uuid4

# Worker config
WSS_URI = "ws://127.0.0.1:9501"
CLIENT_TYPE = "worker"
DEVICE_ID = uuid4()
LOCAL_DEXTER_HOST = "127.0.0.1"
LOCAL_DEXTER_PORT = "9500"
DEFAULT_ERROR_RESPONSE = "Sorry, I seem to have encountered an error while doing some technical AI mumbo jumbo, so I didn't quite hear what you said. Could you say that again please?"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def get_llm_response(data: dict) -> dict:
    """
    Fetches a response from an LLM API.

    Args:
        prompt_api: The URL of the LLM API.
        session: The session data to send as JSON.

    Returns:
        The JSON response from the API, or None on error.
    """
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(
                f"http://{LOCAL_DEXTER_HOST}:{LOCAL_DEXTER_PORT}/llm",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"session": data}),
            ) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching LLM response: {e}")
        return {"response": DEFAULT_ERROR_RESPONSE}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return {"response": DEFAULT_ERROR_RESPONSE}


async def worker_work_request(websocket) -> dict | None:
    """
    Requests the connected api for work to do.

    Args:
        websocket: the ws/wss object for this instance.

    Returns:
        The response from the API, or None on error.
    """
    try:
        await websocket.send(
            json.dumps(
                {
                    "clientType": CLIENT_TYPE,
                    "deviceId": str(DEVICE_ID),
                }
            )
        )
        message = await websocket.recv()
        return message
    except Exception as e:
        logging.error(f"Failed to make a work request: {e}")
        return None


async def handle_work_load(websocket, message):
    """Handles messages received from the server."""
    try:
        data = json.loads(message)
        if data:
            logging.info(f"Received message from server: {data}")
        if data is None or "data" in data:
            return
        if (
            "clientType" in data
            and "deviceId" in data
            and "history" in data
            and "workerId" in data
            and "status" in data
        ):
            response = await get_llm_response(data)
            if "response" in response:
                response = response["response"]
            data["clientType"] = CLIENT_TYPE
            data["history"].append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )
            data["status"] = "done"
            await websocket.send(json.dumps(data))
            logging.info(f"Completed task for device: {data['deviceId']}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON received: {message}")
    except Exception as e:
        logging.error(f"Error handling message: {e}")


async def worker_socket_process():
    """maintains a constant connection to the central api."""
    while True:
        try:
            async with websockets.connect(WSS_URI) as websocket:
                while True:
                    message = await worker_work_request(websocket)
                    if message:
                        await handle_work_load(websocket, message)
                    else:
                        break
                    await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosedError:
            logging.error("Connection closed. Retrying...")
            time.sleep(10)
        except OSError as e:
            logging.error(f"OS Error: {e}. Retrying...")
            time.sleep(10)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}. Retrying...")
            time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wss_uri",
        type=str,
        default="ws://127.0.0.1:9501",
        help="Which host name to connect to.",
    )
    args = parser.parse_args()
    WSS_URI = args.wss_uri
    asyncio.run(worker_socket_process())
