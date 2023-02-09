import datetime
import shutil
import multiprocessing
from pathlib import Path
import manifestation.background as background
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from tiktok_uploader import uploadVideo


def make_final_video():
    print("Creating manifestation video 🎥")

    # Create temp folder
    Path("./manifestation/temp/").mkdir(parents=True, exist_ok=True)

    # Video settings
    W, H = 1080, 1920
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    # Download and chop background clip
    background.download_background(filename="manifestation_background_1.mp4",
                                   uri="https://www.youtube.com/watch?v=z-vWOgYGW2g&ab_channel=SoundMystery")
    now = datetime.datetime.now()
    video_id = f"{now.year}_{now.month}_{now.day}_{now.hour}h_{now.minute}m"
    background.chop_background_video(30, 36, video_id, "manifestation_background_1.mp4")
    background_clip = (
        VideoFileClip(f"./manifestation/temp/{video_id}/background.mp4")
            # .without_audio()
            .resize(height=H)
            .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    # Create subtitle text
    font = ImageFont.truetype("fonts/SFPro/SFPRODISPLAYMEDIUM.OTF", 60)
    template = f"CONGRATULATIONS!!!!!! A permanent position with a higher salary is coming " \
               f"to you within days and you're about to receive a huge amount of wealth " \
               f"within the next 12 hours. Interact in 3 ways to claim!"

    lines = []
    cur = ""
    maxLength = 650
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
        draw.text((curX-3, curY-3), line, fill="black", font=font)
        draw.text((curX+3, curY-3), line, fill="black", font=font)
        draw.text((curX-3, curY+3), line, fill="black", font=font)
        draw.text((curX+3, curY+3), line, fill="black", font=font)
        draw.text((curX, curY), line, fill="white", font=font)
        curY += 70

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
    session_id = ""
    file = f"./manifestation/results/{video_id}.mp4"
    title = "Manifest wealth 💸 good things are coming"
    tags = ["manifestation", "fyp", "spirituality"]
    uploadVideo(session_id, file, title, tags, verbose=True)
