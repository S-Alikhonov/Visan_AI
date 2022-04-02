import cv2
import numpy as np

import copy
import requests
import uuid
from time import time
from datetime import datetime,timedelta
from track.deep_sort.deep_sort import DeepSort
import random
model_config = 'src/yolov3.cfg'
model_weights = 'src/yolov3.weights'
BASE_URL = 'http://localhost:5000/'

class ObjectDetector():
    def __init__(self):
        net = cv2.dnn.readNet(model_config,model_weights)
        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(416,416),scale=1/255)
        self.classes_allowed = [0]
        
    def detect(self,img):
        bboxes = []
        confs = []
        class_ids,scores,boxes = self.model.detect(img,nmsThreshold=0.4)
        for class_id, score,box in zip(class_ids,scores,boxes):
            if score < 0.3:
                continue
            
            if class_id in self.classes_allowed:
                x,y,w,h = [a for a in box]
                box = [x,y,w,h]
                bboxes.append(box)
                confs.append(score)
        return bboxes,confs



#draw poly on roi
def draw_roi(pts,color,frame):
    alpha = 0.95
    #create overlay
    overlay = np.zeros_like(frame,np.uint8)
    #draw
    cv2.fillPoly(overlay,pts,color)
    mask = overlay.copy().astype(bool)
    frame[mask] = cv2.addWeighted(frame, alpha, overlay, 1 - alpha, 0)[mask]
    cv2.polylines(frame,pts,True,(122,34,25),1)
    return frame

def heatmap(background_subtractor,raw_frame,frame,accum_image):
    filter = background_subtractor.apply(raw_frame)  # remove the background
    threshold = 2
    maxValue = 2
    ret, th1 = cv2.threshold(filter, threshold, maxValue, cv2.THRESH_BINARY)
    # add to the accumulated image
    accum_image = cv2.add(accum_image, th1)
    color_image = cv2.applyColorMap(accum_image, cv2.COLORMAP_JET)
    result_overlay = cv2.addWeighted(frame, 0.8, color_image, 0.6, 0)
        
    return background_subtractor,accum_image,result_overlay
        
        
def api_sender(heatmap,count):
    heatmap_file_name = 'result.jpg'
    cv2.imwrite(heatmap_file_name,heatmap)
    data = {
        'heatmap':heatmap_file_name,
        'count': len(count)
    }
    req = requests.post(BASE_URL+'api/bc0f5afc-9846-4eb8-853a-0ed9716fcf34',data=data,files={"media":open(heatmap_file_name,'rb')})
    print(req.json())
    
def callbacking(event,x,y,flags,param):
    img = copy.deepcopy(image)
    if event == cv2.EVENT_LBUTTONDOWN:
        roi.append((x,y))
    if event == cv2.EVENT_RBUTTONDOWN:
        roi.pop()
    

def draw(img,x1,y1,x2,y2,people_count,id,colors):
    r=int(0.1*(x2-x1))
    d=2*r
    thickness=3
    color = colors[id,:].tolist()
    # cv2.rectangle(img,(x1,y1),(x2,y2),color,1)
    cv2.putText(img,str(id),(x1,y1),cv2.FONT_HERSHEY_SIMPLEX,1,color,3)
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
    cv2.putText(img,f'people count:{len(people_count)}',(30,45),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,0),2)
    return img

def run_tracker(video_path='src/test.mp4'):
    
    detector = ObjectDetector()
    tracker = DeepSort()
    background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
    
    
    global image
    global roi
    roi = []
    tracked = []
    people_count= []
    is_first=True
    time_to_send = datetime.now()
    colors = np.random.randint(0,256,size=(100,3))
    #roi selection
    image = cv2.imread('file.jpg')
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', callbacking)
    
    
    while True:
        cap = cv2.VideoCapture(video_path)
        ret,image = cap.read()
        if len(roi)>0:
            cv2.circle(image,roi[-1],3,(0,0,255),-1)
        if len(roi)>1:
            for i in range(len(roi)-1):
                cv2.circle(image,roi[i],5,(0,0,255),-1)
                cv2.line(image,roi[i],roi[i+1],(255,0,0),2)
        cv2.imshow('image',image)
        key = cv2.waitKey(1) & 0xFF
        if key == 83 or key== 115:
            break
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    roi = np.array([roi],np.int32)
    
    #actual tracking loop
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)
    result = cv2.VideoWriter('filename.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         10, size)
    if not cap.isOpened():
        print('there is a error openning the video file')
    else:
        ret,frame = cap.read()
        cv2.imwrite('file.jpg',frame)
        while cap.isOpened():
            ret,frame = cap.read()
            
            if ret :
                if is_first:
                    is_first= False
                    height, width = frame.shape[:2]
                    print(height,width)
                    accum_image = np.zeros((height, width), np.uint8)
                #detecting people
                bboxes,confs = detector.detect(frame)
                tracked_people = tracker.update(bboxes,confs,frame)
                raw_frame = copy.deepcopy(frame)
                for person in tracked_people:
                    x1,y1,x2,y2,id = [int(a) for a in person]
                    #checking if person crossed roi
                    c = [(x1+x2)//2,(y1+y2)//2]
                    crossed = cv2.pointPolygonTest(roi,c,False)
                    if crossed==1 and id not in people_count:
                        people_count.append(id)
                    frame = draw(frame,x1,y1,x2,y2,people_count,id,colors)
                    frame = draw_roi(roi,(135,0,255),frame)
                background_subtractor,accum_image,frame_2_send = heatmap(background_subtractor,raw_frame,frame,accum_image)
                cv2.imshow('video',frame)
                result.write(frame)
                # if time_to_send.hour == datetime.now().hour:
                #     api_sender(frame_2_send,people_count)
                #     time_to_send += timedelta(hours=1)
                #     people_count = []
                #     print(f'time to send : {time_to_send}')
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else :
                break
        first = cv2.imread('file.jpg')
        background_subtractor,accum_image,first = heatmap(background_subtractor,raw_frame,first,accum_image)
        api_sender(first,people_count)
        cap.release()
        result.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        
            
                    
                