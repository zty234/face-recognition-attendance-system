import cv2
import numpy as np
from recognition.recognition import face_match
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class FaceRecognitionConsumer(AsyncWebsocketConsumer):
    # connect
    async def connect(self):
        await self.accept()
        print("Successfully Connect!")
    
    # disconnect
    async def disconnect(self, close_code):
        print("Diconnected")
    
    # receive
    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:

            # 转np array
            img_array = np.frombuffer(bytes_data, dtype=np.uint8)

            # 转三通道
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

           
            if frame is None:
                await self.send(text_data=json.dumps({"error":"Cannot decode image data"}))
                return

            # 调用face_match 异步处理防止阻塞
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, face_match, frame)

            await self.send(text_data=json.dumps({"faces": results}))
        
        else:
            await self.send(text_data=json.dumps({"error":"No image data"}))
