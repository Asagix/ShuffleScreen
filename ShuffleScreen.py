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
import vlc
import functools
import time
from PyQt6 import QtWidgets, QtGui, QtCore

# List of video file extensions supported by VLC
VIDEO_EXTENSIONS = [
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
    '.webm', '.mpeg', '.mpg', '.ts', '.m4v'
]

class VideoFrame(QtWidgets.QFrame):
    """Custom video frame."""
    double_clicked = QtCore.pyqtSignal()
    wheel_scrolled = QtCore.pyqtSignal(int)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.setStyleSheet("background-color: black;")
        self.setMouseTracking(True)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()

    def wheelEvent(self, event):
        self.wheel_scrolled.emit(event.angleDelta().y())

class VideoPlayer(QtWidgets.QMainWindow):
    """Main application window for ShuffleScreen."""

    def __init__(self):
        super().__init__()

        # VLC instances and players
        self.instances = []  # List of VLC instances
        self.players = []  # List of media players
        self.video_frames = []  # Corresponding video frames

        # Number of videos to play simultaneously
        self.num_videos = 1

        # Video files list
        self.video_files = []
        self.last_played = []

        # Fullscreen state
        self.is_fullscreen = False

        # Save normal geometry
        self.normal_geometry = self.saveGeometry()

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

        # Active screens label
        self.active_screens_label = QtWidgets.QLabel("Active Screens: 1")

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
        self.volume_slider.setValue(50)  # Default volume set to 50
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setEnabled(False)

        volume_layout.addWidget(self.mute_button)
        volume_layout.addWidget(self.volume_slider)

        # Current video label
        self.current_video_label = QtWidgets.QLabel("No video playing.")
        self.current_video_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Mute checkboxes for individual videos
        self.mute_checkboxes_layout = QtWidgets.QHBoxLayout()
        self.update_mute_checkboxes()

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
        playback_layout.addWidget(self.active_screens_label)

        playback_layout.addWidget(self.toggle_playlist_button)

        controls_layout.addLayout(playback_layout)
        controls_layout.addStretch()
        controls_layout.addLayout(volume_layout)

        main_layout.addWidget(self.folder_button)
        main_layout.addWidget(self.folder_label)
        main_layout.addLayout(self.mute_checkboxes_layout)  # Add mute checkboxes layout
        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addWidget(self.current_video_label)
        main_layout.addLayout(controls_layout)

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

    def change_num_videos(self, value):
        """Change the number of videos to play simultaneously."""
        self.num_videos = value
        self.active_screens_label.setText(f"Active Screens: {self.num_videos}")
        # Stop existing players
        for player in self.players:
            if player.is_playing():
                player.stop()
                time.sleep(0.1)
            player.release()
        self.last_played = []
        # Clear existing instances, players, video frames
        self.instances.clear()
        self.players.clear()
        self.video_frames.clear()
        # Clear the video area layout
        while self.video_area_layout.count():
            item = self.video_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        # Clear mute checkboxes
        self.update_mute_checkboxes()
        # Create new instances, players, and video frames
        for i in range(self.num_videos):
            instance = vlc.Instance()
            player = instance.media_player_new()
            player.video_set_mouse_input(False)
            player.video_set_key_input(False)
            video_frame = VideoFrame(i)
            video_frame.double_clicked.connect(self.video_frame_double_click)
            video_frame.wheel_scrolled.connect(functools.partial(self.video_frame_wheel_scrolled, i))
            self.set_video_output(player, video_frame)
            self.instances.append(instance)
            self.players.append(player)
            self.video_frames.append(video_frame)
        # Arrange video frames in the layout
        self.arrange_video_frames()
        # Update mute checkboxes
        self.update_mute_checkboxes()
        # Start playing new set immediately if videos are loaded
        if self.video_files:
            self.play_random_videos()
            self.play_button.setText("Pause")

    def update_mute_checkboxes(self):
        """Update mute checkboxes for individual videos."""
        # Clear existing checkboxes
        while self.mute_checkboxes_layout.count():
            item = self.mute_checkboxes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # Add new checkboxes
        for index in range(self.num_videos):
            checkbox = QtWidgets.QCheckBox(f"Mute Video {index + 1}")
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(functools.partial(self.toggle_individual_mute, index))
            self.mute_checkboxes_layout.addWidget(checkbox)

    def toggle_individual_mute(self, index, state):
        """Toggle mute for an individual video."""
        is_muted = state == QtCore.Qt.CheckState.Checked.value
        current_player = self.players[index]
        current_instance = self.instances[index]
        current_media = current_player.get_media()
        current_time = current_player.get_time()
        current_position = current_player.get_position()
        # Stop and release current player
        current_player.stop()
        current_player.release()
        # Create new instance with or without dummy audio output
        if is_muted:
            # Use dummy audio output to mute
            new_instance = vlc.Instance('--aout=dummy')
        else:
            # Use default audio output
            new_instance = vlc.Instance()
        new_player = new_instance.media_player_new()
        new_player.video_set_mouse_input(False)
        new_player.video_set_key_input(False)
        self.set_video_output(new_player, self.video_frames[index])
        self.instances[index] = new_instance
        self.players[index] = new_player
        # Set media and play
        if current_media:
            new_player.set_media(current_media)
            new_player.play()
            # Restore playback position
            if current_position > 0:
                new_player.set_position(current_position)
        # Attach event manager for marquee
        event_manager = new_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, functools.partial(self.on_player_playing, index=index))

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

    def toggle_fullscreen(self):
        """Toggle fullscreen mode for the video area."""
        if not self.is_fullscreen:
            # Enter fullscreen
            self.is_fullscreen = True
            # Save current geometry
            self.normal_geometry = self.saveGeometry()
            self.showFullScreen()
            self.fullscreen_button.setText("Exit Fullscreen")
            # Hide UI elements
            self.menuBar().hide()
            self.statusBar().hide()
            self.folder_button.hide()
            self.folder_label.hide()
            self.splitter.hide()
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
            self.active_screens_label.hide()
            for i in range(self.mute_checkboxes_layout.count()):
                widget = self.mute_checkboxes_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
            # Re-add video area directly to central widget
            self.centralWidget().layout().addWidget(self.video_area_widget)
            # Update the video outputs
            for player, video_frame in zip(self.players, self.video_frames):
                self.set_video_output(player, video_frame)
        else:
            # Exit fullscreen
            self.is_fullscreen = False
            self.showNormal()
            # Restore geometry
            self.restoreGeometry(self.normal_geometry)
            self.fullscreen_button.setText("Fullscreen")
            # Show UI elements
            self.menuBar().show()
            self.statusBar().show()
            self.folder_button.show()
            self.folder_label.show()
            self.splitter.show()
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
            self.active_screens_label.show()
            for i in range(self.mute_checkboxes_layout.count()):
                widget = self.mute_checkboxes_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            # Remove video area from central widget and add back to splitter
            self.centralWidget().layout().removeWidget(self.video_area_widget)
            self.splitter.addWidget(self.video_area_widget)
            # Update the video outputs
            for player, video_frame in zip(self.players, self.video_frames):
                self.set_video_output(player, video_frame)

    def video_frame_double_click(self):
        """Handle double-click event on the video frame."""
        self.toggle_fullscreen()

    def video_frame_wheel_scrolled(self, index, delta):
        """Handle mouse wheel scroll event on a video frame."""
        player = self.players[index]
        if player:
            # Scroll up to seek forward, down to seek backward
            current_time = player.get_time()
            if delta > 0:
                # Seek forward 10 seconds
                player.set_time(current_time + 10000)
            else:
                # Seek backward 10 seconds
                player.set_time(max(current_time - 10000, 0))

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
        if any(player.audio_get_mute() == 0 for player in self.players):
            for player in self.players:
                player.audio_set_mute(True)
            self.mute_button.setText("Unmute")
        else:
            for player in self.players:
                player.audio_set_mute(False)
            self.mute_button.setText("Mute")

    def set_volume(self, value):
        """Set the volume for all videos."""
        for i, player in enumerate(self.players):
            # If the player is not muted individually
            checkbox = self.mute_checkboxes_layout.itemAt(i).widget()
            if checkbox and not checkbox.isChecked():
                player.audio_set_volume(value)

    def play_random_videos(self):
        """Play random videos and overlay the video number."""
        if not self.video_files:
            return  # Avoid showing a message at startup

        self.last_played = []
        for i, player in enumerate(self.players):
            choices = [video for video in self.video_files if video not in self.last_played]
            if not choices:
                choices = self.video_files.copy()
            next_video = random.choice(choices)
            self.last_played.append(next_video)

            try:
                media = self.instances[i].media_new(next_video)
                player.set_media(media)

                # Attach event manager
                event_manager = player.event_manager()
                event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, functools.partial(self.on_player_playing, index=i))

                player.play()

                # Set initial volume
                checkbox = self.mute_checkboxes_layout.itemAt(i).widget()
                if checkbox and checkbox.isChecked():
                    player.audio_set_mute(True)
                else:
                    player.audio_set_mute(False)
                    player.audio_set_volume(self.volume_slider.value())

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{next_video}\nError: {str(e)}")

        # Update UI elements
        self.play_button.setText("Pause")
        now_playing = ', '.join([os.path.basename(v) for v in self.last_played])
        self.current_video_label.setText(f"Now Playing: {now_playing}")
        self.timer.start()

    def on_player_playing(self, event, index):
        """Event handler for when a player starts playing."""
        player = self.players[index]
        # Set VLC marquee to display the video number on top-right
        player.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 1)
        player.video_set_marquee_int(vlc.VideoMarqueeOption.Size, -30)  # Absolute font size of 30 pixels
        player.video_set_marquee_int(vlc.VideoMarqueeOption.Position, 6)  # Top-right corner
        player.video_set_marquee_string(vlc.VideoMarqueeOption.Text, f"{index + 1}")

    def play_selected_video(self, item):
        """Play the selected video from the list in all players."""
        selected_video = item.text()
        self.last_played = [selected_video] * len(self.players)  # Update last played

        for i, player in enumerate(self.players):
            try:
                media = self.instances[i].media_new(selected_video)
                player.set_media(media)

                # Attach event manager
                event_manager = player.event_manager()
                event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, functools.partial(self.on_player_playing, index=i))

                player.play()

                # Set initial volume
                checkbox = self.mute_checkboxes_layout.itemAt(i).widget()
                if checkbox and checkbox.isChecked():
                    player.audio_set_mute(True)
                else:
                    player.audio_set_mute(False)
                    player.audio_set_volume(self.volume_slider.value())

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{selected_video}\nError: {str(e)}")
        self.play_button.setText("Pause")
        self.current_video_label.setText(f"Now Playing: {os.path.basename(selected_video)}")
        self.timer.start()

    def update_ui(self):
        """Update the UI based on the players' state."""
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
                    media = self.instances[i].media_new(next_video)
                    player.set_media(media)

                    # Attach event manager
                    event_manager = player.event_manager()
                    event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, functools.partial(self.on_player_playing, index=i))

                    player.play()
                    # Set initial volume
                    checkbox = self.mute_checkboxes_layout.itemAt(i).widget()
                    if checkbox and checkbox.isChecked():
                        player.audio_set_mute(True)
                    else:
                        player.audio_set_mute(False)
                        player.audio_set_volume(self.volume_slider.value())
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Playback Error", f"Failed to play video:\n{next_video}\nError: {str(e)}")
            elif state == vlc.State.Error:
                QtWidgets.QMessageBox.warning(self, "Playback Error", "An error occurred during playback.")
                self.play_next()

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop and release all media players
        for player in self.players:
            if player.is_playing():
                player.stop()
            time.sleep(0.1)  # Wait briefly to ensure the player has stopped
            player.release()
        # Release the VLC instances
        for instance in self.instances:
            instance.release()
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
