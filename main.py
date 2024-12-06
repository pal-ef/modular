import CardGenerator, json

cardgen = CardGenerator.CardGenerator()
data = cardgen.generate_card("Hollow", "Spanish", "English")

print(json.dumps(data, indent=4))