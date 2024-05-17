#youtube_operations.py

from pytube import YouTube, Playlist, exceptions

import traceback

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
        except exceptions.VideoUnavailable:
            raise ValueError("Video is unavailable")
        except exceptions.LiveStreamError:
            raise ValueError("Cannot download live streams")
        except exceptions.VideoPrivate:
            raise ValueError("Video is private")
        except exceptions.MembersOnly:
            raise ValueError("Video is members-only")
        except exceptions.AgeRestrictedError:
            raise ValueError("Video is age-restricted")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Error occurred in get_video_info: {e}")

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
        except exceptions.VideoUnavailable:
            raise ValueError("One or more videos in the playlist are unavailable")
        except KeyError:
            raise ValueError("Invalid Playlist URL")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Error occurred in get_playlist_info: {e}")
