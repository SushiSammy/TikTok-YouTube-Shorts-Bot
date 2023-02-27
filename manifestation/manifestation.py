import datetime
import shutil
import multiprocessing
import glob
import os
import random
import pytz
from pathlib import Path
import manifestation.background as background
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from tiktok_uploader import uploadTikTokVideo
from youtube_uploader import uploadYouTubeVideo

# For testing purposes:
# python -c 'import manifestation.manifestation as m; m.make_final_video()'
def make_final_video(session_id=""):
    print("Creating manifestation video 🎥")

    # Create temp folder
    Path("./manifestation/temp/").mkdir(parents=True, exist_ok=True)

    # Video settings
    W, H = 1080, 1920
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    # Download and chop background clip
    background.download_background(filename="windchimes.mp4",
                                   uri="https://www.youtube.com/watch?v=z-vWOgYGW2g&ab_channel=SoundMystery",
                                   start=30,
                                   end=36)
    background.download_background(filename="wheat.mp4",
                                   uri="https://www.youtube.com/watch?v=uklsxwTnrAo&ab_channel=AECIPlantHealth",
                                   start=10,
                                   end=17)
    background.download_background(filename="ocean.mp4",
                                   uri="https://www.youtube.com/watch?v=lDWoInMdjJQ&ab_channel=MyTranquilitee",
                                   start=708,
                                   end=715)
    background.download_background(filename="nebula.mp4",
                                   uri="https://www.youtube.com/watch?v=ZPxfHGbVwj8&ab_channel=TeunvanderZalm",
                                   start=260,
                                   end=268)
    background.download_background(filename="bedroom.mp4",
                                   uri="https://www.youtube.com/watch?v=xg1gNlxto2M&ab_channel=Choolutter",
                                   start=9840,
                                   end=9846)
    now = datetime.datetime.now(tz=pytz.utc)
    now = now.astimezone(pytz.timezone('US/Pacific'))
    video_id = f"{now.year}_{now.month}_{now.day}_{now.hour}h_{now.minute}m"

    background_vids = []
    for file in glob.glob('./manifestation/backgrounds/*'):
        background_vids.append(os.path.basename(file))
    random_vid = random.choice(background_vids)

    background_clip = (
        VideoFileClip(f"./manifestation/backgrounds/{random_vid}")
            # .without_audio()
            .resize(height=H)
            .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    # Create subtitle text
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(format, t):
        return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

    templates = {}
    templates[0] = f"CONGRATULATIONS!!!!!! A permanent position with a higher salary is coming to you within days and you're about to receive a huge amount of wealth within the next 12 hours. Interact in 3 ways to claim!"
    templates[1] = f"If you are seeing this video on the {custom_strftime('{S}', now)} or {custom_strftime('{S}', now.replace(day=now.day+1))} of {now.strftime('%B')}, you are about to receive a LARGE amount of wealth in 7-8 hours. Don't skip, interact in at least 3 ways to claim or at least save it for the drafts. Karma is real."
    templates[2] = f"If you are seeing this video on the {custom_strftime('{S}', now)} or {custom_strftime('{S}', now.replace(day=now.day+1))} of {now.strftime('%B')}, you are about to receive the best news of your life in 3-5 hours after watching this. Use this sound (could be private) and interact in at least 3 ways to claim."
    templates[3] = f"This is your last chance. It doesn't matter if you've skipped all the other sounds, but if you skip this one, it's over. You will live the best life possible, have a lot of fun, money, and a long lasting relationship with your crush. Don't risk skipping. Interact in 3 ways to claim."
    templates[4] = f"If you are seeing this video on the {custom_strftime('{S}', now)} or {custom_strftime('{S}', now.replace(day=now.day+1))} of {now.strftime('%B')}, this video is meant for you. The love of your life will find their way to you in the next 1-2 days, and they will fall in love with you. Interact in 3 ways to claim."

    font = ImageFont.truetype("fonts/SFPro/SFPRODISPLAYMEDIUM.OTF", 60)
    lines = []
    cur = ""
    maxLength = 700
    template = random.choice(list(templates.values()))
    for i, char in enumerate(template):
        cur += char
        next_space = template.find(" ", i + 1)
        if next_space == -1:
            next_space = len(template)
        next_word = template[i + 1:next_space]
        if char == " " and font.getlength(cur + next_word) > maxLength:
            lines.append(cur)
            cur = ""
    lines.append(cur)

    # Draw text
    x = 1080
    y = 70 * len(lines) + 100
    img = Image.new('RGBA', (x, y), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    curY = 50
    for line in lines:
        w, h = draw.textsize(line, font=font)
        curX = (1080 - w) // 2
        draw.text((curX, curY), line, fill="black", font=font, stroke_width=4)
        draw.text((curX, curY), line, fill="white", font=font)
        curY += 70

    Path(f"./manifestation/temp/{video_id}").mkdir(parents=True, exist_ok=True)
    img.save(f"./manifestation/temp/{video_id}/text.png")

    # Generate Video
    clip_length = background_clip.duration
    image_clip = (
        ImageClip(f"./manifestation/temp/{video_id}/text.png")
        .set_duration(clip_length)
        .resize(width=W)
        .set_position((0, (H - y)//2))
    )
    final = CompositeVideoClip([background_clip, image_clip])
    print("Writing final video...")
    Path("./manifestation/results/").mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        f"./manifestation/results/{video_id}.mp4",
        fps=30,
        audio_codec="aac",
        audio_bitrate="192k",
        verbose=False,
        threads=multiprocessing.cpu_count(),
    )

    # Cleanup
    shutil.rmtree(Path(f"./manifestation/temp/{video_id}"))

    # Post to TikTok
    file = f"./manifestation/results/{video_id}.mp4"
    title = "Manifest wealth 💸 good things are coming"
    tags = "manifestation fyp spirituality"
    uploadTikTokVideo(session_id, file, title, tags.split())


    # Post to YouTube
    youtube = {
        'title': title,
        'description': title,
        'tags': tags,
        'category': 23,  # has to be an int, more about category below
        'status': 'public'  # {public, private, unlisted}
    }
    uploadYouTubeVideo(file, youtube)
