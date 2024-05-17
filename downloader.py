import os
from pytube import YouTube, Playlist
from pytube.exceptions import RegexMatchError, VideoUnavailable, LiveStreamError, VideoPrivate, MembersOnly, AgeRestrictedError

import traceback

class Downloader:
    @staticmethod
    def download_video(url, resolution, download_folder, progress_callback):
        try:
            yt = YouTube(url=url, on_progress_callback=progress_callback)
            video = yt.streams.filter(resolution=resolution).first()
            if not video:
                raise ValueError(f"No videos found at resolution: {resolution}")

            # Prepare the file name by removing invalid characters
            filename = "".join(x for x in video.title if x.isalnum() or x in [' ', '.']) + ".mp4"
            filepath = os.path.join(download_folder, filename)

            # Ensure download folder exists
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            # Download with progress tracking
            video.download(output_path=download_folder, filename=filename)
        except RegexMatchError:
            raise ValueError("Invalid URL")
        except VideoUnavailable:
            raise ValueError("Video is unavailable")
        except LiveStreamError:
            raise ValueError("Cannot download live streams")
        except VideoPrivate:
            raise ValueError("Video is private")
        except MembersOnly:
            raise ValueError("Video is members-only")
        except AgeRestrictedError:
            raise ValueError("Video is age-restricted")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Download failed in download_video: {e}")

    @staticmethod
    def download_audio(url, download_folder, progress_callback):
        try:
            yt = YouTube(url=url, on_progress_callback=progress_callback)
            audio = yt.streams.filter(only_audio=True).first()
            
            if not audio:
                raise ValueError("No audio streams found")

            # Prepare the file name by removing invalid characters
            filename = "".join(x for x in yt.title if x.isalnum() or x in [' ', '.']) + ".mp3"
            filepath = os.path.join(download_folder, filename)

            # Ensure download folder exists
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            # Download with progress tracking
            audio.download(output_path=download_folder, filename=filename)
        except RegexMatchError:
            raise ValueError("Invalid URL")
        except VideoUnavailable:
            raise ValueError("Video is unavailable")
        except LiveStreamError:
            raise ValueError("Cannot download live streams")
        except VideoPrivate:
            raise ValueError("Video is private")
        except MembersOnly:
            raise ValueError("Video is members-only")
        except AgeRestrictedError:
            raise ValueError("Video is age-restricted")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Download failed in download_audio: {e}")

    @staticmethod
    def download_playlist(url, resolution, download_folder, progress_callback):
        try:
            playlist = Playlist(url)
            for video in playlist.videos:
                video.register_on_progress_callback(progress_callback)
                stream = video.streams.filter(resolution=resolution).first()
                if not stream:
                    raise ValueError(f"No videos found at resolution: {resolution}")

                # Prepare the file name by removing invalid characters
                filename = "".join(x for x in video.title if x.isalnum() or x in [' ', '.']) + ".mp4"
                filepath = os.path.join(download_folder, filename)

                # Ensure download folder exists
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)

                # Download with progress tracking
                stream.download(output_path=download_folder, filename=filename)
        except RegexMatchError:
            raise ValueError("Invalid Playlist URL")
        except VideoUnavailable:
            raise ValueError("One or more videos in the playlist are unavailable")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Download failed in download_playlist: {e}")
