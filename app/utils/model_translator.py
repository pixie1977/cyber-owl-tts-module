import os
import torch

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_PATH = os.path.join(CURRENT_DIRECTORY, "..", "models")

model, _ = torch.hub.load(
    repo_or_dir=LOCAL_MODEL_PATH,
    model='silero_model_ru',
    language='ru',
    speaker='v4_ru'
)

# Экспорт в TorchScript
model = model.to('cpu')
scripted_model = torch.jit.script(model)

os.makedirs('models', exist_ok=True)
torch.jit.save(scripted_model, 'models/silero_model_ru_jit.pt')

print("✅ Модель успешно сохранена: models/silero_model_ru_jit.pt")