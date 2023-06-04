#!/usr/bin/python3

from dotenv import load_dotenv
from random import randrange
from time import sleep

import os, openai, sys, requests
import simpleaudio as sa

load_dotenv()

uberduck_auth = (os.getenv("UBERDUCK_API_KEYSECOND"), os.getenv("UBERDUCK_SECRETSECOND"))

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")

adjectives = ["angry", "negative", "mean"]

def ad_lib_response():
    irand = randrange(len(adjectives)-1)
    return adjectives[irand]

def give_conversation(topic):
    adjective = ad_lib_response()

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Give a one response " + adjective + " conversation between SpongeBob SquarePants and Patrick about " + topic,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text

def generate_tts(voicemodel_uuid, speech):

    url = "https://api.uberduck.ai/speak"
    data = requests.post(
        url,
        json=dict(speech=speech, voicemodel_uuid=voicemodel_uuid),
        auth=uberduck_auth,
    ).json()

    url2 = "https://api.uberduck.ai/speak-status"

    while True:
        sleep(1)
        output = requests.get(
            url2,
            params=dict(uuid=data["uuid"]),
            auth=uberduck_auth,
        ).json()

        if "path" in output:
            if output["path"] != None:
                audio_url = output["path"]

                return audio_url

def main():
    conversation = give_conversation(sys.argv[1])
    convo_arr = conversation.splitlines()
    convo_arr = list(filter(None, convo_arr))
    audio_urls = []

    for line in convo_arr:
        print(line)

        pieces = line.split(": ")
        name = pieces[0]

        if name.lower() == 'spongebob':
            x = generate_tts("dadf8599-cc2a-44e0-a375-d18bec0b7811", pieces[1])
            audio_urls.append(x)
        
        if name.lower() == 'patrick':
            x = generate_tts("3b2755d1-11e2-4112-b75b-01c47560fb9c", pieces[1])
            audio_urls.append(x)
    

    i = 0
    for audio in audio_urls:
        filename = str(i) + "_speech.wav"

        with open(filename, 'wb') as a:
            resp = requests.get(audio)
            if resp.status_code == 200:
                a.write(resp.content)
            else:
                print(resp.reason)
                exit(1)
        
        i += 1
    
    for x in range(len(audio_urls)):
        filename = str(x) + "_speech.wav"
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
        

if __name__ == "__main__":
    main()