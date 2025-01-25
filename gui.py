import customtkinter as tk
from PIL import Image
import logic
import threading
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent

def get_image(path):
    image = Image.open(f'assets/{path}')
    return tk.CTkImage(image)


class PrimaryActions(tk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.is_playing = logic.is_playing()  # Track playback state

        self.back = tk.CTkButton(self, command=self.on_back_click, text="", width=50, height=50,
                                 image=get_image("back.png"))
        self.back.grid(row=0, column=0, padx=5, pady=10)

        self.play_pause = tk.CTkButton(self, command=self.on_play_pause_click, text="", width=50, height=50,
                               image=get_image("pause.png") if self.is_playing else get_image("play.png"))
        self.play_pause.grid(row=0, column=1, padx=5, pady=10)


        self.skip = tk.CTkButton(self, command=self.on_skip_click, text="", width=50, height=50,
                                 image=get_image("skip.png"))
        self.skip.grid(row=0, column=2, padx=5, pady=10)

    def on_back_click(self):
        logic.skip_back()

    def on_skip_click(self):
        logic.skip_song()

    def on_play_pause_click(self):
        # Toggle play/pause state
        if self.is_playing:
            self.play_pause.configure(image=get_image("play.png"))
            logic.pause_song()
        else:
            self.play_pause.configure(image=get_image("pause.png"))
            logic.play_song()

        self.is_playing = not self.is_playing


class SecondaryActions(tk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        print("SecondaryActions")
        self.is_shuffled = logic.is_shuffled()  # Track shuffle state
        self.is_liked = logic.is_liked()  # Track like state

        self.shuffle = tk.CTkButton(self, command=self.on_shuffle_click, text="", width=50, height=50,
                                    image=get_image("shuffle.png") if self.is_shuffled else get_image("shuffle_false.png"))
        self.shuffle.grid(row=0, column=0, padx=5, pady=10)

        self.like = tk.CTkButton(self, command=self.on_like_click, text="", width=50, height=50,
                                 image=get_image("heart_full.png") if self.is_liked else get_image("heart_empty.png"))
        self.like.grid(row=0, column=1, padx=5, pady=10)

    def on_shuffle_click(self):
        logic.toggle_shuffle(not self.is_shuffled)
        if self.is_shuffled:
            self.shuffle.configure(image=get_image("shuffle_false.png"))
        else:
            self.shuffle.configure(image=get_image("shuffle.png"))
        self.is_shuffled = not self.is_shuffled

    def on_like_click(self):
        if self.is_liked:
            self.like.configure(image=get_image("heart_empty.png"))
            logic.remove_from_liked_songs()
        else:
            self.like.configure(image=get_image("heart_full.png"))
            logic.add_to_liked_songs()

        self.is_liked = not self.is_liked


class SongInfo(tk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.title = tk.CTkLabel(self, text="No song playing", font=("Arial", 16, "bold"))
        self.title.grid(row=0, column=0, padx=10, pady=0)

        self.artist = tk.CTkLabel(self, text="", font=("Arial", 14))
        self.artist.grid(row=1, column=0, padx=10, pady=0)

        self.album = tk.CTkLabel(self, text="", font=("Arial", 12, "italic"))
        self.album.grid(row=2, column=0, padx=10, pady=0)

    def update_info(self, song_title, artist_name, album_name):
        self.title.configure(text=song_title)
        self.artist.configure(text=artist_name)
        self.album.configure(text=album_name)

    def clear_info(self):
        self.update_info("No song playing", "", "")

    def shorten_text(self, text, length=30):
        return text if len(text) <= length else text[:length] + "..."


class RightSide(tk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.song_info = SongInfo(self)
        self.song_info.grid(row=0, column=0, padx=5, pady=10)

        self.primary_actions = PrimaryActions(self)
        self.primary_actions.grid(row=1, column=0, padx=20, pady=5)

        self.secondary_actions = SecondaryActions(self)
        self.secondary_actions.grid(row=2, column=0, padx=5, pady=5)


class App(tk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x300")
        self.title("DeskThing")
        self.resizable(False, False)



        if not logic.is_authenticated():
            self.auth_button = tk.CTkButton(self, text="Authenticate with Spotify", command=self.authenticate)
            self.auth_button.grid(row=0, column=0, padx=10, pady=10)
        else:
            self.initiate_gui()

    def authenticate(self):
        #Triggers the Spotify authentication flow.
        print("Authenticating with Spotify...")
        logic.authenticate_with_spotify()
        self.auth_button.destroy()  # Remove the button after clicking
        self.initiate_gui()

    def update_album_cover(self, image_path="cover.png"):
        #image = Image.open(f'assets/{image_path}')

        # Set label size (e.g., 250x250)
        #label_width = 250
        #label_height = 250

        # Resize the image to fit the label
        #image = image.resize((label_width, label_height))

        # Convert the image to PhotoImage format, which is compatible with CTkLabel
        #photo_image = tk.CTkImage(image)

        # Update the album cover label with the resized photo image
        photo_image = tk.CTkImage(Image.open(root_dir / "assets" / image_path), size=(250, 250))

        self.album_cover.configure(image=photo_image)
        self.album_cover.image = photo_image

    def initiate_gui(self):
        self.album_cover = tk.CTkLabel(self, text="", width=250, height=250)
        self.album_cover.grid(row=0, column=0, padx=10, pady=10)

        self.right_side = RightSide(self)
        self.right_side.grid(row=0, column=1, padx=10, pady=10)

        self.update_song_info_loop()

    def update_song_info_loop(self):
        # Starts a loop to check and update the song info.
        def update():
            while True:
                try:
                    current_track = logic.get_current_track()
                    if current_track:
                        # If a song is playing, update song info and album cover
                        title = self.right_side.song_info.shorten_text(current_track["item"]["name"], 30)
                        artist = self.right_side.song_info.shorten_text(", ".join([artist["name"] for artist in current_track["item"]["artists"]]), 35)
                        album = self.right_side.song_info.shorten_text(current_track["item"]["album"]["name"], 40)
                        cover_url = current_track["item"]["album"]["images"][0]["url"]


                        if self.right_side.primary_actions.is_playing != logic.is_playing():
                            self.right_side.primary_actions.is_playing = logic.is_playing()
                            self.right_side.primary_actions.play_pause.configure(
                                image=get_image("pause.png") if self.right_side.primary_actions.is_playing else get_image("play.png"))


                        if self.right_side.secondary_actions.is_shuffled != logic.is_shuffled():
                            self.right_side.secondary_actions.is_shuffled = logic.is_shuffled()
                            self.right_side.secondary_actions.shuffle.configure(
                                image=get_image("shuffle.png") if self.right_side.secondary_actions.is_shuffled else get_image("shuffle_false.png"))

                        if self.right_side.secondary_actions.is_liked != logic.is_liked():
                            self.right_side.secondary_actions.is_liked = logic.is_liked()
                            self.right_side.secondary_actions.like.configure(
                                image=get_image(
                                    "heart_full.png") if self.right_side.secondary_actions.is_liked else get_image(
                                    "heart_empty.png"))

                        if  current_track["item"]["name"] != self.right_side.song_info.title.cget("text"):
                            self.right_side.song_info.update_info(title, artist, album)
                            logic.download_album_cover(cover_url, "current_cover.png")
                            self.update_album_cover("current_cover.png")
                    else:
                        # No song playing, clear song info and set default cover
                        self.right_side.song_info.clear_info()
                        self.update_album_cover("cover.png")
                except Exception as e:
                    print(f"Error in song update loop: {e}")
                    self.update_album_cover("cover.png")  # Use default cover on error

                time.sleep(2)

        threading.Thread(target=update, daemon=True).start()


app = App()
app.configure(fg_color="gray")
app.grid_columnconfigure((0, 1), weight=1)
app.mainloop()