"""生成 1 秒测试音频并通过回环 HTTP 验证 yt-dlp；不访问第三方平台。"""
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import wave
from importlib.metadata import version


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def run(*args):
    result = subprocess.run(
        [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-plugin-dirs',
         '--proxy', '', '--socket-timeout', '10', *args],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        fixture = root / 'source'
        fixture.mkdir()
        audio = fixture / 'tone.wav'
        with wave.open(str(audio), 'wb') as wav:
            wav.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
            wav.writeframes(struct.pack('<h', 0) * 8000)
        handler = functools.partial(QuietHandler, directory=str(fixture))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}/tone.wav'
            metadata = json.loads(run('--simulate', '--dump-single-json', url))
            assert metadata['id'] and metadata['formats']
            batch = root / 'urls.txt'
            batch.write_text(url + '\n', encoding='utf-8')
            output = root / 'download'
            archive = root / 'archive.txt'
            common = ('--no-playlist', '--download-archive', str(archive),
                      '-P', str(output), '-o', '%(id)s.%(ext)s', '-a', str(batch))
            run(*common)
            downloaded = list(output.glob('*.wav'))
            assert len(downloaded) == 1
            digest = hashlib.sha256(downloaded[0].read_bytes()).hexdigest()
            assert digest == hashlib.sha256(audio.read_bytes()).hexdigest()
            assert archive.read_text(encoding='utf-8').strip()
            # 删除测试目录中的已知下载文件后再执行，证明归档阻止重下，
            # 而不是因为输出文件已存在才跳过。
            downloaded[0].unlink()
            run(*common)
            assert not list(output.glob('*.wav'))
            summary_path = root / 'summary.json'
            subprocess.run([sys.executable, str(Path(__file__).with_name('inspect_media.py')),
                            url, '--output', str(summary_path)], check=True, timeout=60)
            assert json.loads(summary_path.read_text(encoding='utf-8'))['id']
            report = {'yt_dlp': version('yt-dlp'), 'metadata': 'PASS',
                      'batch_download_sha256': 'PASS', 'download_archive': 'PASS',
                      'python_api': 'PASS', 'fixture_bytes': audio.stat().st_size,
                      'fixture_sha256': digest,
                      'scope': 'Local HTTP WAV only; no platform or FFmpeg verification'}
            Path('output').mkdir(exist_ok=True)
            Path('output/verification.json').write_text(
                json.dumps(report, indent=2), encoding='utf-8')
            print(json.dumps(report, indent=2))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    main()
