import pathlib
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).resolve().parent
FPS=30; DUR=64.2; N=int(DUR*FPS)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto((D / 'ep001.html').as_uri()); pg.wait_for_timeout(800)
    for i in range(N):
        pg.evaluate(f"render({i/FPS})")
        pg.screenshot(path=str(D / f'frames/{i:05d}.jpg'),type='jpeg',quality=90)
        if i%300==0: print(i,flush=True)
    b.close()
print('done')
