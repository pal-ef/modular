import json, time, sys, logging
from urllib import request
import requests

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

endpoint = "http://127.0.0.1:7851/api"

class VoiceGenerator:
    def __init__(self):
        # Verify that server is online
        logger.info("Initializing Voice Generator...")
        tries = 1

        while not self.is_server_ready() and tries <= 10:
            logger.critical(f"AllTalk TTS is not reachable. Retrying in 3 seconds... ({tries}/10 tries)")
            time.sleep(3)

        if tries == 10:
            logger.error("Failed to initialize voice generator correctly.")
            return
    
        logger.info("Voice generator initialized.")

    def is_server_ready(self) -> bool:
        logger.info("Pinging All Talk TTS endpoint...")
        req =  request.Request(endpoint + "/ready")
        status_code = request.urlopen(req).getcode()
        if status_code != 200: 
            logger.warning("PING Failed.")
            return False
        logger.info("PING Success.")
        return True

    def generate(self, language: str, text_input: str, text_filtering: str = 'standard', voice: str = 'hannah', output_file_name: str = 'dialog', output_file_timestamp: str = 'true', autoplay: str = 'true'):
        logger.info("Queueing text to voice generation endpoint...")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = f'text_input={text_input}&text_filtering={text_filtering}&character_voice_gen={voice}.wav&narrator_enabled=false&narrator_voice_gen=male_01.wav&text_not_inside=character&language={language}&output_file_name={output_file_name}&output_file_timestamp={output_file_timestamp}&autoplay={autoplay}&autoplay_volume=0.8'
        response = requests.post(endpoint + '/tts-generate', headers=headers, data=data)
        response_dict = json.loads(response.text)
        logger.info("Response obtained")

        for i in response_dict:
            logger.debug("key: ", i, "val: ", response_dict[i])
        
        return response_dict