from httpx import AsyncClient
from asyncio import run, sleep
from os.path import isfile, isdir
from os import mkdir, environ
from logging import basicConfig, info, error, warning as warn
from json import dumps
from multiprocessing import Process
from wget import download
from urllib.error import HTTPError
from urllib.parse import unquote
from sys import exit as sexit
from box import Box

basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',
    level=environ.get('LOGGING_LEVEL', 'INFO')
)

if not isfile('cookies.txt'):
    error('Please set cookies in cookies.txt')
    sexit()

with open('cookies.txt', encoding='utf-8') as f:
    client = AsyncClient(
        cookies = (
            _ := {
                key: val
                for key, val in map(
                    lambda _: list(map(
                        lambda __: unquote(__.strip()),
                        _.split('=',1)
                    )),
                    f.read().split(';')
                )
            }
        ),
        headers = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'X-CSRF-Token': _['ct0'],
        },
        proxy=environ.get('https_proxy')
    )

process_pool: list[Process] = []

def download_process(url:str, path:str):
    info(f'Start downloading {path}!')
    tries = 5
    while tries:
        try:
            download(url, path)
        except HTTPError as e:
            warn(f'Download {path} failed because {e}, trying again!')
            tries -= 1
            continue
        break
    if tries:
        info(f'Download {path} completed!')
        return
    error(f'Download {path} failed, max retries exceeded.')

def add_download(url:str, path:str):
    process_pool.append(
        Process(
            target=download_process, 
            args=(url,path)
        )
    )
    process_pool[-1].start()

def wait_for_finish():
    for process in process_pool:
        process.join()

async def main():
    if not isdir('data'):
        mkdir('data')

    tries = 0
    page = None
    while True:
        if tries >= 5:
            break
        try:
            resp = await client.get(
                'https://x.com/i/api/graphql/oLLzvV4gwmdq_nhPM4cLwg/Likes?'
                    'variables='
                        '%7B'
                            f'%22userId%22%3A%22{client.cookies["twid"][2:]}%22%2C'
                            '%22count%22%3A20%2C'
                            f'{"%22cursor%22%3A%22{}%22%2C".format(page) if page else ""}'
                            '%22includePromotedContent%22%3Afalse%2C'
                            '%22withClientEventToken%22%3Afalse%2C'
                            '%22withBirdwatchNotes%22%3Afalse%2C'
                            '%22withVoice%22%3Atrue%2C'
                            '%22withV2Timeline%22%3Atrue'
                        '%7D'
                    '&features='
                        '%7B'
                            '%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C'
                            '%22rweb_tipjar_consumption_enabled%22%3Atrue%2C'
                            '%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C'
                            '%22verified_phone_label_enabled%22%3Afalse%2C'
                            '%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C'
                            '%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C'
                            '%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C'
                            '%22premium_content_api_read_enabled%22%3Afalse%2C'
                            '%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C'
                            '%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C'
                            '%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Afalse%2C'
                            '%22articles_preview_enabled%22%3Atrue%2C'
                            '%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C'
                            '%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C'
                            '%22view_counts_everywhere_api_enabled%22%3Atrue%2C'
                            '%22longform_notetweets_consumption_enabled%22%3Atrue%2C'
                            '%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C'
                            '%22tweet_awards_web_tipping_enabled%22%3Afalse%2C'
                            '%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C'
                            '%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C'
                            '%22standardized_nudges_misinfo%22%3Atrue%2C'
                            '%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C'
                            '%22rweb_video_timestamps_enabled%22%3Atrue%2C'
                            '%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C'
                            '%22longform_notetweets_inline_media_enabled%22%3Atrue%2C'
                            '%22responsive_web_enhance_cards_enabled%22%3Afalse'
                        '%7D'
                    '&fieldToggles='
                        '%7B'
                            '%22withArticlePlainText%22%3Afalse'
                        '%7D'
            )
        except HTTPError as e:
            resp = None
        if not resp or resp.status_code != 200:
            error(f'Server returned an invalid status code: {resp.status_code}')
            tries += 1
            sleep(3)
            continue
        tries = 0

        entries = Box(resp.json()).data.user.result.timeline_v2.timeline.instructions[0].entries

        flag = False # Last item
        for entry in entries[:-2]:
            result = entry.content.itemContent.tweet_results.result
            dir = f'data/{result.rest_id}'
            if isdir(dir):
                flag = True
                break
            mkdir(dir)
            user = result.core.user_results.result
            legacy = result.legacy
            entities = legacy.entities
            with open(f'{dir}/metadata.json', 'w', encoding='utf-8') as f:
                f.write(dumps({
                    'user': {
                        'rest_id': user.rest_id,
                        'name': user.legacy.name
                    },
                    'tweet': {
                        'content': legacy.full_text,
                        'hashtags': entities.hashtags
                    }
                }))
            for index, media in enumerate(entities.media):
                mpath = f'{dir}/{index}.'
                if media.type == 'video':
                    add_download(
                        (_:=media.video_info.variants[-1]).url,
                        mpath+_.content_type.split('/')[-1]
                    )
                add_download(
                    (_:=media.media_url_https),
                    mpath+_.rsplit('.',1)[-1]
                )

        if flag:
            break

        if entries[-1].content.value == page:
            break

        page = entries[-1].content.value
    
    wait_for_finish()

if __name__ == '__main__':
    run(main())