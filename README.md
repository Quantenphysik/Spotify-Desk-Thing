# DeskThing: Spotify Desktop Controller


DeskThing is a sleek desktop application that allows you to control your Spotify playback seamlessly. With support for Spotify authentication, playback controls, shuffle, liking tracks, and real-time updates, it's your perfect Spotify companion.
Im running this on a small custom build Raspi Zero 2w with a touch display. The GUI Size is designed to perfectly fit my screen, but it can be customized very easy.

## Features

- **Play, Pause, Skip, and Rewind Songs**
- **Toggle Shuffle Mode**
- **Like/Unlike Tracks**
- **Real-Time Track Info Display**
  - Song Title, Artist, and Album
  - Album Art
- **Authentication with Spotify**
- **Lightweight and Intuitive GUI**

## Technologies Used

- **Python**
- **Spotify Web API**
- **Flask** for authentication callback handling
- **CustomTkinter** for a modern GUI
- **Pillow** for image handling
- **Requests** for API interaction
- **Threading** for non-blocking updates

---

## Installation

Follow these steps to set up and run the project locally:

### Prerequisites

- Python 3.8+
- Spotify Developer Account ([Create an app here](https://developer.spotify.com/dashboard/))
- Pipenv (optional, for virtual environment management)

### Clone the Repository
```bash
$ git clone https://github.com/your-username/DeskThing.git
$ cd DeskThing
```

### Install Dependencies

1. **Using Pip:**
   ```bash
   $ pip install -r requirements.txt
   ```

2. **Using Pipenv (recommended):**
   ```bash
   $ pipenv install
   $ pipenv shell
   ```

### Environment Variables

1. Create a `.env` file in the root directory:
   ```env
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   ```

2. Replace `your_spotify_client_id` and `your_spotify_client_secret` with values from your Spotify developer app.

## Usage

### Step 1: Authenticate with Spotify
Run the application:
```bash
$ python gui.py
```
If you're not authenticated, click **Authenticate with Spotify** and log in to your Spotify account.
After that, run the programm again to begin using your personal DeskThing

### Step 2: Control Your Playback
- Use the buttons to **play**, **pause**, **skip**, **rewind**, or **shuffle** tracks.
- **Like or Unlike** the current song.
- View real-time updates for the current song, including title, artist, album, and artwork.

---

## Project Structure

```
DeskThing/
├── assets/               # Image assets for GUI
├── logic.py              # Core Spotify API integration
├── gui.py                # CustomTkinter GUI implementation
├── .env                  # Environment variables (not included in the repo)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Screenshot

![Main Interface](assets/screenshot.png)

---

## Contribution

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository
2. Create a feature branch:
   ```bash
   $ git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   $ git commit -m 'Add new feature'
   ```
4. Push your changes:
   ```bash
   $ git push origin feature-name
   ```
5. Open a pull request

---


## Acknowledgements

- Thanks to the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for making this possible.
- GUI built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- Icons designed with ❤️.

---

## Author

**Quantenphysik09**

- [GitHub](https://github.com/Quantenphysik)

Feel free to star ⭐ the repo if you find this useful!

