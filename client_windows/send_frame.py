# client_windows/send_frame
# 把windows摄像头识别的图片通过Websocket传给wsl Ubuntu Django

import cv2
import requests
import time
import websockets
import asyncio
import json

SERVER_URL_FLASK = "http://localhost:5000/recognize"  # Flask http-service address
SERVER_URL_WEBSOCKET = "ws://172.26.162.178:8000/ws/recognize_face/" # Django websocket-service address

# 绘制人脸框和人名框
def draw_rectangle(frame, results):
    for face in results:
        top, right, bottom, left = face["top"], face["right"], face["bottom"], face["left"]
        name = face["name"]
        status = face["status"]

        # 绘制人脸框
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

        # 绘制名字框
        cv2.rectangle(frame, (left, bottom+5), (right, bottom+35), (0, 0, 255), 3)

        # 绘制名字
        cv2.putText(frame, name, (left+10, bottom+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        
        if name != "Unknown":
            # 绘制成功签到
            str = status
            cv2.putText(frame, str, (left+5, bottom+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

async def send_and_receive():
    # 开摄像头
    cap = cv2.VideoCapture(0)
    try:
        async with websockets.connect(uri=SERVER_URL_WEBSOCKET, max_size=None) as websocket:

            while True:
                # 取frame
                ret, frame = cap.read()

                # 判断是否打开摄像头
                if not ret:
                    print("Cannot Open camera")
                    break

                # frame转图片jpg格式
                _, img_encodes = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                # jpg转bytes
                img_bytes = img_encodes.tobytes()
                
                try:
                    # 发送post请求
                    # response = requests.post(SERVER_URL_DJANGO, files={"image": img_bytes})
                    
                    # 发送二进制数据通过websocket
                    await websocket.send(img_bytes)  # 自动触发face_sockets中的receive

                    response = await websocket.recv() # 自动触发self.send
                    response_data = json.loads(response)

                    # 根据response中的类型判断
                    if 'faces' in response_data:
                        results = response_data['faces']
                        draw_rectangle(frame, results)

                    elif 'error' in response_data:
                        print("Service error:", response_data['error'])

                    # 显示窗口
                    cv2.imshow("Camera", frame)
                    if cv2.waitKey(30) & 0xFF == ord('q'):
                        break

                except Exception as e:
                    print("Fail to send or receive:", e)
                    break
    finally:                
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(send_and_receive())