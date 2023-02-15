from pathlib import Path
from pytube import YouTube
from pytube.cli import on_progress
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os


def download_background(filename="", uri="", start=0, end=0):
    if start == 0 and end == 0:
        print("You must specify a start and end!")
        return

    Path("./manifestation/backgrounds/").mkdir(parents=True, exist_ok=True)
    # note: make sure the file name doesn't include an - in it

    if Path(f"./manifestation/backgrounds/{filename}").is_file():
        return

    if uri == "":
        print("No uri specified!")
        return

    print("Downloading the background video... please be patient 🙏, it is only done once.")

    resolutions = [1080, 720, 480, 360]
    for res in resolutions:
        if YouTube(uri, on_progress_callback=on_progress).streams.filter(res=f"{res}p", progressive=True).first() is None:
            if res == resolutions[-1]:
                print("No video resolution found!")
            continue

        YouTube(uri, on_progress_callback=on_progress).streams.filter(res=f"{res}p", progressive=True).first().download(
            "./manifestation/backgrounds", filename=f"temp.mp4"
        )
        break

    print("Background video downloaded successfully! 🎉")
    print("Chopping background video... ✂️")
    chop_background_video(filename, start, end)


def chop_background_video(filename, start, end):
    # try:
    #     ffmpeg_extract_subclip(
    #         f"./manifestation/backgrounds/temp.mp4",
    #         start,
    #         end,
    #         targetname=f"./manifestation/backgrounds/{filename}",
    #     )
    # except (OSError, IOError):  # ffmpeg issue see #348
    with VideoFileClip(f"./manifestation/backgrounds/temp.mp4") as video:
        new = video.subclip(start, end)
        new.write_videofile(f"./manifestation/backgrounds/{filename}", audio_codec="aac", audio_bitrate="192k")

    os.remove(Path(f"./manifestation/backgrounds/temp.mp4"))
    print("Background video chopped successfully! ✂️")


