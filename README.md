# The World in One Day — Friday 27 November 2026

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/JohnyKucel/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/JohnyKucel/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A single-image broadsheet front page for the make.fun
[news-image-20261127](https://make.fun/bounty/news-image-20261127) bounty:
**Friday 27 November 2026 — 35 dated stories, 8 regions.**

Lead story: China stocks surge as Beijing unleashes the "national team"
— Shanghai +3.3%, its sharpest one-day rise in over two years, STAR 50
+12%. Around it: the Hormuz tanker death confirmed, Merz aiming for an
EU budget deal before year-end, Tokyo core inflation at 2.9%, a Kosdaq
jump of 6.7%, and Bitcoin holding $61,637 as $7bn in options expire
(BTC $61,637 · ETH $1,734 · SOL $73.09 · Fear & Greed 12, Extreme Fear).

Every story on the page happened on, or was first reported on, Friday
27 November 2026. A red DATE CHECK box lists what was left out on
purpose — the Kuwait drone attack (26 Nov, it led yesterday's paper),
the COP31 collapse (22 Nov), and more.

## Build

```sh
python3 build_assets.py   # Pillow only: pre-renders every tile into assets/
python3 main.py           # stdlib only: assembles assets/ into out/entry.png
```

`out/entry.png` is 1024×1024, deterministic — run `main.py` twice and the
SHA-256 is identical. No timestamps, no randomness, no network.

## Design

Built with the winner package: a giant serif date as masthead, a region
bar with counts, a UTC strip, 13 flat-geometric illustrated cards (no
faces), a 22-brief ALSO ON list, a world map with plain pins, a numbers
strip, a CRYPTO NEWS band, a DATE CHECK box, and a trust badge
(CONFIRMED / OFFICIAL / REPORTED / CLAIM) plus a source under every
story. Classic broadsheet on newsprint `#F1ECE0`, ink `#111111`, one
spot red.
