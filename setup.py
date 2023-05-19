import requests
from bs4 import BeautifulSoup
import time
from FB2 import FictionBook2, Author
import os
import torch
chapter = 1
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
url = f"https://ranobelib.me/last-wish-system/v1/c{chapter}"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
target_div = soup.find("div", class_="reader-header-action__text text-truncate")
output_file_name = target_div.text
paragraphs = soup.find_all("p")
with open(f'Глава {chapter}-{output_file_name}.txt', "w", encoding="utf-8") as file:
    for i in range(1):
        url = f'https://ranobelib.me/last-wish-system/v1/c{chapter}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f'Ошибка при получении страницы, повторная попытка через 5 секунд...')
            time.sleep(5)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        text_list = [p.text for p in soup.find_all('p') if
                     'Больше не показывать' not in p.text and
                     'Внимание! Данный контент может содержать ненормативную лексику, сексуальные сцены откровенного характера, а также художественное изображение жестокости и насилия и ux cлoвecныe oпucaнuя, которые недоступны для просмотра лицам до 18 лет.'
                     not in p.text]
        file.write('\n'.join(text_list))
        print(f'Текст главы {chapter} сохранен в файл {output_file_name}.txt')
        chapter += 1

#FB2 BLOCK
with open(f'Глава {chapter-1}-{output_file_name}.txt', 'r', encoding='utf-8') as input_file:
    text = input_file.read()
book = FictionBook2()
book.titleInfo.title = f"{output_file_name}"
book.titleInfo.authors = [Author(firstName="FALN", lastName="LNDZ")]
book.titleInfo.genres = ["sf", "sf_fantasy"]
book.chapters.append(("Глава 1", [text]))
book.write(f"Глава {chapter-1}-{output_file_name}.fb2")
print(f'Текст главы {chapter-1} сохранен в файл {output_file_name}.fb2')

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
with open(f"Глава {chapter-1}-{output_file_name}.txt", encoding="utf-8") as f:
    while True:
        example_text = f.read(1000)
        print("Считываю документ...")
        if not example_text:
            break
        audio_paths = model.save_wav(text=example_text, speaker=speaker, sample_rate=sample_rate, put_accent=put_accent, put_yo=put_yo)
        print(f"Записал озвучку - Часть {part}...")
        old_name = 'test.wav'
        new_name = f'Часть {part}-{output_file_name}.mp3'
        os.rename(old_name, new_name)
        part = part + 1
print(f"Запись файлов {output_file_name} глава  {chapter-1} закончена")