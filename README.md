![Python](https://img.shields.io/badge/Python-3.12-blue)

# 🐦 Flappy Bird Python

A Python implementation of the classic Flappy Bird game with enhanced features and multiple game screens.

> [!CAUTION]
> **This source requires Python version 3.12.x strictly.**
>
> - Ensure you have Python 3.12.x installed before proceeding. Using any other version may result in critical errors or unexpected behavior.
> - [Download Python 3.12.x](https://www.python.org/downloads/) if you do not already have it installed.

### ⚠️ Windows Executable Download Instructions

> [!CAUTION]
> **How to run on Windows:**
>
> - **Version 2.0.0 and below:**  
>   Download the all-in-one `.exe` file and run it directly. All assets are bundled inside the executable.
>
> - **Version 2.1.0 and above:**  
>   Download the provided `.zip` file, extract all contents, and then run the `.exe` inside the extracted folder.  
>   This method is safer for Windows and ensures all assets and dependencies are loaded correctly.
>
> If you encounter issues running the executable, make sure your antivirus is not blocking it and that you have extracted all files before launching.

## 📦 Requirements

* Python 3.12 (strictly required)
* [`pygame`](https://pypi.org/project/pygame/)
* [`uv`](https://pypi.org/project/uv/) for dependency management

## 🚀 Getting Started

Clone this repo and install the requirements:

```bash
pip install uv
```

Sync dependencies using:

```bash
uv sync
```

Then run the game:

```bash
uv run main.py
```

## 🎮 How to Play

- Press SPACE to make the bird flap
- Avoid the pipes
- Try to get the highest score possible

## 🎯 Features

- **Multiple Game Screens:**
  - Main Menu Screen
  - Game Screen
  - Game Over Screen
  - Settings Screen
  - Stats Screen
  - Loading Screen

- **Game Elements:**
  - Different bird colors (yellow, red, blue)
  - Day and night backgrounds
  - Green and red pipes
  - Sound effects

- **Settings:**
  - Customizable game settings
  - Audio control options

## 📁 Project Structure

```
├── main.py                  # Main entry point
├── assets/                  # Game assets (sprites, audio)
│   ├── sprites/
│   └── audio/
└── src/                     # Source code
    ├── constants.py         # Game constants
    ├── objects.py           # Game objects
    ├── settings.py          # Game settings
    ├── ui_constants.py      # UI constants
    ├── ui.py                # UI components
    └── screens/             # Different game screens
        ├── game_screen.py
        ├── game_over_screen.py
        ├── loading_screen.py
        ├── main_menu_screen.py
        ├── settings_screen.py
        └── stats_screen.py
```

## 🎨 Assets

Game assets are from [samuelcust/flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets).

## 📈 Future Improvements

- Online leaderboard
- Additional game modes
- Character customization options

https://github.com/user-attachments/assets/7c9d51fc-61c8-4ba0-aa08-0544a38d2b2b
