from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from res.prompt_templates import card_generation_template, test_generation_template
import sys
import json
import logging

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def parse_word_list(words):
    """
    Return a single string out of a list of words.
    """
    word_str = ""

    for word in words:
        word_str += "- " + word + "\n"

    return word_str

class GenericTextGenerator:
    def __init__(self, model: str, template: str = card_generation_template, max_tries: int = 10) -> None:
        self.tries = 0
        self.max_tries = max_tries

        # Loading model
        logger.info(f"Initializing Ollama with model {model}...")
        self.model = OllamaLLM(model=model, num_ctx=2048)
        self.model.cache = False
        logger.info("Model completely loaded in memory.")

        # Loading template
        logger.info("Loading template...")
        self.set_template = template
        template: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
        logger.info("Template loaded into memory.")

        # Chaining template and model
        logger.info("Chaining template with model.")
        self.chain = template | self.model

        logger.info("Generic Text Generator is ready.")

    def markdown_to_txt(self, markdown: str):
        if "```json" in markdown:
            txt = markdown.split("```json")[1]
            txt = txt.split("```")[0]
        elif "```":
            txt = markdown.split("```")[1]
        else:
            return markdown

        return txt

    def text_to_card(self, input: str, user_language: str, target_language: str):
        if self.tries > self.max_tries:
            logger.critical(f"Failed to generate proper card after {self.max_tries} tries.")
            return None

        # Start card generation from input
        response = self.chain.invoke(
            {"input": input, "user_language": user_language, "target_language": target_language})

        # Trim down markdown syntax: OMITTED, DEPENDS ON MODEL
        # response = response.split("</think>")[1] #for thought chain models
        logger.info(response)
        # str_json: str = ''.join(response.splitlines()[1:-1]) # previous method
        str_json = self.markdown_to_txt(response)
        # str_json: str = response # tmp fix
        logger.info(str_json)

        # Validate JSON
        try:
            logger.info("Trying to convert str to JSON...")
            result = json.loads(str_json)
            result["original_input"] = input

            return result
        except ValueError as error:
            logger.debug("Since failed to parse generated text, clearing cache...")

            logger.debug(error)
            logger.warning("Unable to generate card from generated output. Retrying...")
            self.tries += 1
            self.text_to_card(input, user_language, target_language)

    def list_to_exam(self, input: str, user_language: str, target_language: str):
        if self.tries > self.max_tries:
            logger.critical(f"Failed to generate proper exam after {self.max_tries} tries.")
            return None

        # Parse input to match prompt
        parsed_words: str = parse_word_list(input)

        # Start exam generation from input
        response = self.chain.invoke(
            {"input": parsed_words, "user_language": user_language, "target_language": target_language})

        # Trim down Markdown syntax: OMITTED, DEPENDS ON MODEL
        # response = response.split("</think>")[1] #for thought chain models
        logger.info(response)
        # str_json: str = ''.join(response.splitlines()[1:-1]) # previous method
        str_json = self.markdown_to_txt(response)
        # str_json: str = response # tmp fix
        logger.info(str_json)

        # Validate JSON
        try:
            logger.info("Trying to convert str to JSON...")
            result = json.loads(str_json)
            result["original_input"] = input

            return result
        except ValueError as error:
            logger.debug("Since failed to parse generated text, clearing cache...")

            logger.debug(error)
            logger.warning("Unable to generate exam from generated output. Retrying...")
            self.tries += 1
            self.text_to_card(input, user_language, target_language)

    def change_model(self, model: str, template: str = card_generation_template) -> None:
        # Load model
        logger.info(f"Initializing Ollama with model {model}...")
        self.model = OllamaLLM(model=model)
        logger.info("Model completely loaded in memory.")

        # Load template
        logger.info("Loading template...")
        template: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
        logger.info("Template loaded into memory.")

        # Chain template with model
        logger.info("Chaining template with model.")
        self.chain = template | self.model

    def change_template(self, template: str) -> None:
        # Load template
        logger.info("Loading template...")
        self.set_template = template
        template: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
        logger.info("Template loaded into memory.")

        # Chain template with model
        logger.info("Chaining template with model.")
        self.chain = template | self.model

    def use_exam_template(self):
        self.change_template(test_generation_template)

    def use_card_template(self):
        self.change_template(card_generation_template)

    def is_generating_cards(self):
        if self.set_template == card_generation_template:
            return True

        return False

    def is_generating_exams(self):
        if self.set_template == test_generation_template:
            return True

        return False