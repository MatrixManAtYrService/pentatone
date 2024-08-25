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

### Some commands to try

python tone.py
python tone.py --string 2 --fret 5
python tone.py --string 2 --fret 5 --overtones
python tone.py --string 2 --fret 5 --overtones --scale
