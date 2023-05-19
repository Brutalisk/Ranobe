import requests
from bs4 import BeautifulSoup
import time
from FB2 import FictionBook2, Author
import os
import torch


###

#Блок сайта
site = "https://wuxiaworld.ru"
novel_name = "sistema-poslednego-zhelaniya"
glava = 1
avtor = "Автор: Alemillach"
text = ''

###

#Имя файла
url = f'{site}/{novel_name}/{novel_name}-glava-{glava}'
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
link = soup.find("a", {"rel": "category tag"})
file_name = link.text
###


with open(f'{file_name}.txt', 'a', encoding='utf-8') as f:
    for i in range(1):
        url = f'{site}/{novel_name}/{novel_name}-glava-{glava}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка при получении страницы, повторная попытка через 10 секунд...')
            time.sleep(10)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        text_list = [p.text for p in soup.find_all('p') if
                     'Редактируется Читателями!' not in p.text and
                     f'{avtor}' not in p.text and
                     'Перевод: Artificial_Intelligence' not in p.text and
                     'Ваш адрес email не будет опубликован. Обязательные поля помечены *' not in p.text
                     and "Δ" not in p.text and "Пропущена глава или т.п. - сообщи в Комментариях. Улучшить Текст можно РЕДАКТОРом!" not in p.text]
        f.write('\n'.join(text_list))
        print(f'Текст главы {glava} сохранен в файл {file_name}.txt')
        glava += 1

# Читаем содержимое текстового файла
with open(f'{file_name}.txt', 'r', encoding='utf-8') as input_file:
    text = input_file.read()

# Создаем объект книги FB2
book = FictionBook2()
book.titleInfo.title = f"{file_name}"
book.titleInfo.authors = [Author(firstName="FALN", lastName="LNDZ")]
book.titleInfo.genres = ["sf", "sf_fantasy"]
book.chapters.append(("Глава 1", [text]))
book.write(f"{file_name}.fb2")

#Блок озвучки
device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'model.pt'

#Блок исполнения озвучки
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
with open(f"{file_name}.txt", encoding="utf-8") as f:
    while True:
        example_text = f.read(1000)
        print("Считываю документ...")
        if not example_text:
            break
        audio_paths = model.save_wav(text=example_text, speaker=speaker, sample_rate=sample_rate, put_accent=put_accent, put_yo=put_yo)
        print(f"Записал озвучку - Часть {part}...")
        old_name = 'test.wav'
        new_name = f'{file_name} - Часть {part}.mp3'
        os.rename(old_name, new_name)
        part = part + 1
print(f"Запись файлов {file_name} глава  {glava-1} закончена")



#<prosody rate="slow"></prosody>
