import spacy
import re

nlp = spacy.load("ru_core_news_sm")

text = "Это пример текста, и в с другие слова, которые нужно очистить.\nSome english words are here too.  !"
doc = nlp(text)


filtered_tokens = []
for token in doc:
    if not token.is_stop and not token.is_punct and token.text != '\n' and token.text != ' ': # Дополнительная проверка на \n
        lemma = token.lemma_.lower()
        if not re.fullmatch(r"[a-zA-Z]+", lemma):
            filtered_tokens.append(lemma)

