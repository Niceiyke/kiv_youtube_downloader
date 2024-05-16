from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock, mainthread
from youtube_operations import YouTubeOperations
from downloader import Downloader
import os
from functools import partial
import threading


class MyRoot(Widget):
    video_title = ObjectProperty(None)
    video_size = ObjectProperty(None)
    video_duration = ObjectProperty(None)
    url_input = ObjectProperty(None)
    resolution_spinner = ObjectProperty(None)
    progress_box = ObjectProperty(None)
    loading = BooleanProperty(False)

    download_count = 0
    download_playlist = False

    def __init__(self, **kwargs):
        super(MyRoot, self).__init__(**kwargs)
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

    def video_info(self, url):
        try:
            if self.download_playlist:
                info_list = YouTubeOperations.get_playlist_info(url)
                self.set_playlist_info(info_list)
            else:
                info = YouTubeOperations.get_video_info(url)
                self.set_video_info(info)
        except ValueError as e:
            Clock.schedule_once(lambda dt: setattr(self.ids.video_title, 'text', str(e)))

    def download_video_async(self):
        url = self.ids.url_input.text
        resolution = self.ids.resolution_spinner.text
        if self.download_playlist:
            threading.Thread(target=self._download_playlist, args=(url, resolution)).start()
        else:
            self.download_count += 1
            download_id = f"download_{self.download_count}"

            # Schedule the creation of UI elements for progress tracking on the main thread
            Clock.schedule_once(partial(self.create_progress_ui, url, resolution))

    def create_progress_ui(self, url, resolution, dt):
        progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        progress_label = Label(text=f"Downloading: {url} ({resolution})", font_size=12)
        progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(progress_label)
        progress_layout.add_widget(progress_bar)
        self.ids.progress_box.add_widget(progress_layout)

        # Start download in a new thread
        threading.Thread(target=self._download_video, args=(url, resolution, progress_bar, progress_label)).start()

    def _download_video(self, url, resolution, progress_bar, progress_label):
        try:
            Downloader.download_video(url, resolution, self.download_folder, partial(self.progress_callback, progress_bar, progress_label))
            Clock.schedule_once(lambda dt: self.update_progress_label(progress_label, "Download completed"))
        except ValueError as e:
            Clock.schedule_once(lambda dt: self.update_progress_label(progress_label, str(e)))

    def _download_playlist(self, url, resolution):
        try:
            videos_info = YouTubeOperations.get_playlist_info(url)
            for video_info in videos_info:
                self.download_count += 1
                Clock.schedule_once(partial(self.create_progress_ui_for_video, video_info, resolution))
        except ValueError as e:
            Clock.schedule_once(lambda dt: setattr(self.ids.video_title, 'text', str(e)))

    def create_progress_ui_for_video(self, video_info, resolution, dt):
        progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        progress_label = Label(text=f"Downloading: {video_info['title']} ({resolution})", font_size=12)
        progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(progress_label)
        progress_layout.add_widget(progress_bar)
        self.ids.progress_box.add_widget(progress_layout)

        threading.Thread(target=self._download_video, args=(video_info['url'], resolution, progress_bar, progress_label)).start()

    def progress_callback(self, progress_bar, progress_label, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        Clock.schedule_once(lambda dt: self.update_progress(progress_bar, progress_label, percentage))

    @mainthread
    def update_progress(self, progress_bar, progress_label, percentage):
        progress_bar.value = percentage
        progress_label.text = f"Downloading: {percentage:.2f}%"

    @mainthread
    def update_progress_label(self, progress_label, text):
        progress_label.text = text

    def update_video_info(self, resolution):
        url = self.ids.url_input.text
        threading.Thread(target=partial(self.fetch_video_info, url, resolution)).start()

    def fetch_video_info(self, url, resolution):
        try:
            info = YouTubeOperations.get_video_info(url)
            video_streams = info.get("video_streams", [])
            selected_resolution = resolution
            video_size = next((stream.filesize_mb for stream in video_streams if stream.resolution == selected_resolution), None)
            video_size_str = f"{video_size:.2f} MB" if video_size else "-"
            Clock.schedule_once(partial(self.update_video_info_ui, info["title"], info["duration"], video_size_str))
        except ValueError as e:
            Clock.schedule_once(partial(self.update_video_info_ui, "-", "-", str(e)))

    @mainthread
    def update_video_info_ui(self, title, duration, size, *args):
        self.ids.video_title.text = title
        self.ids.video_duration.text = f"{duration} min"
        self.ids.video_size.text = size

    def set_video_info(self, info):
        self.ids.video_title.text = info.get("title", "-")
        self.ids.video_duration.text = f"{info.get('duration', 0)} min"

        resolutions = info.get("resolutions", [])
        default_resolution = resolutions[0] if resolutions else "Select Resolution"
        self.update_resolution_spinner(resolutions, default_resolution)

        video_streams = info.get("video_streams", [])
        selected_resolution = self.ids.resolution_spinner.text
        video_size = next((stream.filesize_mb for stream in video_streams if stream.resolution == selected_resolution), None)
        self.ids.video_size.text = f"{video_size:.2f} MB" if video_size else "-"

    def set_playlist_info(self, info_list):
        if info_list:
            total_duration = sum(info['duration'] for info in info_list)
            self.ids.video_title.text = "Playlist"
            self.ids.video_duration.text = f"{total_duration} min"
            self.update_resolution_spinner(info_list[0].get("resolutions", []), "Select Resolution")
            self.ids.video_size.text = "-"

    @mainthread
    def update_resolution_spinner(self, resolutions, default_resolution):
        self.ids.resolution_spinner.values = resolutions
        self.ids.resolution_spinner.text = default_resolution if default_resolution in resolutions else "Select Resolution"

    def on_checkbox_active(self, checkbox, value):
        self.download_playlist = value

    def handle_text_validate(self, instance):
        url = instance.text
        threading.Thread(target=self.video_info, args=(url,)).start()


class YoutubeApp(App):
    def on_text_validate(self, instance):
        self.root.handle_text_validate(instance)

    def download_video(self):
        self.root.download_video_async()

    def build(self):
        return MyRoot()


if __name__ == "__main__":
    YoutubeApp().run()
