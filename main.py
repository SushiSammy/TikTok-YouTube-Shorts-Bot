import youtube_uploader as yt
import config


def main():
    yt.upload2YT("test.mp4", config.youtube)


if __name__ == "__main__":
    main()
