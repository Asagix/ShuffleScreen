# ShuffleScreen

![ShuffleScreen Logo](path_to_logo_image) <!-- Optional: Add a logo or screenshot here -->

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Shortcut Keys](#shortcut-keys)
- [Help Panel](#help-panel)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

**ShuffleScreen** is a versatile video player application built with Python, PyQt6, and VLC. It allows users to play multiple videos simultaneously in an automatic grid layout. Whether you're looking to showcase a collection of videos or create a dynamic multimedia display, ShuffleScreen offers an intuitive interface with robust playback controls and advanced features to enhance your viewing experience.

## Features

- **Multiple Video Playback:** Play up to 9 videos simultaneously in a grid layout.
- **Random Video Selection:** Automatically plays random videos from a selected folder and it's sub-folders.
- **Playlist Management:** View and select videos from a playlist.
- **Individual Mute Controls:** Mute or unmute each video individually.
- **Global Mute Control:** Mute or unmute all videos at once.
- **Volume Control:** Adjust the volume of all non-muted videos using a slider.
- **Fast forward or backward:** Move through videos seperately by hovering your mouse over one and scrolling the mouse wheel.
- **Fullscreen Mode:** Enter or exit fullscreen mode for an immersive viewing experience.
- **Overlay Playback Controls:** Access playback controls in fullscreen with a single click.
- **Shortcut Keys:** Utilize keyboard shortcuts for efficient control over playback.
- **Help Panel:** Access a detailed help menu with usage instructions and shortcut keys.

## Installation

### Prerequisites

- **Python 3.7 or higher** is required. You can download Python from [here](https://www.python.org/downloads/).
- **VLC Media Player** must be installed on your system as ShuffleScreen relies on VLC for video playback. Download VLC from [here](https://www.videolan.org/vlc/).

### Dependencies

Install the necessary Python packages using `pip`:

```bash
pip install python-vlc PyQt6
```

### Clone the Repository

Clone the ShuffleScreen repository to your local machine:

```bash
git clone https://github.com/yourusername/ShuffleScreen.git
cd ShuffleScreen
```

### Running the Application

Execute the Python script to launch ShuffleScreen:

```bash
python shuffle_screen.py
```

## Usage

1. **Select Video Folder:**
   - Click on the **"Select Video Folder"** button.
   - Browse and select the folder containing your video files. Supported formats include MP4, AVI, MKV, MOV, WMV, FLV, WEBM, MPEG, MPG, TS, and M4V.

2. **Adjust Number of Videos:**
   - Use the **"Number of Videos"** spin box to choose how many videos you want to play simultaneously (up to 9).

3. **Playback Controls:**
   - **Play/Pause:** Toggle playback of all videos.
   - **Next:** Load the next set of random videos.
   - **Stop:** Stop all video playback.
   - **Fullscreen:** Enter or exit fullscreen mode.
   - **Mute:** Mute or unmute all videos.
   - **Volume Slider:** Adjust the volume of all non-muted videos.
   - **Mute Video X:** Individually mute or unmute specific videos using the checkboxes.

4. **Fullscreen Mode:**
   - Double-click on any video or click the **"Fullscreen"** button to enter fullscreen.
   - In fullscreen, click once on the video area to display the overlay playback controls.
   - The controls will automatically hide after 5 seconds of inactivity but can be brought back with a single click.

5. **Help Panel:**
   - Click the **"Help"** button to open a detailed help panel containing usage instructions and shortcut keys.
   - The help panel can be toggled on or off as needed.

## Shortcut Keys

Enhance your ShuffleScreen experience with these keyboard shortcuts:

- **Spacebar:** Play/Pause all videos.
- **N:** Play the next set of random videos.
- **S:** Stop all videos.
- **F:** Toggle fullscreen mode.
- **M:** Mute/Unmute all videos.
- **Up Arrow:** Increase volume.
- **Down Arrow:** Decrease volume.
- **Right Arrow:** Seek forward by 10 seconds.
- **Left Arrow:** Seek backward by 10 seconds.
- **Esc:** Exit fullscreen mode.

## Help Panel

Access comprehensive help and usage instructions directly within the application:

- **Opening the Help Panel:**
  - Click the **"Help"** button located in the main controls area.
  - The help panel will appear as a dockable window on the right side of the application.

- **Contents of the Help Panel:**
  - **Basic Usage:** Step-by-step instructions on how to use ShuffleScreen.
  - **Controls:** Detailed descriptions of all playback controls and their functionalities.
  - **Fullscreen Mode:** Guidelines on using fullscreen mode effectively.
  - **Shortcut Keys:** List of all available keyboard shortcuts for quick access.
  - **Troubleshooting:** Tips on resolving common issues and errors.

> **Tip:** The help panel can be hidden or shown at any time by clicking the **"Help"** button again.

## Troubleshooting

### Common Issues

1. **No Videos Found:**
   - **Cause:** The selected folder does not contain any supported video files.
   - **Solution:** Ensure that the folder contains videos in supported formats (e.g., MP4, AVI, MKV).

2. **Playback Errors:**
   - **Cause:** The video file may be corrupted or in an unsupported format.
   - **Solution:** Try playing the video in VLC Media Player directly to verify its integrity. If the issue persists, consider converting the video to a supported format.

3. **Overlay Controls Not Showing:**
   - **Cause:** Ensure you are in fullscreen mode and have clicked on the video area.
   - **Solution:** Click once on the fullscreen video area to display the overlay controls.

### Support

If you encounter issues not covered in this guide, please open an [issue](https://github.com/yourusername/ShuffleScreen/issues) on the GitHub repository.

## Contributing

Contributions are welcome! If you'd like to enhance ShuffleScreen, follow these steps:

1. **Fork the Repository:**
   - Click the **"Fork"** button at the top right of the repository page.

2. **Clone Your Fork:**
   ```bash
   git clone https://github.com/yourusername/ShuffleScreen.git
   cd ShuffleScreen
   ```

3. **Create a New Branch:**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**
   - Implement your feature or fix a bug.

5. **Commit Your Changes:**
   ```bash
   git commit -m "Add Your Feature Description"
   ```

6. **Push to Your Fork:**
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request:**
   - Navigate to your fork on GitHub and click **"Compare & pull request"**.

Please ensure your code follows the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Enjoy using ShuffleScreen! If you have any questions or feedback, feel free to reach out or contribute to the project.**
