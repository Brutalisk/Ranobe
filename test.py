import torch

language = 'ru'
speaker = 'kseniya_16khz'
device = torch.device('cpu')

(model,
 symbols,
 sample_rate,
 example_text,
 apply_tts) = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                          model='silero_tts',
                                          language=language,
                                          speaker=speaker)

model = model.to(device)  # gpu or cpu
audio = apply_tts(texts=[example_text],
                  model=model,
                  sample_rate=sample_rate,
                  symbols=symbols,
                  device=device)