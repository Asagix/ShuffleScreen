#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ShuffleScreen
=============

A Python application that plays random videos from a selected folder, with the ability to play multiple videos simultaneously in a dynamic grid layout. The videos are randomly shuffled and played in split-screen mode, offering a unique multi-video playback experience.

Copyright (c) 2024 Kevin Schürmann. All rights reserved.
"""

import sys
import os
import random
import time
import vlc
import winreg
from PyQt6 import QtWidgets, QtGui, QtCore

# List of video file extensions supported by VLC
VIDEO_EXTENSIONS = [
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
    '.webm', '.mpeg', '.mpg', '.ts', '.m4v'
]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_windows_dark_mode():
    """Check if Windows dark mode is enabled."""
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        key = winreg.OpenKey(registry, key_path)
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return value == 0
    except Exception:
        return False


class VideoFrame(QtWidgets.QFrame):
    """Custom video frame to handle double-click events."""
    double_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()


class VideoPlayer(QtWidgets.QMainWindow):
    """Main application window for the Random Video Player."""

    def __init__(self):
        super().__init__()

        # VLC player instances
        self.instance = vlc.Instance()
        self.players = []  # List of media players
        self.video_frames = []  # Corresponding video frames

        # Number of videos to play simultaneously
        self.num_videos = 1

        # Video files list
        self.video_files = []
        self.last_played = []

        # Fullscreen state
        self.is_fullscreen = False

        # Set the application window icon here, using the resource_path function
        self.setWindowIcon(QtGui.QIcon(resource_path("app_icon.ico")))

        # UI setup
        self.init_ui()

        # Timer to check video state and update UI
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)  # Check every 0.2 seconds
        self.timer.timeout.connect(self.update_ui)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ShuffleScreen")
        self.resize(800, 600)

        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        controls_layout = QtWidgets.QHBoxLayout()
        playback_layout = QtWidgets.QHBoxLayout()
        volume_layout = QtWidgets.QHBoxLayout()

        # Folder selection
        self.folder_button = QtWidgets.QPushButton("Select Video Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.folder_label = QtWidgets.QLabel("No folder selected.")

        # Video list
        self.video_list_widget = QtWidgets.QListWidget()
        self.video_list_widget.hide()  # Hide by default
        self.video_list_widget.itemDoubleClicked.connect(self.play_selected_video)
        self.video_list_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)

        # Number of videos selection
        self.num_videos_label = QtWidgets.QLabel("Number of Videos:")
        self.num_videos_spinbox = QtWidgets.QSpinBox()
        self.num_videos_spinbox.setRange(1, 9)
        self.num_videos_spinbox.setValue(1)
        self.num_videos_spinbox.valueChanged.connect(self.change_num_videos)

        # Playback controls
        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause)
        self.play_button.setEnabled(False)

        self.next_button = QtWidgets.QPushButton("Next")
        self.next_button.clicked.connect(self.play_next)
        self.next_button.setEnabled(False)

        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)

        # Fullscreen button
        self.fullscreen_button = QtWidgets.QPushButton("Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_button.setEnabled(False)

        # Toggle playlist button
        self.toggle_playlist_button = QtWidgets.QPushButton("Hide Playlist")
        self.toggle_playlist_button.clicked.connect(self.toggle_playlist)
        self.toggle_playlist_button.setEnabled(True)

        # Volume controls
        self.mute_button = QtWidgets.QPushButton("Mute")
        self.mute_button.clicked.connect(self.toggle_mute)
        self.mute_button.setEnabled(False)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setEnabled(False)

        volume_layout.addWidget(self.mute_button)
        volume_layout.addWidget(self.volume_slider)

        # Seek slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderPressed.connect(self.position_slider_pressed)
        self.position_slider.sliderReleased.connect(self.position_slider_released)
        self.position_slider.sliderMoved.connect(self.position_slider_moved)
        self.position_slider.setEnabled(False)
        self.position_slider.setSingleStep(1)

        # Time labels
        self.current_time_label = QtWidgets.QLabel("00:00")
        self.total_time_label = QtWidgets.QLabel("00:00")

        # Position layout
        position_layout = QtWidgets.QHBoxLayout()
        position_layout.addWidget(self.current_time_label)
        position_layout.addWidget(self.position_slider, stretch=1)
        position_layout.addWidget(self.total_time_label)

        # Current video label
        self.current_video_label = QtWidgets.QLabel("No video playing.")
        self.current_video_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Video area
        self.video_area_widget = QtWidgets.QWidget()
        self.video_area_layout = QtWidgets.QGridLayout(self.video_area_widget)
        self.video_area_layout.setContentsMargins(0, 0, 0, 0)
        self.video_area_layout.setSpacing(0)

        # Content splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.video_list_widget)
        self.splitter.addWidget(self.video_area_widget)
        self.splitter.setSizes([200, 600])  # Initial sizes
        self.splitter.setStretchFactor(0, 0)  # Playlist does not stretch
        self.splitter.setStretchFactor(1, 1)  # Video area stretches
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # Assemble layouts
        playback_layout.addWidget(self.play_button)
        playback_layout.addWidget(self.next_button)
        playback_layout.addWidget(self.stop_button)
        playback_layout.addWidget(self.fullscreen_button)

        # Number of videos control (placed near playback controls)
        playback_layout.addWidget(self.num_videos_label)
        playback_layout.addWidget(self.num_videos_spinbox)

        playback_layout.addWidget(self.toggle_playlist_button)

        controls_layout.addLayout(playback_layout)
        controls_layout.addStretch()
        controls_layout.addLayout(volume_layout)

        main_layout.addWidget(self.folder_button)
        main_layout.addWidget(self.folder_label)
        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addLayout(position_layout)
        main_layout.addWidget(self.current_video_label)
        main_layout.addLayout(controls_layout)

        # Apply styles
        self.apply_styles()

        # Initialize players and video frames
        self.change_num_videos(self.num_videos)

    def set_video_output(self, player, video_frame):
        """Set the video output window for the VLC player."""
        win_id = int(video_frame.winId())
        if sys.platform.startswith('linux'):
            player.set_xwindow(win_id)
        elif sys.platform == "win32":
            player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            player.set_nsobject(win_id)

    def apply_styles(self):
        """Apply styles based on Windows dark mode setting."""
        dark_mode = is_windows_dark_mode()
        if dark_mode:
            # Dark theme styles
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                }
                QPushButton {
                    background-color: #3e3e42;
                    color: #d4d4d4;
                    border: none;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #505053;
                }
                QLabel {
                    color: #d4d4d4;
                }
                QListWidget {
                    background-color: #3e3e42;
                    color: #d4d4d4;
                }
                QSlider::groove:horizontal {
                    background: #5a5a5a;
                    height: 8px;
                }
                QSlider::handle:horizontal {
                    background: #d4d4d4;
                    width: 16px;
                    margin: -4px 0;
                }
            """)
        else:
            # Light theme styles
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #e1e1e1;
                    color: #000000;
                    border: none;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #d4d4d4;
                }
                QLabel {
                    color: #000000;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QSlider::groove:horizontal {
                    background: #d4d4d4;
                    height: 8px;
                }
                QSlider::handle:horizontal {
                    background: #000000;
                    width: 16px;
                    margin: -4px 0;
                }
            """)

    def select_folder(self):
        """Open folder picker dialog and load video files."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Video Folder")
        if folder:
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.load_videos(folder)
        else:
            self.folder_label.setText("No folder selected.")

    def load_videos(self, folder):
        """Load video files from the selected folder."""
        self.video_files = []
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                    self.video_files.append(os.path.join(dirpath, filename))

        if self.video_files:
            self.video_list_widget.clear()
            for video in self.video_files:
                self.video_list_widget.addItem(video)
            self.video_list_widget.show()
            # Enable playback controls
            self.play_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.fullscreen_button.setEnabled(True)
            self.mute_button.setEnabled(True)
            self.volume_slider.setEnabled(True)
            self.position_slider.setEnabled(True)
            # Start playback automatically
            self.play_random_videos()
            self.play_button.setText("Pause")
        else:
            QtWidgets.QMessageBox.warning(self, "No Videos Found", "No video files were found in the selected folder.")
            self.play_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.fullscreen_button.setEnabled(False)
            self.mute_button.setEnabled(False)
            self.volume_slider.setEnabled(False)
            self.position_slider.setEnabled(False)

    def change_num_videos(self, value):
        """Change the number of videos to play simultaneously."""
        is_playing = any(player.is_playing() for player in self.players)
        self.num_videos = value
        # Stop existing players
        for player in self.players:
            if player.is_playing():
                player.stop()
                time.sleep(0.1)
            player.release()
        self.last_played = []
        # Clear existing players and video frames
        self.players.clear()
        self.video_frames.clear()
        # Clear the video area layout
        while self.video_area_layout.count():
            item = self.video_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        # Create new players and video frames
        for i in range(self.num_videos):
            player = self.instance.media_player_new()
            player.video_set_mouse_input(False)
            player.video_set_key_input(False)
            video_frame = VideoFrame()
            video_frame.mouseDoubleClickEvent = self.video_frame_double_click
            self.set_video_output(player, video_frame)
            self.players.append(player)
            self.video_frames.append(video_frame)
        # Arrange video frames in the layout
        self.arrange_video_frames()
        # If videos were playing, start playing new set immediately
        if is_playing:
            self.play_random_videos()
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

    def arrange_video_frames(self):
        """Arrange video frames in the video area layout."""
        num = len(self.video_frames)
        rows = cols = int(num ** 0.5)
        if rows * cols < num:
            cols += 1
        if rows * cols < num:
            rows += 1
        index = 0
        for row in range(rows):
            for col in range(cols):
                if index < num:
                    self.video_area_layout.addWidget(self.video_frames[index], row, col)
                    index += 1

    def play_pause(self):
        """Toggle play/pause for all videos."""
        if any(player.is_playing() for player in self.players):
            for player in self.players:
                player.pause()
            self.play_button.setText("Play")
        else:
            if all(player.get_state() in [vlc.State.Ended, vlc.State.NothingSpecial, vlc.State.Stopped] for player in self.players):
                self.play_random_videos()
            else:
                for player in self.players:
                    player.play()
            self.play_button.setText("Pause")
            self.timer.start()

    def play_next(self):
        """Play the next set of random videos."""
        self.play_random_videos()

    def stop(self):
        """Stop video playback."""
        for player in self.players:
            if player.is_playing():
                player.stop()
                time.sleep(0.1)  # Wait briefly
        self.play_button.setText("Play")
        self.current_video_label.setText("No video playing.")
        self.timer.stop()
        self.position_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode for the video area."""
        if not self.is_fullscreen:
            # Enter fullscreen
            self.is_fullscreen = True
            self.showFullScreen()
            self.fullscreen_button.setText("Exit Fullscreen")
            # Hide UI elements
            self.menuBar().hide()
            self.statusBar().hide()
            self.folder_button.hide()
            self.folder_label.hide()
            self.splitter.hide()
            self.position_slider.hide()
            self.current_time_label.hide()
            self.total_time_label.hide()
            self.current_video_label.hide()
            self.play_button.hide()
            self.next_button.hide()
            self.stop_button.hide()
            self.mute_button.hide()
            self.volume_slider.hide()
            self.fullscreen_button.hide()
            self.toggle_playlist_button.hide()
            self.num_videos_label.hide()
            self.num_videos_spinbox.hide()
            # Re-add video area directly to central widget
            self.centralWidget().layout().addWidget(self.video_area_widget)
            # Update the video outputs
            for player, video_frame in zip(self.players, self.video_frames):
                self.set_video_output(player, video_frame)
        else:
            # Exit fullscreen
            self.is_fullscreen = False
            self.showNormal()
            self.fullscreen_button.setText("Fullscreen")
            # Show UI elements
            self.menuBar().show()
            self.statusBar().show()
            self.folder_button.show()
            self.folder_label.show()
            self.splitter.show()
            self.position_slider.show()
            self.current_time_label.show()
            self.total_time_label.show()
            self.current_video_label.show()
            self.play_button.show()
            self.next_button.show()
            self.stop_button.show()
            self.mute_button.show()
            self.volume_slider.show()
            self.fullscreen_button.show()
            self.toggle_playlist_button.show()
            self.num_videos_label.show()
            self.num_videos_spinbox.show()
            # Remove video area from central widget and add back to splitter
            self.centralWidget().layout().removeWidget(self.video_area_widget)
            self.splitter.addWidget(self.video_area_widget)
            # Update the video outputs
            for player, video_frame in zip(self.players, self.video_frames):
                self.set_video_output(player, video_frame)

    def video_frame_double_click(self, event):
        """Handle double-click event on the video frame."""
        self.toggle_fullscreen()

    def toggle_playlist(self):
        """Toggle the visibility of the playlist."""
        if self.video_list_widget.isVisible():
            self.video_list_widget.hide()
            self.splitter.setSizes([0, 1])
            self.toggle_playlist_button.setText("Show Playlist")
        else:
            self.video_list_widget.show()
            self.splitter.setSizes([200, 600])
            self.toggle_playlist_button.setText("Hide Playlist")

    def toggle_mute(self):
        """Toggle mute for all videos."""
        if any(player.audio_get_mute() for player in self.players):
            for player in self.players:
                player.audio_set_mute(False)
            self.mute_button.setText("Mute")
        else:
            for player in self.players:
                player.audio_set_mute(True)
            self.mute_button.setText("Unmute")

    def set_volume(self, value):
        """Set the volume for all videos."""
        for player in self.players:
            player.audio_set_volume(value)

    def set_position(self, position):
        """Set the playback position for all videos."""
        for player in self.players:
            player.set_position(position / 1000.0)

    def position_slider_pressed(self):
        """Handle the event when the position slider is pressed."""
        self.is_seeking = True

    def position_slider_released(self):
        """Handle the event when the position slider is released."""
        self.is_seeking = False
        self.set_position(self.position_slider.value())

    def position_slider_moved(self, position):
        """Handle the event when the position slider is moved."""
        if self.is_seeking:
            lengths = [player.get_length() for player in self.players if player.get_length() > 0]
            if lengths:
                total_length = max(lengths)
                current_time = position / 1000 * total_length / 1000
                self.current_time_label.setText(self.format_time(current_time))

    def play_random_videos(self):
        """Play random videos, ensuring no immediate repeats."""
        if not self.video_files:
            QtWidgets.QMessageBox.warning(self, "No Videos", "No videos are loaded to play.")
            return

        self.last_played = []
        for player in self.players:
            choices = [video for video in self.video_files if video not in self.last_played]
            if not choices:
                choices = self.video_files.copy()
            next_video = random.choice(choices)
            self.last_played.append(next_video)

            try:
                media = self.instance.media_new(next_video)
                player.set_media(media)
                player.video_set_mouse_input(False)  # Disable VLC mouse input
                player.play()
                # Set initial volume
                player.audio_set_volume(self.volume_slider.value())
                # Ensure mute is off
                player.audio_set_mute(False)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{next_video}\nError: {str(e)}")
        self.play_button.setText("Pause")
        now_playing = ', '.join([os.path.basename(v) for v in self.last_played])
        self.current_video_label.setText(f"Now Playing: {now_playing}")
        self.timer.start()

    def play_selected_video(self, item):
        """Play the selected video from the list in all players."""
        selected_video = item.text()
        self.last_played = [selected_video] * len(self.players)  # Update last played

        for player in self.players:
            try:
                media = self.instance.media_new(selected_video)
                player.set_media(media)
                player.video_set_mouse_input(False)  # Disable VLC mouse input
                player.play()
                # Set initial volume
                player.audio_set_volume(self.volume_slider.value())
                # Ensure mute is off
                player.audio_set_mute(False)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{selected_video}\nError: {str(e)}")
        self.play_button.setText("Pause")
        self.current_video_label.setText(f"Now Playing: {os.path.basename(selected_video)}")
        self.timer.start()

    def update_ui(self):
        """Update the UI based on the players' state."""
        # Update position slider
        lengths = [player.get_length() for player in self.players if player.get_length() > 0]
        if lengths:
            total_length = max(lengths)
            positions = [player.get_position() * 1000 for player in self.players]
            average_position = sum(positions) / len(positions)
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(int(average_position))
            self.position_slider.blockSignals(False)

            # Update time labels
            current_times = [player.get_time() / 1000 for player in self.players]
            current_time = max(current_times)
            self.current_time_label.setText(self.format_time(current_time))
            total_time = total_length / 1000
            self.total_time_label.setText(self.format_time(total_time))

        # Check for ended videos and replace them
        for i, player in enumerate(self.players):
            state = player.get_state()
            if state == vlc.State.Ended:
                # Play next video in this player
                choices = [video for video in self.video_files if video not in self.last_played]
                if not choices:
                    choices = self.video_files.copy()
                next_video = random.choice(choices)
                self.last_played[i] = next_video

                try:
                    media = self.instance.media_new(next_video)
                    player.set_media(media)
                    player.play()
                    # Set initial volume
                    player.audio_set_volume(self.volume_slider.value())
                    # Ensure mute is off
                    player.audio_set_mute(False)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{next_video}\nError: {str(e)}")
            elif state == vlc.State.Error:
                QtWidgets.QMessageBox.warning(self, "Playback Error", "An error occurred during playback.")
                self.play_next()

    def format_time(self, seconds):
        """Format time in seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def adjust_volume(self, delta):
        """Adjust volume by a delta."""
        current_volume = self.volume_slider.value()
        new_volume = max(0, min(100, current_volume + delta))
        self.volume_slider.setValue(new_volume)

    def keyPressEvent(self, event):
        """Handle key press events for shortcuts."""
        if event.key() == QtCore.Qt.Key.Key_Space:
            self.play_pause()
        elif event.key() == QtCore.Qt.Key.Key_N:
            self.play_next()
        elif event.key() == QtCore.Qt.Key.Key_S:
            self.stop()
        elif event.key() == QtCore.Qt.Key.Key_F:
            self.toggle_fullscreen()
        elif event.key() == QtCore.Qt.Key.Key_M:
            self.toggle_mute()
        elif event.key() == QtCore.Qt.Key.Key_Up:
            self.adjust_volume(5)
        elif event.key() == QtCore.Qt.Key.Key_Down:
            self.adjust_volume(-5)
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            if self.is_fullscreen:
                self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop and release all media players
        for player in self.players:
            if player.is_playing():
                player.stop()
            time.sleep(0.1)  # Wait briefly to ensure the player has stopped
            player.release()
        # Release the VLC instance
        self.instance.release()
        # Add a small delay to allow VLC threads to close
        time.sleep(0.5)
        event.accept()


def main():
    """Main entry point for the application."""
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
