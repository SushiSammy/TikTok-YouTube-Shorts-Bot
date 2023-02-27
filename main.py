import argparse
from manifestation.manifestation import make_final_video


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, help="Options: manifestation, etc", required=True)
    parser.add_argument("-id", "--session_id", help="TikTok sessionid cookie", required=True)
    args = parser.parse_args()

    if args.mode == 'manifestation':
        make_final_video(session_id=args.session_id)
