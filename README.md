# TF Tracker 🤖

A local web app for tracking your Transformers figure collection — accessories, completion status, photos and all.

![TF Tracker screenshot](assets/screenshot.png)

Built for collectors who want full control of their data without cloud services or subscriptions.

![Transformers G1](https://img.shields.io/badge/Generations-G1%20to%20TR-red?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-local-green?style=flat-square)

---

## Features

- **18 series** pre-loaded — G1 through Titans Return (2,600+ figures)
- Track accessories and parts per figure (have / missing)
- Upload photos for each figure and accessory
- Filter by faction (Autobot / Decepticon), status, type
- Sidebar navigation between collections
- PDF export per series
- 100% local — no internet required after setup

---

## Requirements

Before you start, you need **Python** installed on your computer.

👉 Download Python here: https://www.python.org/downloads/

> **Important:** During installation, check the box that says **"Add Python to PATH"**

---

## Installation

### Windows

1. Download this project — click the green **Code** button above, then **Download ZIP**
2. Unzip the folder somewhere on your computer (e.g. your Desktop)
3. Open the folder and double-click **`install.bat`**
4. The installer will set everything up automatically
5. When it's done, click **j** to launch the app — it opens in your browser

That's it. A shortcut called **TF Tracker** is also created on your Desktop for next time.

---

### macOS / Linux

1. Download this project — click the green **Code** button above, then **Download ZIP**
2. Unzip the folder and open Terminal inside it
3. Run:
```bash
bash install.sh
```
4. The app opens automatically at http://localhost:5000

---

### Starting the app after installation

**Windows** — double-click **`TF Tracker.bat`** (or use the Desktop shortcut)

**macOS / Linux** — run `python app.py` in the project folder

---

### Shutting down the app

Click the **⏻** button in the top right corner of the app, or press **Ctrl+C** in the terminal window.

---

## Your data

All your collection data is stored locally on your computer — nothing is sent online.

| What | Where |
|------|-------|
| All figures, accessories, status | `tracker.db` |
| All uploaded photos | `images/` folder |

> **Backup tip:** Copy both `tracker.db` and the `images/` folder to keep your collection safe.

> If you ever delete `tracker.db` by mistake, run `python seed.py` to recreate it with all figures.

---

## Series included

| Series | Short | Years | Figures |
|--------|-------|-------|---------|
| Generation 1 | G1 | 1984–1990 | 344 |
| Generation 2 | G2 | 1993–1995 | 93 |
| Beast Wars | BW | 1996–2001 | 114 |
| Beast Machines | BM | 2000–2001 | 61 |
| Robots in Disguise | RID01 | 2001–2003 | 73 |
| Armada | ARM | 2002–2003 | 64 |
| Energon | ENE | 2003–2005 | 84 |
| Cybertron | CYB | 2005–2006 | 118 |
| Movie (2007) | MOV1 | 2007–2008 | 194 |
| Animated | ANI | 2008–2010 | 88 |
| Movie – ROTF | ROTF | 2007–2010 | 213 |
| Movie – DOTM | DOTM | 2011–2012 | 154 |
| Prime | PRI | 2011–2020 | 166 |
| Movie – AOE | AOE | 2013–2014 | 87 |
| Robots in Disguise 2015 | RID15 | 2015–2017 | 290 |
| Movie – TLK | TLK | 2017–2018 | 104 |
| Combiner Wars | CW | 2015–2018 | 73 |
| Titans Return | TR | 2016–2018 | 76 |

---

## Contributing

Pull requests welcome! Useful contributions:

- Missing figures or accessories
- Bug fixes
- UI improvements
- Additional series (Power of the Primes, War for Cybertron etc.)

Please open an issue before starting larger changes.

---

## License

MIT — free to use, modify and distribute.
