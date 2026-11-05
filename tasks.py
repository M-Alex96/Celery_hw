from celery import Celery
from upscale import upscale
import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

app = Celery(broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/1', backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/2')

@app.task
def upscale_task(input_path: str, output_path: str, model_path: str = 'EDSR_x2.pb') -> str:
    upscale(input_path, output_path, model_path)
    return output_path