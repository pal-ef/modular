from generation.CardTextGenerator import CardTextGenerator
from generation.ImageGenerator import ImageGenerator
from generation.VoiceGenerator import VoiceGenerator
import sys, logging, json

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class CardGenerator:
    def __init__(self, model: str = "phi4", workflow: str = "default"):
        self.text_generator = CardTextGenerator(model) #qwen2.5
        self.image_generator = ImageGenerator(workflow)
        self.voice_generator = VoiceGenerator()

    def generate_identifier(self) -> str:
        return "1"

    def generate_card(self, input: str, user_language: str, target_language: str, style: str = "default", voice: str = "female_06",):
        # Self configuration
        voice_lang = "en"
        if target_language == "Spanish": voice_lang = "es"

        logger.info("Generating card...")
        card = self.text_generator.text_to_card(input, user_language, target_language)
        logger.info("Text generation succesful.")
        examples = card["examples"]

        logger.info("Generating voices for examples...")
        card.update({"examples_audio_path": []})
        
        #print(json.dumps(card, indent=4))

        for example in examples:
            logger.info(f"Generating voice for example in {voice_lang}: {example}")
            response = self.voice_generator.generate(voice_lang, example, 'standard', voice, 'example')
            print(json.dumps(response, indent=4))
            card["examples_audio_path"].append(response["output_file_path"])

        UID = self.generate_identifier()
        card.update({"UID": UID})

        if not card:
            return False
        
        self.image_generator.text_to_image(card["image_prompt"], UID, style)

        return card