from pathlib import Path
from pytube import YouTube
from pytube.cli import on_progress
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def download_background(filename="", uri=""):
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
        if YouTube(uri, on_progress_callback=on_progress).streams.filter(res=f"{res}p").first() is None:
            if res == resolutions[-1]:
                print("No video resolution found!")
            continue

        YouTube(uri, on_progress_callback=on_progress).streams.filter(res=f"{res}p").first().download(
            "./manifestation/backgrounds", filename=f"{filename}"
        )
        break

    print("Background video downloaded successfully! 🎉")


def chop_background_video(start_time, end_time, video_id, background_filename):
    print("Chopping background video... ✂️")

    try:
        ffmpeg_extract_subclip(
            f"./manifestation/backgrounds/{background_filename}",
            start_time,
            end_time,
            targetname=f"./manifestation/temp/{video_id}/background.mp4",
        )
    except (OSError, IOError):  # ffmpeg issue see #348
        print("FFMPEG issue. Trying again...")
        with VideoFileClip(f"./manifestation/backgrounds/{background_filename}") as video:
            new = video.subclip(start_time, end_time)
            Path(f"./manifestation/temp/{video_id}").mkdir(parents=True, exist_ok=True)
            new.write_videofile(f"./manifestation/temp/{video_id}/background.mp4", audio_codec="aac", audio_bitrate="192k")
    print("Background video chopped successfully! ✂️")


