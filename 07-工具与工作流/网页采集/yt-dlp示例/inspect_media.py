"""仅提取元数据；不下载音视频。URL 是必填参数。"""
import argparse
import json
from pathlib import Path
import yt_dlp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--output', default='output/summary.json')
    args = parser.parse_args()
    with yt_dlp.YoutubeDL({'noplaylist': True, 'quiet': True,
                          'socket_timeout': 20, 'retries': 2}) as ydl:
        info = ydl.extract_info(args.url, download=False)
        if not info or info.get('_type') in ('playlist', 'multi_video'):
            raise ValueError('请传入单个媒体页面地址')
        summary = {key: info.get(key) for key in
                   ('id', 'title', 'duration', 'uploader', 'webpage_url', 'extractor')}
        summary['formats'] = [
            {key: fmt.get(key) for key in ('format_id', 'ext', 'height', 'vcodec', 'acodec')}
            for fmt in info.get('formats', [])
        ]
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved metadata: {target}')


if __name__ == '__main__':
    main()
