import multiprocessing.dummy
import sys
import warnings
from pathlib import Path
import time
import os
import pandas as pd
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL
from channel_search import ChannelSearch

warnings.filterwarnings('ignore')
download_videos = False

NUMS = 100  # maximal items you can download
iMaxDuration = 1200# maximal duration in seconds
iMinDuration = 600
YL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
    # 'proxy':'socks5://127.0.0.1:10808'
}
YDL_OPTIONS_EXTRACT = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
    # 'proxy':'socks5://127.0.0.1:10808'
    #"age-limit":12,
}


YDL_OPTIONS_AUDIO_ONLY = {
    'format': 'bestaudio[ext=m4a]',
}



def download(index):
    print("index", index)
    arg, title, folder, animal = download_information[index]

    path = Path(folder) / animal.split("/")[0]
    path.mkdir(exist_ok=True, parents=True)

    YL_OPTIONS['outtmpl'] = str(path / (arg + ".mp4"))
    with YoutubeDL(YL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
            YDL_OPTIONS_AUDIO_ONLY['outtmpl'] = str(path / ( arg + ".m4a"))
            with YoutubeDL(YDL_OPTIONS_AUDIO_ONLY) as ydl_audio:
                audio = ydl_audio.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
                return True
        except Exception:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=False)
            return False


def mut_download(folder, animals):
    download_information = []
    proxy = 'socks5://127.0.0.1:10808'
    os.environ['HTTP_PROXY']=proxy
    os.environ['HTTPS_PROXY']=proxy
    for animal in animals.split("/"):
        for channel in channels:
            s=ChannelSearch(animal,channel)
            while 1:
                flag=s.next()
                result=s.result(mode = 1)
                for info in result['result']:
                    id=info['id']
                    title=info['title']
                    description=info['description']
                    url=info['url']
                    times=info['duration']
                    #if animal.lower() in title.lower() or animal.lower() in description.lower():
                    # if 1:
                    download_information.append([id, title, folder, animal])
                if flag==True or s.continuationKey==None:
                    break
                time.sleep(5)
    print("the number of download inforamtion", len(download_information))
    return download_information

#每个频道都有个ID
channels=['UCDPk9MG2RexnOMGTD-YnSnA','UCwmZiChSryoWQCZMIQezgTg','UCa_VZIyozQ00fxPtmoVJk-A','UC-Uh0-0dEQV8a-SPrx50zmw',
          'UCTKGGi6PHFWSW6tllNZcKRw','UCJtGZ0fUOkh_MmFXix45DPA','UCo9R7UZjH3FPOysc5_uVbKQ','UCUvT5_2eXhGgUD7QZ-pVa4g',
          'UCbq-4OJxnziD3awH-aTezeA','UCyfZleh4w7buTzi0WfY8WqA','UC4tIX3IbVzdNEnuaWBNTVzA','UCQtW2oz8ec8pHjjxawujNjg']

#nat geo wild,bbc earth,wild animals planet,africa adventures
#Big Animals,Survival Animals,Animal Africa,ND Channel
#Real Wild,Latest Sightings,King of Beasts,Free Documentary - Nature

CPU = 10

folder, animal_name = "".join(sys.argv[1:]).split("||")
print(folder)
print(animal_name)
download_information = mut_download(folder, animal_name)

print(download_information)
num_videos = len(download_information)
video_index = [i for i in range(0, num_videos)]
print(video_index)
print("the number of videos", num_videos)

if download_videos:
    with multiprocessing.dummy.Pool(CPU) as pool:       
        pool.map(download, video_index)


