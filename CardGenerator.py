from generation.CardTextGenerator import CardTextGenerator
from generation.ImageGenerator import ImageGenerator
from generation.VoiceGenerator import VoiceGenerator
import sys, logging, json, random, os, shutil
from pathlib import Path


logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)



class CardGenerator:
    def __init__(self, model: str = "phi4", style: str = "default"):
        self.text_generator = CardTextGenerator(model) # used to be qwen2.5
        self.image_generator = ImageGenerator(style)
        self.voice_generator = VoiceGenerator()

    def generate_identifier(self) -> str:
        number_of_tries = 0
        identifier = str(random.randrange(1, 999999999999999))
        my_file = Path(f"/home/jin/Projects/FrontEnd-Modular/public/{identifier}_00001_.png")
        while my_file.is_file() and number_of_tries < 5000:
            identifier = random.randrange(1, 999999999999999)
            my_file = Path(f"/home/jin/Projects/FrontEnd-Modular/public/{identifier}_00001_.png")
            number_of_tries += 1

        if number_of_tries >= 5000:
            return "Failed to generate unique identifier"

        return identifier

    def generate_card(self, input: str, user_language: str, target_language: str, style: str = "default", voice: str = "female_06",):
        voice_lang = "en"
        if target_language == "Spanish": voice_lang = "es"
        elif target_language == "Japanese": voice_lang = "ja"
        elif target_language == "French": voice_lang = "fr"

        logger.info("Generating card...")
        card = self.text_generator.text_to_card(input, user_language, target_language)
        
        if not card:
            logger.critical("Card generation failed.")
            return False
        
        logger.info("Text generation succesful.")
        examples = card["examples"]

        logger.info("Generating voices for examples...")
        card.update({"examples_audio_path": []})
        
        #print(json.dumps(card, indent=4))

        for example in examples:
            logger.info(f"Generating voice for example in {voice_lang}: {example}")
            response = self.voice_generator.generate(voice_lang, example, 'standard', voice, 'example')
            print(json.dumps(response, indent=4))
            new_path = "/home/jin/Projects/FrontEnd-Modular/public/" + response["output_file_path"][39:]
            shutil.move(response["output_file_path"], new_path)
            card["examples_audio_path"].append(response["output_file_path"][39:])

        UID = self.generate_identifier()
        if UID == "failure":
            logger.critical("WARNING: UNIQUE IDENTIFIERS ARE NOT BEING GENERATED!")
            return False
        
        card.update({"id": UID})
        card.update({"image": UID + "_00001_.png"})

        self.image_generator.text_to_image(card["image_prompt"], UID, style)

        return card