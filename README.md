# news-image-20261125 — The World in One Page

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Apizairdrop/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Apizairdrop/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A make.fun entry for [news-image-20261125](https://make.fun/bounty/news-image-20261125):
sum up Wednesday 25 November 2026's world news in one image.

## The image

`entry.png` is a coded flat front page, 1024×1024, drawn by `main.py`
(pure Python standard library — no network, no font files on disk: a
hand-rolled 5×7 bitmap font and a zlib PNG writer). It holds:

- Masthead + date: Wednesday 25 November 2026
- Main headline: tariff threat sinks Asia stocks (Reuters, 25 Nov)
- Schematic world map with the 16 lead stories numbered on it
- 16 leads, each with its own date and named source
- A UTC timeline of the day
- 36 more briefs from every region
- A market box (KOSPI, TWII, Nikkei, Nasdaq, Dow, NVDA, BTC, ETH, Brent)
- A date-check footer and a named source list

## Date-check

Every story on the page carries its own date. The main headline, the Asia
markets story and the Kyiv confirmation were first reported on 25 November
2026. Stories marked 24 Nov happened or were first reported on Tuesday
24 November 2026 and are labelled with that date. Nothing on the page is
older than 24 November 2026.

## Run it

```sh
python3 main.py                              # writes ./entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py       # writes out/entry.png
```

Two runs write byte-identical files (verified by SHA256). The program runs
with no network and writes only `entry.png` to the output directory.

## License

MIT — see [LICENSE](LICENSE).
