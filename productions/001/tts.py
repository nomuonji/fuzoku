import json, sys, pathlib
import numpy as np
from scipy.io import wavfile
from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from style_bert_vits2.tts_model import TTSModel

D = pathlib.Path(__file__).resolve().parent
bert_models.load_model(Languages.JP, str(D.parent.parent / "models/bert")).float()
bert_models.load_tokenizer(Languages.JP, str(D.parent.parent / "models/bert"))

voice = sys.argv[1] if len(sys.argv) > 1 else "M1"
style = sys.argv[2] if len(sys.argv) > 2 else "Neutral"
out = D / "voice" / f"{voice}_{style}"
out.mkdir(parents=True, exist_ok=True)
ckpt = {"M1": "jvnv-M1-jp/jvnv-M1-jp_e158_s14000.safetensors", "M2": "jvnv-M2-jp/jvnv-M2-jp_e159_s17000.safetensors"}[voice]
m = TTSModel(model_path=D.parent.parent / "models" / ckpt, config_path=D.parent.parent / f"models/jvnv-{voice}-jp/config.json",
             style_vec_path=D.parent.parent / f"models/jvnv-{voice}-jp/style_vectors.npy", device="cpu")

lines = json.loads((D / "lines.json").read_text())
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
for item in lines:
    if only and item["id"] not in only:
        continue
    sr, audio = m.infer(text=item["text"], language=Languages.JP, style=style, style_weight=item.get("sw", 1.5),
                        sdp_ratio=0.25, noise=0.5, noise_w=0.7, length=item.get("len", 1.12),
                        pitch_scale=0.92, intonation_scale=item.get("int", 0.85))
    wavfile.write(out / f"{item['id']}.wav", sr, audio)
    print(item["id"], round(len(audio) / sr, 2))
