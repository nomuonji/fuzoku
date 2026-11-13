"""Mix #008 narration, office hum, keys, heels, and neon."""
import json, pathlib, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

D = pathlib.Path(__file__).resolve().parent
SR = 48000
TL = json.loads((D / "timeline.json").read_text())
DUR = float(TL["total"])
N = int(DUR * SR)
rng = np.random.default_rng(6)

def db(v): return 10 ** (v / 20)

def filt(x, lo=None, hi=None):
    if lo and hi:
        sos = butter(3, [lo, hi], btype="band", fs=SR, output="sos")
    elif lo:
        sos = butter(3, lo, btype="high", fs=SR, output="sos")
    elif hi:
        sos = butter(3, hi, btype="low", fs=SR, output="sos")
    else:
        return x
    return sosfilt(sos, x)

def place(buf, x, when, gain=1.0):
    i = max(0, int(when * SR))
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j-i] * gain

def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True
    ).stdout
    return np.frombuffer(raw, np.float32).copy()

def norm(x, target):
    rms = np.sqrt(np.mean(x * x)) + 1e-9
    return x * db(target) / rms

def envelope(points):
    ts, vs = zip(*points)
    return np.interp(np.arange(N) / SR, ts, vs)

ev = dict(TL["events"])
vo = np.zeros(N, dtype=np.float64)
for k, start, duration in TL["vo"]:
    x = norm(load(D / f"vo_fast/{k}.wav"), -16)
    place(vo, x, start)

# Background music, ducked under narration.
bgm = load(D / "bgm.mp3")
bgm = np.pad(bgm[:N], (0, max(0, N-len(bgm))))
bgm = norm(bgm, -28)
active = np.convolve((np.abs(vo) > 0.003).astype(float), np.ones(int(SR*0.22))/(SR*0.22), mode="same")
duck = 1 - 0.72 * np.clip(active * 3, 0, 1)
bg_level = envelope([(0,0.55),(TL["teaser_end"],0.55),(TL["teaser_end"]+0.1,0),
                     (TL.get("main_start",TL["teaser_end"]+1.4)-0.15,0),(TL.get("main_start",TL["teaser_end"]+1.4)+0.3,0.8),
                     (ev["heels"]-1.8,0.8),(ev["heels"]-0.1,0),(ev["neon"],0),
                     (ev["neon"]+0.6,0.32),(DUR,0.25)])
music = bgm * duck * bg_level

# Office hum: low body with slow rail rhythm, ducked under the voice. Stops after the doors.
t = np.arange(N) / SR
noise = rng.normal(0,1,N)
noise_hi = rng.normal(0,1,N)
rhythm = 0.75 + 0.25*np.clip(np.sin(2*np.pi*t/1.35)*4-3, 0, 1)
room = filt(noise, hi=180) * db(-30) * rhythm + filt(noise_hi, 700, 3000) * db(-50)
room_env = envelope([(0,0.5),(TL["teaser_end"],0.5),(TL["teaser_end"]+0.05,0),
                     (TL.get("main_start",TL["teaser_end"]+1.4)+0.1,0),(TL.get("main_start",TL["teaser_end"]+1.4)+0.8,0.6),
                     (ev["door"],0.6),(ev["door"]+1.2,0.12),(ev["heels"]-0.5,0.12),
                     (ev["heels"],0.05),(ev["neon"],0),(DUR,0.1)])
room *= room_env * (1 - 0.58*np.clip(active*3,0,1))

sfx = np.zeros(N)
# Notification: one muted two-tone chime.
for j,f in enumerate((880,1320)):
    n=int(SR*0.25); tt=np.arange(n)/SR
    place(sfx, np.sin(2*np.pi*f*tt)*np.exp(-tt/0.09), ev["notif"]+j*0.09, db(-30))
# Keyboard clatter then a final enter key.
for j in range(26):
    n=int(SR*0.03); tt=np.arange(n)/SR
    click=filt(rng.normal(0,1,n), 1500, 6500)*np.exp(-tt/0.005)
    place(sfx, click, ev["keys"] + j*0.045 + rng.uniform(0,0.02), db(-31))
# Building door: soft hiss.
n=int(SR*0.9); tt=np.arange(n)/SR
place(sfx, filt(rng.normal(0,1,n),2500,8000)*np.exp(-tt/0.3), ev["door"], db(-30))
# Three heel clicks with soft low knocks.
def heel():
    n=int(SR*0.35); tt=np.arange(n)/SR
    click=filt(rng.normal(0,1,n),1800,6500)*np.exp(-tt/0.007)
    knock=np.sin(2*np.pi*190*tt)*np.exp(-tt/0.028)*0.45
    return click+knock
for i, offset in enumerate((0,0.55,1.1)):
    place(sfx,heel(),ev["heels"]+offset,db(-14-i*1.5))
# Neon flicker and a low note.
n=int(SR*3.0); tt=np.arange(n)/SR
gate=(tt>0.48).astype(float)
buzz=(np.sin(2*np.pi*120*tt)*0.35+np.sin(2*np.pi*240*tt)*0.2)*gate
crackle=filt(rng.normal(0,1,n),2000,8000)*np.maximum(0,np.diff(np.r_[0,gate]))*db(0)
place(sfx,buzz,ev["neon"],db(-30))
place(sfx,crackle,ev["neon"],db(-26))
n=int(SR*3.6); tt=np.arange(n)/SR
low=np.zeros(n)
for h in range(1,6):
    low += np.sin(2*np.pi*55*h*tt)/(h**1.35)*np.exp(-tt/(2.1/h))
place(sfx,low,ev["low"],db(-17))

mix = vo + music + room + sfx
peak = float(np.max(np.abs(mix))) + 1e-9
if peak > 0.9: mix = np.tanh(mix/peak*1.25)*0.88
fade = envelope([(0,1),(DUR-0.65,1),(DUR,0)])
mix *= fade
stereo=np.stack([mix+np.roll(room,220)*0.12,mix+np.roll(room,-220)*0.12],axis=1)
stereo /= max(1.0,float(np.max(np.abs(stereo)))/0.95)
wavfile.write(D/"mix.wav",SR,(stereo*32767).astype(np.int16))
print("mix ok",round(float(np.max(np.abs(stereo))),3),"duration",DUR)
