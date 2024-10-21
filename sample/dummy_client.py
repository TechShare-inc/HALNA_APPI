import asyncio
import websockets
import json
import ssl

async def on_message(websocket):
    async for message in websocket:
        if isinstance(message, bytes):
            await handle_binary_message(message)
        else:
            await handle_text_message(websocket, message)

async def handle_text_message(websocket, message):
    print(f"Received command: {message}")
    data = json.loads(message)
    # メッセージタイプに応じた処理を行う
    if 'navigation' in data:
        await handle_navigation_command(websocket, data['navigation'])
    elif 'cmd_vel' in data:
        await handle_cmd_vel_command(websocket, data['cmd_vel'])
    elif 'param' in data:
        await handle_param_command(websocket, data['param'])
    elif 'graph' in data:
        await handle_graph_command(websocket, data['graph'])
    elif 'rosbag' in data:
        await handle_rosbag_command(websocket, data['rosbag'])
    elif 'picture' in data:
        await handle_picture_command(websocket, data['picture'])
    elif 'process' in data:
        await handle_process_command(websocket, data['process'])
    else:
        print("Unknown command received")

async def handle_binary_message(message):
    print("Binary message received (not expected in client)")

async def handle_navigation_command(websocket, command):
    msg_type = command.get('msg_type')
    if msg_type == 'NAVIGATION':
        x = command.get('x')
        y = command.get('y')
        th = command.get('th')
        print(f"Navigating to ({x}, {y}, {th})")
        # ナビゲーション処理を模擬
        await asyncio.sleep(1)
        # 応答メッセージを送信
        response = {
            "sender": "robot1",
            "timestamp": "2023-10-21T12:00:00Z",
            "msgtype": "NAVIGATION_RESPONSE",
            "destination": command.get('sender'),
            "command_id": command.get('command_id'),
            "result": True
        }
        await websocket.send(json.dumps(response))
    # 他のナビゲーションタイプの処理も追加可能

async def handle_cmd_vel_command(websocket, command):
    linear_x = command.get('linear_x')
    linear_y = command.get('linear_y')
    angular_z = command.get('angular_z')
    print(f"Moving with linear_x={linear_x}, linear_y={linear_y}, angular_z={angular_z}")
    # 速度制御を模擬

async def handle_param_command(websocket, command):
    print(f"Updating parameters: {command}")
    # パラメータ更新を模擬
    # 更新後のパラメータをサーバーに送信
    response = {
        "sender": "robot1",
        "timestamp": "2023-10-21T12:00:00Z",
        "msgtype": "PARAM",
        "destination": command.get('sender'),
        "command_id": "0",
        "type": "updated_param",
        "msg": command  # 更新後のパラメータをそのまま返す
    }
    await websocket.send(json.dumps(response))

async def handle_graph_command(websocket, command):
    print(f"Graph command received: {command}")
    # グラフコマンドの処理を模擬

async def handle_rosbag_command(websocket, command):
    print(f"Rosbag command received: {command}")
    # ROSBagコマンドの処理を模擬
    if command.get('type') == 'get_rosbags':
        # ロスバグリストを返す
        response = {
            "sender": "robot1",
            "timestamp": "2023-10-21T12:00:00Z",
            "msgtype": "ROSBAG",
            "destination": command.get('sender'),
            "command_id": "0",
            "type": "rosbag_name_list",
            "msg": ["rosbag1.bag", "rosbag2.bag"]
        }
        await websocket.send(json.dumps(response))

async def handle_picture_command(websocket, command):
    print(f"Picture command received: {command}")
    # ピクチャーコマンドの処理を模擬
    # 応答メッセージを送信
    response = {
        "sender": "robot1",
        "timestamp": "2023-10-21T12:00:00Z",
        "msgtype": "MESSAGE",
        "destination": command.get('sender'),
        "command_id": "0",
        "msg": "Received all the patrol pictures",
        "error": False
    }
    await websocket.send(json.dumps(response))

async def handle_process_command(websocket, command):
    print(f"Process command received: {command}")
    # プロセスコマンドの処理を模擬
    # 応答メッセージを送信
    response = {
        "sender": "robot1",
        "timestamp": "2023-10-21T12:00:00Z",
        "msgtype": "MESSAGE",
        "destination": command.get('sender'),
        "command_id": "0",
        "msg": f"Process '{command.get('systemctl')}' executed",
        "error": False
    }
    await websocket.send(json.dumps(response))

async def send_initial_messages(websocket):
    # 初期接続メッセージを送信
    initial_message = {
        "sender": "robot1",
        "timestamp": "2023-10-21T12:00:00Z",
        "msgtype": "INNITIAL_CONNECTION",
        "destination": "server",
        "map_id": "map_001",
        "ip_address": "192.168.1.2",
        "building_number": 0,
        "floor_level": 0
    }
    await websocket.send(json.dumps(initial_message))

    # グラフデータの送信（バイナリメッセージ）
    header = "graph_data:original_graph_node.txt".encode('utf-8')
    map_name = "map_001".encode('utf-8')
    floor_name = "floor_0".encode('utf-8')
    graph_data = b"Sample graph data content"
    message = header + b'\0' + map_name + b'\0' + floor_name + b'\0' + graph_data
    await websocket.send(message)

    # パラメータデータの送信（バイナリメッセージ）
    header = "param_data:initial_param".encode('utf-8')
    params = {
        "map_id": "map_001",
        "minimum_height_for_conversion": 0.1,
        "maximum_height_for_conversion": 2.0,
        "robot_name": "robot1"
    }
    param_data = json.dumps(params).encode('utf-8')
    message = header + b'\0' + b'' + b'\0' + param_data
    await websocket.send(message)

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    uri = "wss://localhost:5000/sample/robot1/"

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        await send_initial_messages(websocket)
        await on_message(websocket)

if __name__ == "__main__":
    asyncio.run(main())
