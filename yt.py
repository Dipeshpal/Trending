import json
import pandas as pd
import csv
from apiclient.discovery import build
import requests
from datetime import datetime
from tqdm import tqdm

DEBUG = False

LOGS = []


def print_console(lines):
    LOGS.append(lines)
    if DEBUG:
        print_console(lines)


class Youtube_API:
    def __init__(self):
        file_name = "key.json"

        with open(file_name) as file:
            data = json.load(file)

            self.key = data['key']

        self.youtube = build('youtube', 'v3', developerKey=self.key)

    def get_channel_videos(self, channel_id=None, channel_name=None):
        if channel_id is None:
            url = f'https://www.youtube.com/c/{channel_name}'

            r = requests.get(url).text
            a = r.find('externalId') + len('externalId') + 3
            b = r.find('"keywords":"') - 2
            channel_id = r[a:b]
            print_console(f"Channel_id for {channel_name} is {channel_id}")
        res = self.youtube.channels().list(id=channel_id,
                                           part='contentDetails').execute()

        playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        next_page_token = None

        while 1:
            res = self.youtube.playlistItems().list(playlistId=playlist_id,
                                                    part='snippet',
                                                    maxResults=2,
                                                    pageToken=next_page_token).execute()
            videos += res['items']
            next_page_token = res.get('nextPageToken')

            if next_page_token is None:
                break

        return videos

    def filter_latest_videos(self, videos, published_in_last_days=7):
        latest_videos = []
        for i in videos:
            published_date = i['snippet']['publishedAt'][:10]
            published_date = datetime.strptime(published_date, '%Y-%m-%d')
            today = datetime.today()
            if (today - published_date).days < published_in_last_days:
                latest_videos.append(i)
        return latest_videos

    def get_views(self, video_id):
        res = self.youtube.videos().list(id=video_id,
                                         part='statistics').execute()
        return res['items'][0]['statistics']['viewCount']

    def filter_relevant_videos(self, latest_videos):
        relevant_videos = []
        for i in latest_videos:
            title = i['snippet']['title']
            link = f"https://www.youtube.com/watch?v={i['snippet']['resourceId']['videoId']}"
            publishedAt = i['snippet']['publishedAt']
            description = i['snippet']['description']
            viewCount = self.get_views(i['snippet']['resourceId']['videoId'])
            relevant_videos.append((publishedAt, title, viewCount, link, description))
        return relevant_videos

    def make_csv(self, relevant_videos):
        date = datetime.today().strftime('%Y-%m-%d')
        with open(f'videos_{date}.csv', 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Published At', 'Title', 'Views', 'Link', 'Description'])
            writer.writerows(relevant_videos)

        df = pd.read_csv(f'videos_{date}.csv')
        # remove empty rows
        df = df.dropna()
        df.to_csv(f'videos_{date}.csv', index=False)


def start():
    obj = Youtube_API()
    channel_name = ['TechPortOfficial', 'UtsavTechie', 'MrTechpedia', 'sambeckman', 'VenomsTech',
                    'UnusualHacker2', 'TechOnTrend', 'TECHUM', 'TechnicalDrops', 'TipTopTech', 'TechFire1998']

    data = []
    for channel in tqdm(channel_name):
        # videos = obj.get_channel_videos(channel_id='UCGEoRAK92fUk2kY3kSJMR_Q')
        videos = obj.get_channel_videos(channel_name=channel)
        print_console(f"{channel_name} has {len(videos)} videos")

        print_console("Filtering latest videos...")
        latest_videos = obj.filter_latest_videos(videos, published_in_last_days=30)
        print_console(f"{len(latest_videos)} uploaded videos in last 30 days")

        relevant_videos = obj.filter_relevant_videos(latest_videos)
        print_console(f"{len(relevant_videos)} relevant videos")

        data += relevant_videos

    print_console("Creating CSV file...")
    obj.make_csv(data)
    print_console("CSV file created")

    print(LOGS)


if __name__ == '__main__':
    start()
