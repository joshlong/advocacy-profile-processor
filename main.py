import dataclasses
import datetime
import json
import os
import re
import sys
import time
import typing

import requests


@dataclasses.dataclass
class Appearance(object):
    appearance: str
    location: str
    start_date: str
    end_date: str
    time: str
    location_address: str
    marketing_blurb: str
    date: datetime.datetime


@dataclasses.dataclass
class Podcast(object):
    id: str
    uid: str
    title: str
    date: datetime.datetime
    episode_photo_uri: str
    description: str
    episode_uri: str


@dataclasses.dataclass
class Video(object):
    blog_url: str
    date: datetime.datetime
    season_number: int
    title: str
    youtube_embed_url: str
    youtube_id: str


def replace_fragment(source_markup: str, fragment_name: str, replacement: str) -> str:
    start_pattern = re.compile(r""" <!--\s*START:%s\s*--> """.strip() % fragment_name, re.MULTILINE | re.IGNORECASE)
    start_match = start_pattern.findall(source_markup)[0]
    stop_pattern = re.compile(r""" <!--\s*STOP:%s\s*--> """.strip() % fragment_name, re.MULTILINE | re.IGNORECASE)
    stop_match = stop_pattern.findall(source_markup)[0]
    start_fragment_offset = source_markup.find(start_match) + len(start_match)
    stop_fragment_inset = source_markup.find(stop_match)
    begin = source_markup[0:start_fragment_offset]
    end = source_markup[stop_fragment_inset:]
    return ''.join([begin, replacement, end])


def load_json_from_network(url: str) -> typing.Dict:
    return json.loads(requests.get(url).text)


## todo
@dataclasses.dataclass
class Blog(object):
    pass


def fetch_spring_io_blogs() -> typing.List[Blog]:
    '''
    this function should pull down the N latest blogs i've published.
    :return:
    '''
    blogs = requests.get('https://spring.io/blog.atom').text
    return []


##

def fetch_appearances() -> typing.List[Appearance]:
    appearances = load_json_from_network('http://joshlong.com/appearances.json')
    results = []

    def key_for(a: typing.Dict, key: str) -> typing.Any:
        if key in a.keys():
            return a[key]
        return None

    for a in appearances:
        start_date = a['start_date']
        m, d, y = [int(x) for x in start_date.split('/')]
        date: datetime.datetime = datetime.datetime(y, m, d)
        results.append(Appearance(
            key_for(a, 'appearance'),
            key_for(a, 'location'),
            key_for(a, 'start_date'),
            key_for(a, 'end_date'),
            key_for(a, 'time'),
            key_for(a, 'location_address'),
            key_for(a, 'marketing_blurb'),
            date
        ))

    return results


def fetch_spring_tips_videos() -> typing.List[Video]:
    result = []
    videos = load_json_from_network('https://springtipslive.io/episodes.json')
    for v in videos:
        date = datetime.datetime.fromisoformat(v['date'])
        result.append(
            Video(v['blog_url'], date, int(v['season_number']), v['title'], v['youtube_embed_url'], v['youtube_id']))
    return result


def fetch_bootiful_podcasts() -> typing.List[Podcast]:
    podcasts = load_json_from_network('http://bootifulpodcast.fm/podcasts.json')
    results = []
    for p in podcasts:
        # ts = int(p['date']) / 1000
        # date = datetime.datetime.fromtimestamp(ts)
        # date = datetime.datetime(date.year, date.month, date.day)
        keys = ['dataAndTime', 'dateAndTime']
        date: typing.Union[str, None] = None
        for k in keys:
            if k in p:
                date = p[k]
        m, d, y = [int(x) for x in date.split('/')]
        date: datetime.datetime = datetime.datetime(y, m, d)
        results.append(Podcast(p['id'], p['uid'], p['title'], date, p['episodeUri'], p['description'], p['episodeUri']))
    return results


# TODO interleave the markup into the joshlong.md in the Tanzu tuesday git clone

def main(_: typing.List[str]):
    profile_page: str = os.environ['PROFILE_PAGE']
    assert profile_page is not None, 'the PROFILE_PAGE environment variable must be set'

    def build_date_string(d: datetime.datetime) -> str:
        return d.isoformat().split('T')[0]

    def appearance_markdown_line(appearance: Appearance) -> str:
        return '*%s* - %s' % (build_date_string(appearance.date), appearance.marketing_blurb)

    def podcast_markdown_line(podcast: Podcast) -> str:
        return """[(%s) %s](%s) """ % (build_date_string(podcast.date),
                                       podcast.title,
                                       podcast.episode_uri
                                       )

    def video_markdown_line(video: Video) -> str:
        return """[(%s) %s](%s) """ % (build_date_string(video.date),
                                       video.title, 'https://www.youtube.com/watch?v=%s' % video.youtube_id)

    def record_date_key(record: typing.Union[typing.Union[Video, Podcast], Appearance]) -> float:
        return time.mktime(record.date.timetuple())

    appearances: typing.List[Appearance] = sorted(fetch_appearances(), key=record_date_key, reverse=True)
    appearances_markup = os.linesep.join(['* %s' % appearance_markdown_line(a) for a in appearances])

    podcasts: typing.List[Podcast] = sorted(fetch_bootiful_podcasts(), key=record_date_key, reverse=True)
    podcasts_markup = os.linesep.join(['* %s' % podcast_markdown_line(p) for p in podcasts])

    videos: typing.List[Video] = sorted(fetch_spring_tips_videos(), key=record_date_key, reverse=True)
    videos_markup = os.linesep.join(['* %s' % video_markdown_line(v) for v in videos])

    profile_page: str = os.environ['PROFILE_PAGE']
    assert os.path.exists(profile_page), 'the profile page %s does not exist.' % profile_page

    with open(profile_page, 'r') as ppfp:
        content = ppfp.read()

    def add_newlines_to_section(c: str):
        newlines = '\n' * 2
        return '%s%s%s' % (newlines, c, newlines)

    markup = replace_fragment(content, 'APPEARANCES', add_newlines_to_section(appearances_markup))
    markup = replace_fragment(markup, 'PODCASTS', add_newlines_to_section(podcasts_markup))
    markup = replace_fragment(markup, 'SCREENCASTS', add_newlines_to_section(videos_markup))
    markup = '%s\n\n%s' % (markup, '<!-- generated %s -->' % datetime.datetime.now().isoformat())

    with open(profile_page, 'w') as ppfp:
        ppfp.write(markup)


if __name__ == '__main__':
    main(sys.argv)
