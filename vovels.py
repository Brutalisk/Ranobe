import pymorphy2
import nltk

# инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()

# текст для анализа
text = "Купил мужик замок, он ему понравился. Потом купил мужик замок, что бы жить в нем."

# разбиение текста на предложения
sentences = nltk.sent_tokenize(text)

# список слов, которые нужно проанализировать
words_to_analyze = ["замок"]

# проходимся по каждому слову для анализа
for word in words_to_analyze:
    # находим предложение, в котором содержится это слово
    for i, sentence in enumerate(sentences):
        if word in sentence:
            # извлекаем два предыдущих и два последующих предложения для анализа контекста
            prev_sentences = sentences[max(0, i-2):i]
            next_sentences = sentences[i+1:min(i+3, len(sentences))]
            context = " ".join(prev_sentences + next_sentences)
            # анализируем контекст для определения ударения
            words = nltk.word_tokenize(context)
            for j, w in enumerate(words):
                if w == word:
                    # находим морфологическую информацию о слове
                    parsed_word = morph.parse(w)[0]
                    if "nomn" in parsed_word.tag:
                        # определяем ударение
                        if parsed_word.stress_position:
                            print(f"{word} ударение на {parsed_word.stress_position}-й слог")
                        else:
                            print(f"{word} ударение неизвестно")
                    else:
                        print(f"{word} не является существительным")
                    break
            break
