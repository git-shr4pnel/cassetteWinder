from os.path import exists
from os import mkdir
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Tape:
    def __init__(self, length, name):
        self.length = length
        self.name = name
        self.tracks = []
        self.time_elapsed = 0
        self.side = 0

    def __str__(self):
        return f"{self.name}\n{self.tracks}"

    def add(self, track_name, track_minutes, track_artist):
        new_song = Song(track_name, track_minutes, track_artist)
        if new_song.length / 1000 + self.time_elapsed > self.length/2*60-300:
            if self.side == 0:
                query = input(f"Close to the end of side A. Flip cassette? [y/n]\n$ ").lower()
                if query not in {"y", "n"}:
                    query = "y"
                if query == "y":
                    with open(f"tapes/{self.name}.txt", "a") as f_a:
                        f_a.write("SIDE B\n\n")
                    print("Now writing to side B")
                    self.time_elapsed = 0
                    self.side = 1
                    return 0
            else:
                query = input(f"Close to the end of side B. Finalize tracklist? [y/n]\n$ ").lower()
                if query not in {"y", "n"}:
                    query = "y"
                if query == "y":
                    print("DONE")
                    with open(f"tapes/{self.name}.txt", "a") as f_a:
                        f_a.write("\n\nEND")
                return 1
        self.tracks.append(new_song)
        with open(f"tapes/{self.name}.txt", "a") as f_a:
            f_a.write(str(new_song))
        self.time_elapsed += new_song.length
        print(f"{display_time(self.time_elapsed)}/{self.length//2} minutes passed")
        return 0


class Song:
    def __init__(self, name, length, artist):
        self.name = name
        self.length = length
        self.artist = artist

    def __str__(self):
        return f"{self.name}, {self.artist}, {display_time(self.length)}\n"


def display_time(length):
    minutes = length / 1000 // 60
    seconds = length / 1000 % 60
    return f"{int(minutes)}:{round(seconds)}"


def dir_check(tape):
    if not exists("tapes"):
        mkdir("tapes")
        with open(f"tapes/{tape.name}.txt", "w") as f_w:
            f_w.write(f"{tape.name}: {tape.length} minutes\n\n")
        return 1
    if exists(f"tapes/{tape.name}.txt"):
        print("This name is already in use. Enter a new name")
        return 0
    with open(f"tapes/{tape.name}.txt", "w") as f_w:
        f_w.write(f"{tape.name}: {tape.length} minutes\n\n")
    return 1


def instantiate_tape():
    while 1:
        try:
            length = int(input("How many minutes long is your cassette?\n$ "))
            break
        except ValueError:
            print("That's not a valid number. Try again.")
    success = 0
    while not success:
        name = input("What do you want to call this mixtape?\n$ ")
        tape = Tape(length, name)
        success = dir_check(tape)
    with open(f"tapes/{tape.name}.txt", "a") as f_a:
        f_a.write("SIDE A\n\n")
    return tape


def length_format_check(length):
    if ":" not in length:
        print("Invalid, no colon found.")
        return 1
    for n, character in enumerate(length):
        if character == ":":
            minute_digits = n + 1
            break
    # if the format does not fit format M:SS return 1 (indicating failure)
    try:
        int(length[minute_digits:])
        int(length[-1])
        digit = int(length[-2])  # tests for impropper formatting
        if digit > 5:
            raise ValueError
    except ValueError:
        print("Invalid, did you make a typo?")
        return 1
    return 0


def find_songs(sp):
    i = 0
    while 1:
        query = input("What's the name of your song?\n$ ")
        while 1:
            try:
                results, n = sp.search(q=query, limit=5, offset=i), 0
                for n, item in enumerate(results["tracks"]["items"]):
                    print(f"[{n + 1}] {item['name']}: {item['album']['name']} by {item['artists'][0]['name']}")

                if item is None:
                    print("No results found.")
                    raise ValueError
                num_query = int(input("Which one of these songs match your query? For more results, enter 0. "
                                      "To search again enter nothing.\n$ "))
                if num_query > n+1 or num_query < 0:
                    print("Invalid. Please try again.")
                    raise ValueError
                if num_query == 0:
                    print("Retrying...")
                    i += 5
                    raise RuntimeError
                return \
                    results["tracks"]["items"][num_query-1]["name"], \
                    results["tracks"]["items"][num_query-1]["duration_ms"], \
                    results["tracks"]["items"][num_query-1]["artists"][0]["name"]
            except ValueError:
                break
            except RuntimeError:
                continue
            except spotipy.exceptions.SpotifyException:
                print("Invalid search, try again.")
                break


def tracklist(tape):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    while 1:
        try:
            name, length, artist = find_songs(sp)
            done = tape.add(name, length, artist)
            if done:
                break
        except RuntimeError:
            print("The length of your song did not fit the M:SS format. Try again")
            continue


def main():
    tape = instantiate_tape()
    tracklist(tape)


if __name__ == "__main__":
    main()
