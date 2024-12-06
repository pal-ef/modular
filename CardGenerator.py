from generation.CardTextGenerator import CardTextGenerator
from generation.ImageGenerator import ImageGenerator
from generation.VoiceGenerator import VoiceGenerator
import sys, logging

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class CardGenerator:
    def __init__(self):
        self.text_generator = CardTextGenerator("qwen2.5-coder:14b")
        self.image_generator = ImageGenerator()
        self.voice_generator = VoiceGenerator()

    def generate_identifier(self) -> str:
        return "1"

    def generate_card(self, input: str, user_language: str, target_language: str):
        logger.info("Generating card...")
        card = self.text_generator.text_to_card(input, user_language, target_language)
        logger.info("Text generation succesfull.")
        examples = card["examples"]

        logger.info("Generating voices for examples...")
        card.update({"examples_audio_path": []})
        
        for example in examples:
            logger.info(f"Generating voice for example: {example}")
            response = self.voice_generator.generate("en", example, 'standard', 'hannah', 'example')
            card["examples_audio_path"].append(response["output_file_path"])

        UID = self.generate_identifier()
        card.update({"UID": UID})

        if not card:
            return False
        
        self.image_generator.text_to_image(card["image_prompt"], UID)

        return card