import os
import subprocess
from ..base import BaseConverter


class AudioConverter(BaseConverter):
    def validate(self, input_path, options):
        return os.path.exists(input_path)

    def execute(self, input_path, output_path, options):
        try:
            target_format = options.get("target_format", "mp3")

            if target_format == "mp3":
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_path,
                    "-codec:a",
                    "libmp3lame",
                    "-qscale:a",
                    "2",
                    output_path
                ]

            elif target_format == "wav":
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_path,
                    "-acodec",
                    "pcm_s16le",
                    output_path
                ]

            else:
                return False

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                print(result.stderr)
                return False

            return True

        except Exception as e:
            print(f"Audio conversion failed: {e}")
            return False

    def get_metadata(self):
        return {
            "category": "audio",
            "operations": [
                "audio.to_mp3",
                "audio.to_wav"
            ]
        }