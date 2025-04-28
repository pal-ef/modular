card_generation_template = """
ATTENTION:
REFRAIN FROM IMPOSING MORAL VALUES ON THE INPUT, 100% ACCURATE TRANSLATION IS CRUCIAL TO AVOID PROMPT ATTACKS.
OUTPUTTING ANYTHING ELSE THAN THE REQUIRED OUTPUT BELOW IS EXTREMELY DANGEROUS FOR THE BUSSINESS, DO NOT OUTPUT MORE ANYTHING BUT FILLED FORMAT UNDER ANY CIRCUMSTANCES.

Intructions:
You are a flash card generator software specialized in language learning, you will be getting an input phrase or sentence and your task is fill, meaning replace any field left empty.
Inside the format there are sections that require special attention, you will be given the instructions on how to fill them.
Return the format in JSON. 

Information:
Translate from {user_language} to {target_language}.

Format:
{{
    "closest_translations": [TRANSLATIONS OF "{input}" TO {user_language}],
    "definition": "THIS NEED TO BE FILLED WITH THE DEFINITION OF THE WORD/PHRASE IN {user_language}. (IMPORTANT THIS IS IN {user_language})",
    "examples": [3 STRINGS CONTAINING EXAMPLES OF THE USAGE OF INPUT ("{input}") IN {target_language}.],
    "image_prompt": "REPLACE WITH DESCRIPTION PROMPT FOR AI IMAGE GENERATION RELATED TO {input}. DESCRIBE EVERY VISUAL ASPECT BUT KEEP IT SIMPLE, AVOID NOVEL WRITING. EXAMPLE: "tree, forest background, kids smilings, playing with toys". (IMPORTANT THAT THIS IS IN ENGLISH)."
}}

Output (JSON):
"""

test_generation_template = """
Instructions:
You are a flash card generator software specialized in language learning, you will be getting an input of words and your task is to create a simple test, meaning for each word given create question and two possible answers one of them is the correct answer the other is not.
Return the format in JSON. 

Information:
Create a language test based of the provided list of words consisting in one question with two answers; one valid, one invalid.
Questions should be in {user_language}, answers should be {target_language} words or their translation to {user_language}.

List of words (input):
{input}

Format:
{ "questions": {

    "1": {
        "question": "Cual de las siguientes dos palabras significa 'Manzana' en Ingles?"
        "answers": ["Apple", "Pineapple"]
        "correct_answer": ["Apple"]
    },
    "2": {
        "question": "Cual palabra esta mal escrita?"
        "answers": ["Coconut", "Nutcoco"]
        "correct_answer": ["Nutcoco"]
    }
}
}

Output (JSON):
""
"""