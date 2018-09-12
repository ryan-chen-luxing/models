import youtube_dl
import json
import os
import time
import sys
import cv2
import argparse
#import tykoapi

skipObjectDetection = False

def my_hook(d):
    if d['status'] == 'finished':
        videoId = os.path.splitext(os.path.split(d['filename'])[1])[0]

        video = cv2.VideoCapture(d['filename'])
        videoWidth = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        videoHeight = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frameRate = video.get(cv2.CAP_PROP_FPS)
        frameCount = video.get(cv2.CAP_PROP_FRAME_COUNT)
        print('video fps={}, frameCount={}, width={}, height={}'.format(
            int(frameRate), int(frameCount), int(videoWidth), int(videoHeight)))

        if not skipObjectDetection:
          t = time.time()
          command = 'python ObjectDetectionModule.py'
          command += ' --filename "{}"'.format(d['filename'])
          command += ' --scaleFactor "{}"'.format(1.0)
          command += ' --width "{}"'.format(640)
          command += ' --disalbeDisplay "{}"'.format(1)
          command += ' --outputFilename "{}"'.format(videoId + '_objectDetection.json')

          os.system(command)
          elapsed = time.time() - t
          print('object detection time elapsed: {} seconds, fps={}'.format(elapsed, frameCount / elapsed))

        t = time.time()
        command = '/home/ubuntu/openpose/build/examples/openpose/openpose.bin'
        command += ' --video "{}"'.format(d['filename'])
        command += ' --youtubeId "{}"'.format(videoId)
        #command += ' --visualizeKeyframes {}'.format(0)
        command += ' --render_pose {}'.format(0)
        command += ' --display {}'.format(0)
        #command += ' --model_pose {}'.format("COCO")
        
        if not skipObjectDetection:
            command += ' --inputObjectDetection "{}"'.format(1)

        os.system(command)
        elapsed = time.time() - t
        print('pose tracking time elapsed: {} seconds, fps={}'.format(elapsed, frameCount / elapsed))

def process(id):
    ydl = youtube_dl.YoutubeDL(
        {
            'outtmpl': '%(id)s.%(ext)s',
            'format': 'bestvideo',
            'progress_hooks': [my_hook],
        })

    with ydl:
        url = "https://www.youtube.com/watch?v=" + id
        result = ydl.extract_info(url)

        visualJson = json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))
        with open('{}.txt'.format(result['id']), 'w') as file:
            file.write(visualJson)


if __name__ == '__main__':
    #BaseUrl = "http://localhost:55613/"
    #OAuthUsername = "cqX5kBK1TkG8w8zKeW"
    #VerifySslCert = True
    #tyko = tykoapi.TykoApi(BaseUrl, OAuthUsername, VerifySslCert)

    parser = argparse.ArgumentParser()
    parser.add_argument("--skipObjectDetection", help="Whether to run objection detection module or not", action="store_true")
    args = parser.parse_args()

    skipObjectDetection = args.skipObjectDetection
    
    process(
        "b9OlwQEnncs"
    )