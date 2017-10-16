import argparse
import base64
import json
import tweet

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?''version={apiVersion}')

def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)

def main(speech_file):
    with open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    service = get_speech_service()
    service_request = service.speech().syncrecognize(
        body={
            'config': {
                'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
                'sampleRate': 16000,  # 16 khz
                'languageCode': 'ja_JP',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    response = service_request.execute()
    gcloud_dump = json.dumps(response)
    gcloud_data = json.loads(gcloud_dump)
    tweet_text = gcloud_data['results'][0]['alternatives'][0]['transcript']
    
    print("以下の内容をツイートしますか？")
    print(tweet_text,"  [y/N]")
    user_ans = input()
    if user_ans == 'y':
      tweet.tweet(tweet_text)
    else:
      print("ツイートしませんでした。")
      exit()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('speech_file', help='./tweet.raw')
    args = parser.parse_args()
    main(args.speech_file)
