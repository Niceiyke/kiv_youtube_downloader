import os
from pytube import YouTube, exceptions, Playlist

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
        except exceptions.RegexMatchError:
            raise ValueError("Invalid URL")
        except Exception as e:
            raise ValueError(f"Download failed: {e}")

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
        except exceptions.RegexMatchError:
            raise ValueError("Invalid Playlist URL")
        except Exception as e:
            raise ValueError(f"Download failed: {e}")
