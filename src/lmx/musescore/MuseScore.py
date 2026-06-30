from pathlib import Path
import urllib.request
import os
import stat


class MuseScore:
    """Represents a MuseScore executable file"""
    def __init__(self, executable_path: Path, version: str):
        self.executable_path = executable_path
        """Path to the MuseScore executable"""

        self.version = version
        """Version of the MuseScore used, e.g. `4.6.5`"""

    @staticmethod
    def resolve_linux_default():
        """Installs and references the default MuseScore 4.6.5
        AppImage in the 'musescore/' folder, relative to
        the current working directory."""
        
        musescore_directory = Path("musescore")
        musescore_directory.mkdir(exist_ok=True)

        ms = MuseScore(
            executable_path=musescore_directory \
                / "MuseScore-Studio-4.6.5.253511702-x86_64.AppImage",
            version="4.6.5",
        )

        # download if not downloaded yet
        if not ms.executable_path.exists():
            print("Downloading MuseScore to", ms.executable_path, "...")
            urllib.request.urlretrieve(
                url="https://github.com/musescore/MuseScore/releases/download/v4.6.5/MuseScore-Studio-4.6.5.253511702-x86_64.AppImage",
                filename=ms.executable_path,
                reporthook=lambda blocknum, bs, size: \
                    print(f"Downloaded {round((blocknum * bs) / size * 10000) / 100}% ...\r", end="")
            )
            
            # make executable for everyone ($> chmod +x)
            mode = os.stat(ms.executable_path).st_mode
            os.chmod(
                ms.executable_path,
                mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )
            print("MuseScore downloaded.")
        
        return ms
