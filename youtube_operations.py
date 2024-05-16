from pytube import YouTube, Playlist, exceptions

class YouTubeOperations:
    @staticmethod
    def get_video_info(url):
        try:
            yt = YouTube(url=url)
            video_streams = yt.streams.filter(only_video=True)
            resolutions = sorted(set(stream.resolution for stream in video_streams if stream.resolution))
            return {
                "title": yt.title,
                "url": url,
                "video_streams": video_streams,
                "resolutions": resolutions,
                "duration": round(yt.length / 60, 2)
            }
        except exceptions.RegexMatchError:
            raise ValueError("Invalid URL")
        except Exception as e:
            raise ValueError(f"Error occurred: {e}")

    @staticmethod
    def get_playlist_info(url):
        try:
            playlist = Playlist(url)
            videos_info = []
            for video in playlist.videos:
                video_streams = video.streams.filter(only_video=True)
                resolutions = sorted(set(stream.resolution for stream in video_streams if stream.resolution))
                videos_info.append({
                    "title": video.title,
                    "url": video.watch_url,
                    "video_streams": video_streams,
                    "resolutions": resolutions,
                    "duration": round(video.length / 60, 2)
                })
            return videos_info
        except exceptions.RegexMatchError:
            raise ValueError("Invalid Playlist URL")
        except Exception as e:
            raise ValueError(f"Error occurred: {e}")
