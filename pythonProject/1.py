import sqlite3
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import spacy
import re

nlp = spacy.load("ru_core_news_sm") # Загружаем модель для русского языка.  Подберите подходящую модель для вашего языка.
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

cursor.execute("SELECT content FROM documents")
results = cursor.fetchall()
content=""
conteyner_content=[]

for i in range(5):
    conteyner_content.append([
        token.lemma_.lower()
        for token in nlp(results[i][0])
        if not token.is_stop and token.text != '\n' and not token.is_punct and not re.fullmatch(r"[a-zA-Z]+", token.lemma_.lower())
    ])
conn.close()



tokenizer = Tokenizer(num_words=5) # Ограничиваем словарь до 10 слов
tokenizer.fit_on_texts(conteyner_content)

sequences = tokenizer.texts_to_sequences(conteyner_content)
print("sequences", sequences)

padded_sequences = pad_sequences(sequences, padding='post', maxlen=6) #добавляем паддинг
print("padded_sequences", padded_sequences)

word_index = tokenizer.word_index
print("word_index", word_index) 