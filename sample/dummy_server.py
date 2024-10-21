
# server.py

import asyncio
import websockets
import json
import ssl
import pathlib

# ロボットごとの接続を管理するための辞書
connected_robots = {}

async def handle_connection(websocket, path):
    robot_name = path.strip('/').split('/')[-1]
    connected_robots[robot_name] = websocket
    print(f"Robot '{robot_name}' connected.")

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                await handle_binary_message(robot_name, message)
            else:
                await handle_text_message(robot_name, message)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Robot '{robot_name}' disconnected.")
    finally:
        del connected_robots[robot_name]

async def handle_text_message(robot_name, message):
    print(f"Received text message from {robot_name}: {message}")
    data = json.loads(message)
    msgtype = data.get('msgtype')

    # メッセージタイプに応じた処理を行う
    if msgtype == "INNITIAL_CONNECTION":
        await handle_initial_connection(robot_name, data)
    elif msgtype == "NAVIGATION_RESPONSE":
        await handle_navigation_response(robot_name, data)
    elif msgtype == "PARAM":
        await handle_param_response(robot_name, data)
    elif msgtype == "MESSAGE":
        await handle_message(robot_name, data)
    elif msgtype == "ROSBAG":
        await handle_rosbag_response(robot_name, data)
    else:
        print(f"Unknown msgtype '{msgtype}' from {robot_name}")

async def handle_binary_message(robot_name, message):
    print(f"Received binary message from {robot_name}")
    # バイナリメッセージの処理（ファイルの保存など）
    sections = message.split(b'\0')
    header = sections[0].decode('utf-8')
    type_, name = header.split(':')
    if type_ == 'param_data':
        # パラメータデータの処理
        param_data = sections[2]
        params = json.loads(param_data.decode('utf-8'))
        print(f"Received parameters from {robot_name}: {params}")
    else:
        # ファイルデータの保存
        additional_info = sections[1].decode('utf-8')
        data = sections[2]
        filename = f"{robot_name}_{name}"
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"Saved file '{filename}' from {robot_name}")

async def handle_initial_connection(robot_name, data):
    print(f"Handling initial connection from {robot_name}")
    # 必要な初期化処理を行う
    # ここでは特に何もしない

async def handle_navigation_response(robot_name, data):
    result = data.get('result')
    command_id = data.get('command_id')
    print(f"Navigation response from {robot_name}: result={result}, command_id={command_id}")

async def handle_param_response(robot_name, data):
    params = data.get('msg')
    print(f"Updated parameters from {robot_name}: {params}")

async def handle_message(robot_name, data):
    msg = data.get('msg')
    error = data.get('error')
    print(f"Message from {robot_name}: {msg} (Error: {error})")

async def handle_rosbag_response(robot_name, data):
    rosbag_list = data.get('msg')
    print(f"Received rosbag list from {robot_name}: {rosbag_list}")

async def send_command_to_robot(robot_name, command):
    websocket = connected_robots.get(robot_name)
    if websocket:
        await websocket.send(json.dumps(command))
        print(f"Sent command to {robot_name}: {command}")
    else:
        print(f"Robot '{robot_name}' is not connected.")

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    localhost_pem = pathlib.Path(__file__).with_name('dummy_ssl/cert.pem')
    ssl_context.load_cert_chain(localhost_pem)

    server = await websockets.serve(
        handle_connection, 'localhost', 5000, ssl=ssl_context
    )
    print("Server started at wss://localhost:5000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
