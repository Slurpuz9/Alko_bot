from deeppavlov import configs, build_model

ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)
text = ["John Doe и Анна Иванова работают в Google."]
result = ner_model(text)

# Извлечение имен
entities = result[1][0]
words = result[0][0]
names = [word for word, tag in zip(words, entities) if tag == 'B-PER' or tag == 'I-PER']

print("Найденные имена:", names)  # ['John', 'Doe', 'Анна', 'Иванова']