# Viofo A129 Plus Duo - Beep detector

This was done for a friend's Viofo A129 Plus Duo dashcam so it will probably not work for you (unless you're that guy and in that case: **HIIIIIII!**).

It will take input folder full of mp4 files and will try to detect two distinct beeps in pair of two beeps and record the timestamp when that happened in the video. That's for when that ~~guy~~ friend presses the magic *remember this moment* button on Viofo A129 Plus Duo dashcam it will store and lock that recording. He then does some video editing magic  with it so this tool ~~helps~~ will help him a lot in the process, I guess.

# How to install

## Release
1. Grab one from [releases page](https://github.com/jdolinar/viofo-video-beep-detector/releases)
2. Install or unpack
3. Click on icon on Desktop or Start Menu
4. PROFIT!

## Source
1. Get [latest Python](https://www.python.org/downloads/)
2. (if that happens) Return live python to pet store and repeat step 1
3. Run ```python3 -m .venv .venv```
4. Activate venv environment as per [python venv docs](https://docs.python.org/3/library/venv.html) (search for **Command to activate virtual environment**)
5. Run ```python3 beep_detection.py [folder full of your mp4 files] [output text file]```
6. PROFIT!

Send beer or coffee!
