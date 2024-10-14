# ShuffleScreen

**ShuffleScreen** is a Python application that plays random videos from a selected folder. It allows you to play multiple videos simultaneously in a dynamically arranged grid layout, with the videos being shuffled and displayed in split-screen mode.

## Features

- **Random Video Playback**: Automatically plays random videos from the selected folder.
- **Simultaneous Videos**: Play multiple videos at the same time (up to 9), arranged in a grid.
- **Interactive Controls**:
  - **Play/Pause** all videos collectively.
  - **Next** to play a new set of random videos.
  - **Stop** playback.
  - **Fullscreen Mode**: Double-click any video or use the button to toggle fullscreen.
  - **Mute/Unmute** all videos.
  - **Volume Control**: Adjust the volume for all videos.
  - **Seek Bar**: Click or drag to seek through the videos.
- **Playlist Management**:
  - **Video List**: Displays all videos in the selected folder.
  - **Select Specific Video**: Double-click a video from the list to play it in all players.
  - **Toggle Playlist Visibility**.
- **Responsive UI**: The video grid adjusts dynamically based on the number of videos.
- **Keyboard Shortcuts**:
  - **Spacebar**: Play/Pause.
  - **N**: Next videos.
  - **S**: Stop.
  - **F**: Toggle fullscreen.
  - **M**: Mute/Unmute.
  - **Up/Down Arrow Keys**: Adjust volume.
  - **Esc**: Exit fullscreen.

## Requirements

- **Python 3.6** or higher
- **VLC Media Player**: Install the desktop version of VLC media player.
- Python Packages:
  - `python-vlc`
  - `PyQt6`

## Installation

1. **Install VLC Media Player**

   - Download and install VLC from [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/).

2. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/shufflescreen.git
   cd shufflescreen
