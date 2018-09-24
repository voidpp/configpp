
from configpp.soil import Config

cfg = Config('app.json')

cfg.load()

print(cfg.data)
