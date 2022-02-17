from os.path import exists
from os import mkdir


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
        if new_song.secs_convert() + self.time_elapsed > self.length/2*60:

            if self.side == 0:
                query = input(f"The song is too long to fit on this side! You only have "
                              f"{round(self.length/2-self.time_elapsed)} "
                              f"minutes left. Flip side? [y/n]\n$ ").lower()
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
                query = input(f"The song is too long to fit on this side! You only have "
                              f"{round(self.length/2-self.time_elapsed)} minutes left. "
                              f"Finalise tracklist? [y/n]\n$ ").lower()
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
        self.time_elapsed += new_song.secs_convert()
        print(f"{round(self.time_elapsed/60)}/{self.length//2} minutes passed")
        return 0


class Song:
    def __init__(self, name, length, artist):
        self.name = name
        self.length = length
        self.artist = artist

    def __str__(self):
        return f"{self.name}, {self.artist}, {self.length}\n"

    def secs_convert(self):
        for n, character in enumerate(self.length):
            if character == ":":
                minute_digits = n
                break
        # this return statement is getting slices of the numbers before and after the colon and turning it all into
        # seconds. It does this by counting how many loops are needed to get to the divider between mins & secs
        return int(self.length[:minute_digits])*60 + int(self.length[minute_digits + 1:])


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
    for n, character in enumerate(length):
        if character == ":":
            minute_digits = n + 1
    # if the format does not fit format M:SS return 1 (indicating failure)
    try:
        int(length[:minute_digits])
        int(length[-1])
        digit = int(length[-2])  # tests for impropper formatting
        if digit > 5:
            raise ValueError
        if ":" not in length:
            raise RuntimeError
    except ValueError:
        print("Invalid, did you make a typo?")
        return 1
    except RuntimeError:
        print("Invalid, no colon found.")
        return 1
    return 0


def tracklist(tape):
    while 1:
        try:
            name = input("What's the name of your song?\n$ ")
            length = input("How long is the song? (format M:SS, i.e 2:33)\n$ ")
            failure = length_format_check(length)
            if failure:
                raise RuntimeError
            artist = input("What's the name of the artist?\n$ ")
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
