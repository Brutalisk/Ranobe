import requests
from bs4 import BeautifulSoup
import time
import os
import torch
from transliterate import translit
import wave
import re
from num2words import num2words
import spacy
import pickle

#python -m spacy download ru_core_news_sm

ru_nlp = spacy.load('ru_core_news_sm')
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

tom_number = 2
chapter_number = 5

url = f"https://ranobelib.me/mushoku-tensei/v{tom_number}/c{chapter_number}"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
target_div = soup.find("div", class_="reader-header-action__text text-truncate")
output_file_name = target_div.text
illegal_chars = r'[\\/:\*\?"<>\|]'
output_file_name = re.sub(illegal_chars, '_', output_file_name)
paragraphs = soup.find_all("p")

#PARSE
for i in range(1):
    with open(f'Глава {chapter_number}_{output_file_name}.txt', "w", encoding="utf-8") as file:
        url = url
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('Ошибка при получении страницы, повторная попытка через 5 секунд...')
            time.sleep(5)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        text_list = [p.text for p in soup.find_all('p') if
                     'Больше не показывать' not in p.text and
                     'Внимание! Данный контент может содержать ненормативную лексику, сексуальные сцены откровенного характера, а также художественное изображение жестокости и насилия и ux cлoвecныe oпucaнuя, которые недоступны для просмотра лицам до 18 лет.'
                     not in p.text and
                     'Часть 1'not in p.text and 'Часть 2' not in p.text and 'Часть 3'not in p.text and 'Часть 4'not in p.text and 'Часть 5'not in p.text and 'Часть 6'not in p.text and 'Часть 7'not in p.text and 'Часть 8'not in p.text and 'Часть 9'not in p.text and 'Часть 10'not in p.text and 'Часть 11'not in p.text]
        # Замена цифр на слова
        text_with_line_breaks = []
        for paragraph in text_list:
            paragraph_with_words = re.sub(r'\d+', lambda match: num2words(int(match.group(0)), lang='ru'), paragraph)
            paragraph_with_line_breaks = re.sub(r'\.', '.\n', paragraph_with_words)
            text_with_line_breaks.append(paragraph_with_line_breaks)

        file.write('\n'.join(text_with_line_breaks))
        print(f'Текст главы {chapter_number} сохранен в файл {output_file_name}.txt')
        chapter_number += 1

        
#STRESSED
    def load():
        with open(file="lemmas.dat", mode='rb') as f:
            lemmas = pickle.loads(f.read())
        with open(file="wordforms.dat", mode='rb') as f:
            wordforms = pickle.loads(f.read())
        return lemmas, wordforms


    def introduce_special_cases_from_dictionary(wordforms):
        for word in wordforms:
            accentuated_word = wordforms[word][0]["accentuated"]
            if re.search("́", accentuated_word):
                continue
            try:
                accentuated_word_with_plus = re.sub("([АЕИОУЫЁаеиоуыэюяё])(?![́Ѐ-ӿ])", r"\1+", accentuated_word,
                                                    count=1)
                ru_nlp.tokenizer.add_special_case(word, [{"ORTH": accentuated_word_with_plus}])
                ru_nlp.tokenizer.add_special_case(word.capitalize(),
                                                  [{"ORTH": accentuated_word_with_plus.capitalize()}])
            except ValueError:
                pass

    def compatible(interpretation, lemma, tag, lemmas):
        if lemma in lemmas:
            pos_exists = False
            possible_poses = lemmas[lemma]["pos"]
            for i in range(len(possible_poses)):
                if possible_poses[i] in tag:
                    pos_exists = True
                    break
            if not (pos_exists):
                return False

        if interpretation == "canonical":
            return True
        if "plural" in interpretation and not ("Number=Plur" in tag):
            return False
        if "singular" in interpretation and not ("Number=Sing" in tag):
            return False
        if not ("nominative" in interpretation) and ("Case=Nom" in tag):
            return False
        if not ("genitive" in interpretation) and ("Case=Gen" in tag):
            return False
        if not ("dative" in interpretation) and ("Case=Dat" in tag):
            return False
        if not ("accusative" in interpretation) and ("Case=Acc" in tag):
            adj = False
            if "ADJ" in tag and "Animacy=Inan" in tag:
                adj = True
            if not adj:
                return False
        if not ("instrumental" in interpretation) and ("Case=Ins" in tag):
            return False
        if not ("prepositional" in interpretation) and not ("locative" in interpretation) and ("Case=Loc" in tag):
            return False
        if (("present" in interpretation) or ("future" in interpretation)) and ("Tense=Past" in tag):
            return False
        if (("past" in interpretation) or ("future" in interpretation)) and ("Tense=Pres" in tag):
            return False
        if (("past" in interpretation) or ("present" in interpretation)) and ("Tense=Fut" in tag):
            return False

        return True

    def derive_single_accentuation(interpretations):
        if len(interpretations) == 0:
            return None
        res = interpretations[0]["accentuated"]
        for i in range(1, len(interpretations)):
            if interpretations[i]["accentuated"] != res:
                return None
        return res

    def accentuate_word(word, lemmas):
        if ("tag" in word) and ("PROPN" in word["tag"]):
            return word["token"]

        if word["is_punctuation"] or (not "interpretations" in word):
            return word["token"]
        else:
            res = derive_single_accentuation(word["interpretations"])
            if not (res is None):
                return res
            else:
                compatible_interpretations = []
                for i in range(len(word["interpretations"])):
                    if compatible(word["interpretations"][i]["form"], word["interpretations"][i]["lemma"], word["tag"],
                                  lemmas):
                        compatible_interpretations.append(word["interpretations"][i])
                res = derive_single_accentuation(compatible_interpretations)

                if not (res is None):
                    return res
                else:
                    new_compatible_interpretations = []
                    for i in range(len(compatible_interpretations)):
                        if compatible_interpretations[i]["lemma"] == word["lemma"]:
                            new_compatible_interpretations.append(compatible_interpretations[i])
                    res = derive_single_accentuation(new_compatible_interpretations)
                    if not (res is None):
                        return res
                    else:
                        return word["token"]

    def tokenize(text, wordforms):
        res = []
        doc = ru_nlp(text)
        for token in doc:
            if token.pos_ != 'PUNCT':
                word = {"token": token.text, "tag": token.tag_}
                if word["token"] in wordforms:
                    word["interpretations"] = wordforms[word["token"]]
                if word["token"].lower() in wordforms:
                    word["interpretations"] = wordforms[word["token"].lower()]
                word["lemma"] = token.lemma_
                word["is_punctuation"] = False
                word["uppercase"] = word["token"].upper() == word["token"]
                word["starts_with_a_capital_letter"] = word["token"][0].upper() == word["token"][0]
            else:
                word = {"token": token.text, "is_punctuation": True}
            word["whitespace"] = token.whitespace_
            res.append(word)
        return res

    def accentuate(text, wordforms, lemmas):
        res = ""
        words = tokenize(text, wordforms)
        for i in range(len(words)):
            accentuated = accentuate_word(words[i], lemmas)
            if "starts_with_a_capital_letter" in words[i] and words[i]["starts_with_a_capital_letter"]:
                accentuated = accentuated.capitalize()
            if "uppercase" in words[i] and words[i]["uppercase"]:
                accentuated = accentuated.upper()
            res += accentuated
            res += words[i]["whitespace"]
        return res

    lemmas, wordforms = load()
    introduce_special_cases_from_dictionary(wordforms)

    f = open(f'Глава {chapter_number-1}_{output_file_name}.txt', mode='r', encoding='utf-8')
    sentence = f.read()
    f.close()

    res = accentuate(sentence, wordforms, lemmas)

    f = open("final.txt", mode='w', encoding='UTF-8')
    f.write(res)
    f.close()


#CONVERT BLOCK
    with open("final.txt", "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub("([аеиоуыэюя])(́)", r"\1+", text)

    with open("final1.txt", "w", encoding="windows-1251") as f:
        f.write(text.encode("windows-1251", errors="ignore").decode("windows-1251"))


    with open("final1.txt", "r", encoding="windows-1251") as input_file:
        text = input_file.read()
    text = text.replace("а+",
                        "+а").replace("е+", "+е").replace("ё+", "+ё").replace("и+", "+и").replace("о+",
                                                                                                        "+о").replace(
        "у+",
        "+у").replace("ы+", "+ы").replace("э+",
                                          "+э").replace("ю+",
                                                        "+ю").replace("я+",
                                                                      "+я").replace('св+оим',
                                                                                    'сво+им').replace('тв+оими',
                                                                                                      'тво+ими').replace('м+оими',
                                                                                                                  'мо+ими').replace('м+ои',
                                                                                                                  'мо+и').replace('св+ои',
                                                                                                                  'сво+и').replace('тв+ои',
                                                                                                                  'тво+и').replace('ст+ороны',
                                                                                                                  'сторон+ы').replace("тв+оё", "тво+ё").replace("твоё", "тво+ё").replace("должно", "должн+о").replace('пр+оекции', 'про+экции').replace('№', 'н+омер')
    with open("plus_text.txt", "w", encoding="windows-1251") as output_file:
        output_file.write(text)
    os.startfile("plus_text.txt")
    if input("Требуется проверка текста, все ли хорошо? Y/y") == 'y' or 'Y':
        pass


#VOICE BLOCK

    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'
    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',local_file)
    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)
    sample_rate = 48000
    put_accent=True
    put_yo = True
    #aidar, baya, kseniya, xenia, eugene, random
    speaker='xenia'
    part = 1
    with open(f"plus_text.txt", encoding="windows-1251") as f:
        target_text = ""
        last_period_pos = 0
        audio_files = []
        while True:
            example_text1 = f.readline()
            example_text2 = f.readline()
            if not example_text1:
                try:
                    audio_paths = model.save_wav(text=target_text, speaker=speaker, sample_rate=sample_rate,
                                                 put_accent=put_accent, put_yo=put_yo)
                    print(f"-Записана - {part} часть")
                    old_name = 'test.wav'
                    new_name = f'Глава{chapter_number - 1}_часть{part}_{output_file_name}.wav'
                    os.rename(old_name, new_name)
                    audio_files.append(new_name)
                    part = part + 1
                except Exception as e:
                    print(f"Ошибка при записи: {str(e)}")
                break
            index_of_last_period = example_text2.rfind('.')
            if index_of_last_period != -1:
                target_text += translit(example_text1.strip() + ' ' + example_text2[:index_of_last_period + 1], 'ru')
                try:
                    audio_paths = model.save_wav(text=target_text, speaker=speaker, sample_rate=sample_rate,
                                                 put_accent=put_accent, put_yo=put_yo)
                    print(f"-Записана - {part} часть")
                    old_name = 'test.wav'
                    new_name = f'Глава{chapter_number - 1}_часть{part}_{output_file_name}.wav'
                    os.rename(old_name, new_name)
                    audio_files.append(new_name)
                    part = part + 1
                except Exception as e:
                    print(f"Ошибка при записи: {str(e)}")
                target_text = translit(example_text2[index_of_last_period + 1:].strip(), 'ru')
                last_period_pos += index_of_last_period + 1
            else:
                target_text += translit(example_text1.strip() + ' ' + example_text2.strip(), 'ru')
                last_period_pos += len(example_text1) + len(example_text2)

        print(f"------------- Все {part} файлов записаны успешно -------------")

    # объединение аудиофайлов
    if len(audio_files) > 0:
        with wave.open(audio_files[0], 'rb') as first_file:
            params = first_file.getparams()
        with wave.open(f'Глава{chapter_number - 1}_соединенный.wav', 'wb') as output_file:
            output_file.setparams(params)
            for audio_file in audio_files:
                try:
                    with wave.open(audio_file, 'rb') as audio:
                        output_file.writeframes(audio.readframes(audio.getnframes()))
                except Exception as e:
                    print(f"Ошибка при объединении аудиофайлов: {str(e)}")

    print(f"------------- Объединение аудиофайлов завершено -------------")
    os.remove("plus_text.txt")
    os.remove("final1.txt")
    os.remove("final.txt")

