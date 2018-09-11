import youtube_dl
import json
import os
import sys
#import tykoapi

def my_hook(d):
    if d['status'] == 'finished':
        videoId = os.path.splitext(os.path.split(d['filename'])[1])[0]

        command = 'python ObjectDetectionModule.py'
        command += ' --filename "{}"'.format(d['filename'])
        command += ' --scaleFactor "{}"'.format(1.0)
        command += ' --width "{}"'.format(640)
        command += ' --outputFilename "{}"'.format(videoId + '_ObjectDetection.json')

        os.system(command)


        #command = 'C:/Projects/LENS-Web-Platform/Lens.Tensorflow/openpose/openpose/build/bin/OpenPoseDemo.exe'
        #command += ' --video "{}"'.format(d['filename'])
        #command += ' --write_json "{}_PoseTracking.json"'.format(videoId)
        #command += ' --face --hand'
        #command += ' --videoInfo "{}_ObjectDetection.json"'.format(videoId)

        os.system(command)

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
        "99iwy9BafZ0"
        # "0Yly7UieTFM"
        # "WF-OHqZRxdg"
        # "mg6-SnUl0A0",
        #  "gk0nVMU76bc"
        # "VzCO1xnLE04"
        # "AVxF1nul4UM"
        # "JZqJulltwZY"
        # "f-wv6PAwx3U",
        # "6ia8dZnUh-M",
        # "TWxrIblJHO0"
        # "Fg2STFkmZuw"
        # "s7CNxkZz5qg"
        # "TcQ3HT8tH20",
        # 'Z6qWTegXdPk',
        # 'cSp1dM2Vj48',
        # 'KrTFD21ZnFI',
        # 'b9OlwQEnncs',
        # 'r7HlpDtXN8A',
        # 'MJHTQncT-AA',
        # 'YUdOIOINhIY',
        # 'mTMgIViinuQ',
        # 'McHeOQIAUGU',
        # 'ERuFW7q_OWw',
        # '79FMM1g7R20',
        # 'https://www.youtube.com/watch?v=RAytWG1RBRw',
        # 'https://www.youtube.com/watch?v=W_B2UZ_ZoxU',
        # 'https://www.youtube.com/watch?v=EUHcNeg_e9g',
        # 'https://www.youtube.com/watch?v=4JeiUDkpwSc',
        # 'https://www.youtube.com/watch?v=lOQBcP1M6sc',
        # 'https://www.youtube.com/watch?v=ig66GiwxAGA',
        # 'https://www.youtube.com/watch?v=D367RbvXBn4', this one has error
        # 'https://www.youtube.com/watch?v=hFceVEZ0dhk',
        # 'https://www.youtube.com/watch?v=V1HyH4dsHMM',
        # 'https://www.youtube.com/watch?v=H0_VRfPIWoI',
    )