import cv2
from flask import Flask, render_template, Response

app = Flask(__name__)

class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0) 
    def __del__(self):
        self.video.release()
    def Frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

def Generator(camera):
    while True:
        frame = camera.Frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/CameraFeed')
def CameraFeed():
    return Response(Generator(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')   

@app.route('/')
def CameraPage():
    return render_template('camera.html')
    
if __name__ == '__main__':
    pass
    #app.run(host='192.168.11.191', debug=True, port=200)
