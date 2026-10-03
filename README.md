# Film Festival Video Checker and Converter

A Python tool that checks whether submitted films meet the technical requirements of the Narbonne Online Film Festival, and automatically converts the ones that do not. It uses `ffprobe` to read each video's technical details and `ffmpeg` to convert.

## Festival Requirements

| Property | Required |
|----------|----------|
| Container | MP4 |
| Video codec | H.265 (HEVC) |
| Audio codec | AAC |
| Frame rate | 25 FPS |
| Resolution | 640 x 360 (16:9) |

## How It Works

1. **Set up ffmpeg.** The script installs `ffmpeg` (which includes `ffprobe`) and prints the installed versions.
2. **Analyse each video** in the input folder with `ffprobe`. It reads the container, video codec, audio codec, resolution and frame rate.
3. **Check compliance** by comparing those values with the requirements. A frame rate within 0.1 FPS of 25 is accepted. Every mismatch is listed.
4. **Convert** each video that fails any check with `ffmpeg`:
   - video: H.265 (`libx265`), CRF 23, medium preset
   - scaled to 640x360 and set to 25 FPS
   - audio: AAC, 192 kbps, stereo
   - output: MP4 with `faststart`, saved as `<name>_formatOK.mp4` next to the original

It handles `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv` and `.m4v` files.

## Results

`Exercise3files/` holds the converted output for five test films. Checked with `ffprobe`, each one is H.265 video at 640x360 and 25 FPS with stereo AAC audio:

- `Cosmos_War_of_the_Planets_formatOK.mp4`
- `Last_man_on_earth_1964_formatOK.mp4`
- `The_Gun_and_the_Pulpit_formatOK.mp4`
- `The_Hill_Gang_Rides_Again_formatOK.mp4`
- `Voyage_to_the_Planet_of_Prehistoric_Women_formatOK.mp4`

The original films (in MP4, MOV and AVI formats, about 300 MB in total) are not stored in this repository.

## Project Structure

| File / folder | Purpose |
|---------------|---------|
| `Exercise 3.py` | The whole tool: ffmpeg setup, requirements, analysis, compliance check, conversion and the main run |
| `Exercise3files/` | The input folder, with the converted `_formatOK.mp4` films |

## Run Locally

You need Python 3 and ffmpeg.

```bash
git clone https://github.com/ayeshaatif07/Film-Festival-Video-Converter.git
cd Film-Festival-Video-Converter
```

Put the videos you want to check in the `Exercise3files/` folder, then run:

```bash
python3 "Exercise 3.py"
```

The script installs ffmpeg with `apt-get`, so it is written for a Linux environment such as a Jupyter or Docker container, run with permission to install packages. On macOS or Windows `apt-get` does not exist and the script stops at that step. To run it there, install ffmpeg yourself (for example `brew install ffmpeg` on macOS) and remove the `install_ffmpeg()` call near the top of the script.

## Author and Credits

- **Author:** Ayesha Atif
- **Coursework:** Intelligent Signal Processing
- Built with Python, [FFmpeg](https://ffmpeg.org/) and ffprobe.
