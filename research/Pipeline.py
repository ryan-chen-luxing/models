import youtube_dl
import json
import os
import time
import sys
import tykoapi

def my_hook(d):
    if d['status'] == 'finished':
        videoId = os.path.splitext(os.path.split(d['filename'])[1])[0]

        t = time.clock()
        command = 'python ObjectDetectionModule.py'
        command += ' --filename "{}"'.format(d['filename'])
        command += ' --scaleFactor "{}"'.format(1.0)
        command += ' --width "{}"'.format(640)
        command += ' --disalbeDisplay "{}"'.format(1)
        command += ' --outputFilename "{}"'.format(videoId + '_objectDetection.json')

        os.system(command)
        print('object detection time elapsed: {} seconds'.format(time.clock() - t))

        t = time.clock()
        command = '/home/ubuntu/openpose/build/examples/openpose/openpose.bin'
        command += ' --video "{}"'.format(d['filename'])
        command += ' --youtubeId "{}"'.format(videoId)
        #command += ' --visualizeKeyframes {}'.format(0)
        command += ' --render_pose {}'.format(0)
        command += ' --display {}'.format(0)
        command += ' --model_pose {}'.format("COCO")

        os.system(command)
        print('pose tracking time elapsed: {} seconds'.format(time.clock() - t))

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
    process(
        "b9OlwQEnncs"
    )