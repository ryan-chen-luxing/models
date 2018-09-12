import youtube_dl
import json
import numpy as np
import cv2
import math
import object_detection_api
import tensorflow as tf




args = tf.app.flags.FLAGS
if __name__ == '__main__':
    tf.app.flags.DEFINE_string('filename', None, 'input video filename')
    tf.app.flags.DEFINE_float('scaleFactor', 1.0, 'used to re-scale the video before processing')
    tf.app.flags.DEFINE_float('width', -1, 'if scale the video to this width manually')
    tf.app.flags.DEFINE_float('detectThreshold', 0.5, 'threshold used in detecting objects')
    tf.app.flags.DEFINE_float('searchThreshold', 0.25, 'threshold used in searching objects being tracked')
    tf.app.flags.DEFINE_string('outputFilename', None, 'output filename of the json ')
    tf.app.flags.DEFINE_bool('disalbeDisplay', False, 'for console terminal')

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def rectArea(bbox):
    return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

def overlappingRect(bbox1, bbox2):
    left = max(bbox1[0], bbox2[0])
    top = max(bbox1[1], bbox2[1])
    right = min(bbox1[2], bbox2[2])
    bottom = min(bbox1[3], bbox2[3])
    return (left, top, right, bottom)

def searchObject(bbox, className, validTrackers, bboxesTracker, classNamesTracker, threshold=0.5):
    areaOverlappingPercentageBest = 0
    result = -1
    for i in range(0, len(validTrackers)):
        if validTrackers[i]:
            bboxTracker = bboxesTracker[i]
            classNameTracker = classNamesTracker[i]

            if className == classNameTracker:
                area1 = rectArea(bbox)
                area2 = rectArea(bboxTracker)

                overlappingBBox = overlappingRect(bbox, bboxTracker)
                areaOverlapping = rectArea(overlappingBBox)

                areaOverlappingPercentageAvg = (areaOverlapping / area1 + areaOverlapping / area2) * 0.5

                if areaOverlappingPercentageAvg > areaOverlappingPercentageBest and \
                    areaOverlappingPercentageAvg > threshold:
                    areaOverlappingPercentageBest = areaOverlappingPercentageAvg
                    result = i
    return result

def runObjectDetection(filename, scaleFactor, width, detectThreshold, searchThreshold, outputFilename, disalbeDisplay):
    cap = cv2.VideoCapture(filename)
    videoWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    videoHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frameRate = cap.get(cv2.CAP_PROP_FPS)

    if width > 0 and width < videoWidth:
        scaleFactor = float(width) / videoWidth

    resizeWidth = int(round(videoWidth * scaleFactor))
    resizeHeight = int(round(videoHeight * scaleFactor))

    if scaleFactor != 1.0:
      print('resize from [{}, {}] to [{}, {}]'.format(videoWidth, videoHeight, resizeWidth, resizeHeight))

    classificationInfo = []

    framesHavingHuman = []

    trackers = []
    bboxesTracker = []
    classNamesTracker = []
    lastDetectedFrame = []
    validTime = 1

    classesToTrack = ['person', 'pedestrian']

    trackerColor = [(255, 0, 0),
                    (0, 255, 0),
                    (0, 0, 255),
                    (255, 255, 0),
                    (0, 255, 255),
                    (255, 0, 255),
                    (255, 255, 255),
                    (128, 0, 0),
                    (0, 128, 0),
                    (0, 0, 128),
                    (128, 128, 0),
                    (0, 128, 128),
                    (128, 0, 128),
                    (128, 128, 128)]

    #resultObjectDetection.append(framesHavingHuman)


    while(cap.isOpened()):
        frameIndex = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        ret, frame = cap.read()

        if not ret:
            break

        if scaleFactor != 1.0:
            frame = cv2.resize(frame, dsize=(resizeWidth, resizeHeight))

        validTrackers = []
        for i in range(0, len(trackers)):
            if trackers[i] != None:
                validTrackers.append(True)
            else:
                validTrackers.append(False)

        for i in range(0, len(trackers)):
            if trackers[i] != None:
                if frameIndex - lastDetectedFrame[i] < frameRate * validTime:
                    success, rect = trackers[i].update(frame)
                    if success:
                        bboxesTracker[i] = (int(round(rect[0])),
                                            int(round(rect[1])),
                                            int(round(rect[0] + rect[2])),
                                            int(round(rect[1] + rect[3])))
                    else:
                        print('trackers[{}].update() failed'.format(i))
                        trackers[i] = None
                else:
                    validTrackers[i] = False
                    print('trackers[{}] expired'.format(i))

        objects = object_detection_api.get_objects(frame, detectThreshold)


        for object in objects:
            if object['class'] not in classesToTrack:
                continue

            x1 = int(round(object['x1'] * frame.shape[1]))
            y1 = int(round(object['y1'] * frame.shape[0]))
            x2 = int(round(object['x2'] * frame.shape[1]))
            y2 = int(round(object['y2'] * frame.shape[0]))

            objectId = searchObject((x1, y1, x2, y2), object['class'], validTrackers, bboxesTracker, classNamesTracker, searchThreshold)

            if objectId < 0:
                bboxesTracker.append((x1, y1, x2, y2))
                classNamesTracker.append(object['class'])
                lastDetectedFrame.append(frameIndex)

                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, (x1, y1, x2-x1, y2-y1))
                trackers.append(tracker)
                objectId = len(trackers) - 1
            else:
                validTrackers[objectId] = False
                lastDetectedFrame[objectId] = frameIndex

            object['id'] = objectId

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            #text = '{}, {}'.format(item['class'], int(round(item['score'] * 100)))
            #cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX,
            #            int(math.ceil(scaleFactor)), (255, 255, 255), int(math.ceil(scaleFactor * 1.0)), cv2.LINE_AA)

        for i in range(0, len(trackers)):
            if trackers[i] != None and frameIndex - lastDetectedFrame[i] < frameRate * validTime:
                bboxTracker = bboxesTracker[i]
                classNameTracker = classNamesTracker[i]
                color = trackerColor[i%len(trackerColor)]
                cv2.rectangle(frame, (bboxTracker[0], bboxTracker[1]), (bboxTracker[2], bboxTracker[3]), color, 2)
                text = '{}'.format(i)
                cv2.putText(frame, text, (bboxTracker[0], bboxTracker[1] + 25), cv2.FONT_HERSHEY_SIMPLEX,
                            int(math.ceil(scaleFactor)), color, int(math.ceil(scaleFactor * 2.0)), cv2.LINE_AA)

        persons = []
        for object in objects:
            if object['class'] in classesToTrack:
                object.pop('class', None)
                persons.append(object)

        for i in range(0, len(validTrackers)):
            if validTrackers[i]:
                persons.append(
                    {
                        'score': detectThreshold,
                        'x1': float(bboxesTracker[i][0]) / videoWidth,
                        'y1': float(bboxesTracker[i][1]) / videoHeight,
                        'x2': float(bboxesTracker[i][2]) / videoWidth,
                        'y2': float(bboxesTracker[i][3]) / videoHeight,
                        'id': i
                    }
                )

        if len(persons) > 0:
            framesHavingHuman.append(frameIndex)

        classificationInfo.append(
            {
                'frame': frameIndex,
                'persons': persons
            }
        )

        #classificationInfo.append(
        #    {
        #        'frame': frameIndex,
        #        'objects': objects
        #    }
        #)

        fontSize = math.ceil(float(resizeWidth) / 960)
        cv2.putText(frame, str(frameIndex), (fontSize * 25, fontSize * 25), cv2.FONT_HERSHEY_SIMPLEX, fontSize, (128, 128, 128), fontSize, cv2.LINE_AA)

        if not disalbeDisplay:
            cv2.imshow('frame', frame)
            cv2.waitKey(1)


    resultObjectDetection = {
        'framesPoseTracking': framesHavingHuman,
        'classificationInfo': classificationInfo
    }
    with open(outputFilename, 'w') as file:
        file.write(json.dumps(resultObjectDetection, cls=NumpyEncoder))

    cap.release()
    cv2.destroyAllWindows()



def main():
    filename = args.filename
    scaleFactor = args.scaleFactor
    width = args.width
    detectThreshold = args.detectThreshold
    searchThreshold = args.searchThreshold
    outputFilename = args.outputFilename
    disalbeDisplay = args.disalbeDisplay

    runObjectDetection(filename, scaleFactor, width, detectThreshold, searchThreshold, outputFilename, disalbeDisplay)


if __name__ == '__main__':
    main()