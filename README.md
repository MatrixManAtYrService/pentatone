This is a rudamentary guitar simulator.  It makes sounds.

### Setup with Nix

1. `git clone git@github.com:MatrixManAtYrService/pentatone`
2. `cd pentatone`
3. `nix develop` (dependencies are handled in [flake.nix](flake.nix))

### Setup Elsewhere

1. install [ffmpeg](https://www.ffmpeg.org/)
2. `git clone git@github.com:MatrixManAtYrService/pentatone`
3. `cd pentatone`
4. install [pydub](https://github.com/jiaaro/pydub) (a virtual environment is recommended)

### Windows Notes

I ended up installing `ffmpeg` on Windows via [scoop](https://github.com/ScoopInstaller/Scoop):
```
PS C:\Users\matt\src\pentatone> scoop install ffmpeg
```

Also, in order to avoid permissions errors I had to install pyaudio into the venv (alongside pydub, which is defined in `requirements.txt`):

```
PS C:\Users\matt\src\pentatone> python -m venv venv
PS C:\Users\matt\src\pentatone> .\venv\Scripts\Activate.ps1
(venv) PS C:\Users\matt\src\pentatone> pip install -r .\requirements.txt
(venv) PS C:\Users\matt\src\pentatone> pip install pyaudio
```

I'm not sure why pyaudio was necessary.  Thanks to [this comment](https://stackoverflow.com/questions/44215734/python-pydub-permission-denied#comment135740281_57634935).


After these steps, I could make sounds happen:

```
(venv) PS C:\Users\matt\src\pentatone> python .\tone.py --string 1 --fret 7 --overtones --scale
String 1, Fret 7: 122.86118030388789 Hz
String 1, Fret 10: 146.10738977501563 Hz
String 2, Fret 7: 164.81377845643496 Hz
String 2, Fret 9: 184.9972113558172 Hz
String 3, Fret 7: 220.25114030087218 Hz
String 3, Fret 9: 247.22354608459207 Hz
(venv) PS C:\Users\matt\src\pentatone>
```

### Some commands to try

```shell
python tone.py
python tone.py --string 2 --fret 5
python tone.py --string 2 --fret 5 --overtones
python tone.py --string 2 --fret 5 --overtones --scale
```
