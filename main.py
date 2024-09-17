import subprocess
from concurrent.futures import ProcessPoolExecutor


def start_fastapp():
    subprocess.call(['python', '-m', 'src.asgi'])


def start_bot():
    subprocess.call(['python', '-m', 'src.telegram.bot'])


if __name__ == '__main__':
    with ProcessPoolExecutor() as pool:
        pool.submit(start_bot)
        pool.submit(start_fastapp)
