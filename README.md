# Extension Overview
This is a Chrome extension for controlling MahjongSoul using a keyboard. 
https://github.com/KantaHasegawa/mahjong-soul-keyboard
This script is essential for the extension to function. 
It captures the game's play screen from the extension, analyzes the image to determine the current hand situation, and notifies the Chrome extension. 
As a result, you can enjoy smooth keyboard operations regardless of how many times you call tiles.

# Requirements
- Python3
- OpenCV
- Port 8090 open on the local machine

# HowToUse
1. `git clone git@github.com:KantaHasegawa/mahjong-soul-keyboard-backend.git`
2. `cd mahjong-soul-keyboard-backend`
3. `python3 main.py`

With this, the Chrome extension will operate correctly when launched.

