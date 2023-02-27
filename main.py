import argparse
from config import youtube
from youtube_uploader import uploadYouTubeVideo
from manifestation.manifestation import make_final_video


# def main():
#     yt.upload2YT("test.mp4", config.youtube) # run code


if __name__ == "__main__":
    # uploadYouTubeVideo("test.mp4", youtube)


    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, help="Options: manifestation, etc", required=True)

    parser.add_argument("-id", "--session_id", help="TikTok sessionid cookie", required=True)
    args = parser.parse_args()

    if args.mode == 'manifestation':
        # print(args.session_id)
        print("making final video")
        make_final_video(session_id=args.session_id)
        # print("manifesting...")
        # uploadVideo(args.session_id, args.path, args.title, args.tags)
