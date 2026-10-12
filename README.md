# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a little shopping agent for second-hand clothes. You ask for
something in plain language, like "vintage graphic tee under $30" and it
searches the thrift listings for items that match your words, your size, and
your price limit. It then picks the best match, suggests an outfit using clothes already in your wardrobe, and writes a short caption (a "fit card") you could post about the find. If nothing matches, it stops early and tells you what to change instead of making something up.

<!-- Scratch notes for myself (Milestone 1):

A listing has 11 fields: id, title, description, category, style_tags
(list), size, condition, price (float), colors (list), brand (str OR None),
platform.

- size is messy: "W30 L30", "S/M", "M/L", "XL (oversized)", "US 9",
"One Size". A plain substring test is a trap. "s" in "us 9" is True,
"l" in "xl" is True. Be careful in search_listings.
- brand is None for a lot of listings. Don't assume it's always there.
- 40 listings, 5 categories (tops, bottoms, outerwear, shoes, accessories), 3 platforms (depop, thredUp, poshmark).
- Empty wardrobe is {"items": []}, so suggest_outfit has to survive that. -->


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Looks through all the thrift listings and returns the ones
  that match the user's keywords, and, when they are given, their size and price
  limit. It scores each listing by how many of the description words overlap with
  the listing's title, description, and style tags, then sorts best match first.
- **Inputs:** `description` (str, the keywords), `size` (str or None, which
  skips size filtering when None), `max_price` (float or None, an inclusive
  ceiling, skipped when None).
- **Returns:** A list of listing dicts, best match first (at most
  `SEARCH_RESULT_LIMIT`, which is 10). Each dict has the full listing fields:
  `id, title, description, category, style_tags, size, condition, price, colors,
  brand, platform`.
- **When it has nothing:** Returns an empty list `[]`, not `None` and not an
  exception. The loop checks this to decide whether to stop.

<!-- Size matching rule I'm committing to (so it isn't a substring trap): compare
     whole tokens, ignoring case. I split the listing's size on spaces and
     slashes, so "S/M" becomes ["s","m"] and "US 8" becomes ["us","8"], then
     keep the listing only if the requested size is one of those tokens. That
     way "M" matches "S/M" and "M/L" but NOT "XL", and "s" does not match
     "US 9". -->

### `suggest_outfit`

- **What it does:** Takes the item the user is considering and their wardrobe,
  and asks the model for one or two outfit ideas that go with the item.
- **Inputs:** `new_item` (dict, one listing), `wardrobe` (dict with an `items`
  key holding a list of wardrobe items; the list may be empty).
- **Returns:** A string of outfit suggestions that is never empty. When the
  wardrobe has items, it names specific pieces the user already owns; when the
  wardrobe is empty, it gives general styling advice for the item instead.
- **When it has nothing:** If `wardrobe["items"]` is empty, it still returns a
  string that is not empty (general styling advice); it does not return `""` or
  raise.

### `create_fit_card`

- **What it does:** Writes a short caption worth posting about the find, based on
  the item and the outfit suggestion.
- **Inputs:** `outfit` (str, the suggestion from `suggest_outfit`), `new_item`
  (dict, the listing).
- **Returns:** A caption of two to four sentences that mentions the item and its
  price and platform once each. Because the model runs with temperature,
  different items give different captions.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns a
  short descriptive message instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, I put a message in
`session["error"]` that names what the user could change and return the session
right away, without calling `suggest_outfit`. Otherwise I take the first result
(the best scoring one) as `session["selected_item"]` and carry on to
`suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** String handling with two small regexes, not the
model. A helper called `parse_query` in `agent.py` pulls out `max_price` (a number
after "under", or any "$NN"), `size` (the token after the word "size"), and uses
whatever text is left over as the `description`.

**What moves through the session:** The fields fill in this order: `query` (what
the user typed), then `parsed` (description, size, max_price), then
`search_results`, then `selected_item`, then `outfit_suggestion`, then
`fit_card`. If the search comes back empty, `error` is set instead and every
field after `search_results` stays `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask "vintage graphic tee under $30"

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair your new Y2K baby tee with the baggy straight-leg jeans and
            chunky white sneakers for a cute, casual throwback look. Throw on the
            black cropped zip hoodie if you need an extra layer!

  Fit card: Obsessed with this Y2K butterfly tee I just scored! It's yours on
            Depop for just $18.00. Pair it with baggy jeans and chunky sneakers
            for the ultimate throwback fit! ✨🦋

2 model calls this session, 326 prompt + 86 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; r=search_listings('graphic tee', max_price=30); print(len(r), 'results, best first:'); [print(' ', x['id'], '|', x['title'], '| $'+str(x['price']), '|', x['size']) for x in r]"
7 results, best first:
  lst_002 | Y2K Baby Tee — Butterfly Print | $18.0 | S/M
  lst_006 | Graphic Tee — 2003 Tour Bootleg Style | $24.0 | L
  lst_017 | Mesh Long-Sleeve Top — Black | $15.0 | S/M
  lst_033 | Vintage Band Tee — Faded Grey | $19.0 | L
  lst_011 | Low-Rise Cargo Pants — Khaki | $27.0 | W29
  lst_012 | Oversized Crewneck Sweatshirt — Vintage Navy | $20.0 | XL (fits oversized)
  lst_015 | Vintage Graphic Hoodie — Faded Black | $26.0 | L
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey there! Those vintage Levi's 501 jeans are such a great find.

Try pairing your new medium wash jeans with the white ribbed tank top, black cropped zip hoodie, and chunky white sneakers for an easy, casual streetwear look.

For a cooler day, throw the vintage black denim jacket over the grey crewneck sweatshirt, tuck the crewneck into the jeans with your brown leather belt, and finish it off with your black combat boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Score! Just hunted down these vintage Levi's 501 jeans in the absolute best medium wash. They can be yours on Depop right now for just $38.00! I'm styling mine with a crisp pair of white sneakers for the ultimate effortless weekend fit. Grab them before I change my mind and keep them!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* A way to filter listings by size that would not fall for
  the substring trap the starter warned about, where "s" matches "us 9" and "l"
  matches "xl".
- *What came back:* The idea to split each listing's size on spaces and slashes
  into whole tokens, so "S/M" becomes ["s", "m"] and "US 8" becomes ["us", "8"],
  then keep a listing only when the requested size equals one of those tokens.
- *What I changed:* I put that rule into `search_listings` and tested it. Asking
  for size "M" returned only the S/M tops, with no XL items and no shoes, so I
  kept it and wrote the rule into my Tool Inventory.

**Moment 2**

- *What I asked for:* Help turning a plain query like "vintage graphic tee under
  $30" into a separate description, size, and price.
- *What came back:* A small regex approach for the price and size, plus the
  suggestion to strip the price and size phrases out of the text before using the
  rest as the description, so their numbers do not get treated as keywords.
- *What I changed:* I used that for `parse_query`, but while testing I noticed the
  keyword match still matches substrings inside other words (so "tee" can match a
  word that only contains "tee"). The real matches still sort to the top, so I
  left it and used that limitation as the reason my criterion 1 target is 4 of 5
  instead of 5 of 5.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | **MISSED (2/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Produced by `run_eval.py::main` against `agent.py::run_agent`, every scenario in
`scenarios.py` run five separate times with caching off. The whole file is
committed at `results/run_2026-10-11_1825_before.md`. Ten scenarios, fifty runs,
no crashes.

**Reading row 1.** Criterion 1 was revised this unit, and its five tries are
five different phrasings rather than five repeats of one query, so the columns
read left to right as phrasing 1 through phrasing 5:

| Try | Query | Should find | Actually selected | |
|---|---|---|---|---|
| 1 | `levis jeans size 30` | lst_001 Vintage Levi's 501 Jeans | nothing, stopped at step 2 | FAIL |
| 2 | `black bomber jacket` | lst_022 90s Leather Bomber | lst_022 90s Leather Bomber | PASS |
| 3 | `a green silk shirt` | lst_029 Silk Button-Down, Sage Green | lst_024 Vintage Polo Shirt | FAIL |
| 4 | `small tan purse` | lst_039 Mini Shoulder Bag, Tan Leather | lst_002 Y2K Baby Tee | FAIL |
| 5 | `chunky knit cardigan` | lst_008 Oversized Knit Cardigan | lst_008 Knit Cardigan | PASS |

Each phrasing was also run five times and gave the same answer all five times,
so none of this is model variance. `search_listings` has no model in it.

**Why I scored tries 3 and 4 as FAIL.** My criterion says the agent "returns a
fit card", and on a flat reading of those four words tries 3 and 4 passed: a
fit card came back both times. I scored them FAIL anyway, because the criterion
I wrote also has a column headed "the item it should find", and I filled that
column in before I ran anything. Try 4 returned a cheerful caption about a Y2K
butterfly baby tee to someone who asked for a tan purse. Counting that as a
pass would turn the row from MISSED into MET and leave me nothing to diagnose,
which is exactly the move this unit warns about. The looser reading is
available to me and I am not taking it.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

---

#### Criterion 1, try 1: `levis jeans size 30` (FAIL, found nothing)

Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: yes — I couldn't find anything for "levis jeans size 30". Try removing the price limit, using a different size, or simpler keywords.
- selected_item: (none)
- search_results: 0

Trace:
[1] parse_query
      in:  levis jeans size 30
      out: description='levis jeans', size='30', max_price=None
[2] search_listings (via MCP)
      in:  description='levis jeans', size='30', max_price=None
      out: [] (empty)
      →    branch: empty list, stopping before suggest_outfit
```

Two steps and a stop. The agent behaved correctly for what it was handed, an
empty list, and the branch did its job. The problem is upstream: the list
should not have been empty. `lst_001` exists, it is a pair of Levi's jeans, and
its size is `W30 L30`.

---

#### Criterion 1, try 4: `small tan purse` (FAIL, found the wrong thing)

Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 5

Fit card:
Obsessed with this adorable Y2K baby tee featuring the cutest butterfly print! Score it on my Depop for just $18.00 before someone else snatches it up. Pair it with baggy jeans and chunky sneakers for the ultimate nostalgic fit! ✨🦋

Trace:
[1] parse_query
      in:  small tan purse
      out: description='small tan purse', size=None, max_price=None
[2] search_listings (via MCP)
      in:  description='small tan purse', size=None, max_price=None
      out: 5 items: Y2K Baby Tee — Butterfly Print, Crochet Halter Top — Cream, Suede Chelsea Boots — Tan … +2 more
      →    branch: 5 results, carrying on
[3] select_item
      in:  5 results, taking index 0
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item id is lst_002
[4] suggest_outfit
      in:  item lst_002, wardrobe with 10 items
      out: Pair your butterfly Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for an easy, nost…
[5] create_fit_card
      in:  item lst_002, outfit of 219 chars
      out: Obsessed with this adorable Y2K baby tee featuring the cutest butterfly print! Score it on my Depop for just $…
[6] done
      →    all three tools ran, returning the session
```

This is the one worth looking at twice. Nothing errored. All six steps ran,
`selected_item` travelled through the session intact, and the caption is
perfectly well written. It is also about a butterfly baby tee, and the user
asked for a tan purse. Every criterion except this one would call this run a
success.

---

#### Criterion 2: an impossible query stops before the second tool

Scenario `impossible query stops early`, query `designer ballgown size XXS under $5`.
Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: yes — I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.
- selected_item: (none)
- search_results: 0

Trace:
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty list, stopping before suggest_outfit
```

How I read it: the trace stops at step 2. There is no `suggest_outfit` step at
all, `selected_item` is `(none)`, and the message names three things the user
could change. The scenario reported `0 model calls`, which is the part I trust
most, because `suggest_outfit` cannot have run without calling the model. Same
on all five tries. **5 of 5, target was 5 of 5, MET.**

---

#### Criterion 3: the item found is the item that gets styled

Scenario `selected item is the item styled`, query `90s track jacket in size M`.
Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: no
- selected_item: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
- search_results: 4

Trace:
[1] parse_query
      in:  90s track jacket in size M
      out: description='90s track jacket in', size='M', max_price=None
[2] search_listings (via MCP)
      in:  description='90s track jacket in', size='M', max_price=None
      out: 4 items: 90s Track Jacket — Navy/White Stripe, 90s Leather Bomber — Black, 90s Silk Slip Dress — Floral, Midi Length … +1 more
      →    branch: 4 results, carrying on
[3] select_item
      in:  4 results, taking index 0
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    selected_item id is lst_004
[4] suggest_outfit
      in:  item lst_004, wardrobe with 10 items
      out: Layer the 90s Track Jacket over your white ribbed tank top and pair it with the baggy straight-leg jeans and c…
[5] create_fit_card
      in:  item lst_004, outfit of 330 chars
      out: Scored this ultimate 90s Track Jacket in navy and white for just $45.00 on Poshmark, and I’m so obsessed! Thro…
[6] done
      →    all three tools ran, returning the session
```

How I read it: my criterion says to compare `session["selected_item"]["id"]`
against the item going into `suggest_outfit`. Step 3 prints
`selected_item id is lst_004` and step 4 prints `item lst_004` as its input.
Those are the two values the criterion names and they are the same string. All
five tries printed `lst_004` in both places. **5 of 5, target was 5 of 5, MET.**

I added those two ids to the trace in Milestone 2 so this criterion could be
read off the output instead of taken on trust. It is worth noting what this
criterion does **not** say: it says the item that was selected is the item that
got styled, and it says nothing about whether the right item was selected in
the first place. Criterion 1 try 4 passes criterion 3 perfectly while styling a
baby tee for someone shopping for a purse.

---

#### Criterion 4: the fit card names the price

Scenario `fit card names the price`, query `silk slip dress in midi length under $40`.
The top result is `lst_013` at `$30.0`, so I am looking for `30` in the caption.
All five captions from `tools.py::create_fit_card`, via `run_eval.py::run_once`:

```
Try 1: Absolute 90s dream find! 🌸✨ I’m obsessed with this floral midi silk slip dress and can't believe I scored it for just $30.00. Grab it now over on my Depop before I change my mind and keep it for myself!
Try 2: Found the ultimate 90s dream! 🌸 This gorgeous floral midi slip dress is giving all the nostalgic vibes and is up for grabs on Depop for just $30. Grab it before it's gone and go live your best vintage life!
Try 3: Found the ultimate 90s silk slip dress and I am obsessed! 🌸✨ Grab this gorgeous floral midi for just $30.00 over on my Depop before it’s gone. Style it over a white tee with chunky sneakers for the weekend, or throw an oversized crewneck and combat boots right over it when it gets chilly!
Try 4: Obsessed with this 90s silk slip dress I just thrifted! Layer it over a white tee with chunky sneakers for daytime, or throw on an oversized crewneck and combat boots when it gets chilly. Grab this floral midi on my Depop right now for just $30! ✨👗
Try 5: Obsessed with this 90s silk slip dress! 🌸 Throw it on over a white tee with chunky sneakers for an easy daytime look, or layer an oversized crewneck and combat boots when it gets chilly. Grab this floral midi on my Depop right now for just $30.00!
```

How I read it: the price is in all five, written as `$30` and `$30.00`. My
criterion says the number from `new_item["price"]` has to appear somewhere in
the caption, and `30` does every time. **5 of 5, target was 4 of 5, MET.**

I set this at 4 of 5 last unit because I expected the model to round or write
around the number sometimes. Across ten captions for this item over two runs it
has not done it once. The five captions are otherwise all different text, so
this is not the cache handing back one answer.

---

#### Criterion 5: the price ceiling is never crossed

Scenario `price ceiling is never crossed`, query `vintage graphic tee under $30`.

`run_eval.py` records how many results came back but not what they cost, and my
criterion is about **every** listing returned, not just the one that got picked.
Its row in the results file shows `search_results: 10` and a selected item at
`$18.0`, which says nothing about the other nine. So I measured it directly,
five times, reading `session["search_results"]` out of `agent.py::run_agent`
with caching off, the same way `run_eval.py` runs it:

```
try 1: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 2: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 3: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 4: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 5: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
```

The command, so it can be run again:

```
python -c "
import config
config.CACHE_ENABLED = False
from agent import run_agent
from utils.data_loader import get_example_wardrobe
CEILING = 30.0
for attempt in range(1, 6):
    s = run_agent('vintage graphic tee under \$30', get_example_wardrobe())
    prices = [x['price'] for x in s['search_results']]
    over = [p for p in prices if p > CEILING]
    print(f'try {attempt}: {len(prices)} results, prices {sorted(prices)}')
    print(f'         max={max(prices)}  over: {over or \"none\"}')
"
```

How I read it: ten results every try, nothing above the ceiling, and the top
price is exactly `$30.0` every time. That last part is the bit I wanted to see.
My Tool Inventory promised `max_price` was **inclusive**, so an item priced at
exactly the ceiling has to come back, and it does. A filter using `<` instead of
`<=` would have dropped it and still looked like a pass on a careless reading.
**5 of 5, target was 5 of 5, MET.**


## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools *(revised this unit)* | 4 of 5 | **MISSED (2/5)** | Five phrasings, five items I confirmed are in the data. One returned nothing and two returned a fit card for the wrong item. Each phrasing ran five times and gave the same answer every time, so this is not variance. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | The trace stops at step 2 on all five tries, there is no `suggest_outfit` step, and the scenario reported `0 model calls`. `suggest_outfit` cannot run without calling the model, so the count is the proof. |
| 3 | The item found is the item that gets styled | 5 of 5 | MET (5/5) | Compared the two ids the criterion names, `selected_item id is lst_004` at step 3 against `item lst_004` going into step 4. Same string on all five tries. |
| 4 | The fit card names the price | 4 of 5 | MET (5/5) | Read all five captions for `lst_013` at `$30.0`. The number is in all five, as `$30` or `$30.00`. The five captions are otherwise different text, so the cache is not involved. |
| 5 | The price ceiling is never crossed | 5 of 5 | MET (5/5) | Printed every returned price, not just the selected one, five times. Ten results each try, nothing above `$30`, top price exactly `$30.0`, which also confirms the ceiling is inclusive as my Tool Inventory promised. |

**Diagnoses**

Criterion 1 is the only miss, and it missed three of five tries. All three land
in the same place, so this is one problem and not three.

**Where it happened: a tool.** `tools.py::search_listings`. Not the loop, not
the session, not the model. The loop branched correctly every time, including
on the try that found nothing, where it stopped at step 2 exactly as criterion
2 says it should. The session carried the selected item through intact, which
criterion 3 confirms. The model wrote a good caption every time it was asked.
The agent did the right thing with what the search handed it. The search handed
it the wrong thing.

Inside that one tool there are two distinct mechanisms.

---

**Mechanism A, the size filter cannot read a waist size. One try: phrasing 1.**

`levis jeans size 30` returned an empty list. `parse_query` read `size='30'`
correctly, so the parse is fine. The listing it should have found is `lst_001`,
whose size field is the string `W30 L30`.

My size rule, which I wrote last unit and put in my Tool Inventory, splits the
listing's size on spaces and slashes and keeps the listing only if the
requested size equals one of the whole tokens. For `W30 L30` those tokens are
`['w30', 'l30']`. The string `'30'` is not equal to either, so the listing is
dropped before scoring ever happens.

I confirmed it is the size filter and not the keywords by taking the query
apart:

```
search("levis jeans", size="30") -> 0 results
search("levis jeans")            -> 3 results    (lst_001 is one of them)
search("jeans", size="30")       -> 0 results
search("jeans")                  -> 3 results
```

The keywords find the jeans. The size filter then throws them away. And it
throws away **every** pair of jeans in the data, because the bottoms are sized
`W27`, `W28`, `W29`, `W30`, `W30 L30`, `W32`, and a shopper asking for jeans
types `size 30`, not `size W30`.

The painful part is that this rule is not a careless bug. It is the fix I wrote
for the substring trap the starter warned about, where `"s" in "us 9"` is True
and `"l" in "xl"` is True. Whole token matching solves that properly for tops
and shoes. It just has no idea that `W30` means a waist of 30, and I never
tested a bottoms query with a size in it, because my unit 3 sample run was a
tee.

---

**Mechanism B, the score is an unweighted count, so ties are common and get
broken by whatever order the data is in. Two tries: phrasings 3 and 4.**

Both of these returned a fit card and neither of them errored. The right item
was in the results list both times. It just was not first, and
`agent.py::run_agent` takes `search_results[0]`.

`search_listings` scores a listing by counting how many of the query keywords
appear anywhere in its title, description, and style tags. One keyword, one
point. Nothing is weighted, so a match on a decorative word counts exactly as
much as a match on the noun naming the thing.

```
QUERY: 'a green silk shirt'
  picked  lst_024 score=2 matched=['green', 'shirt']  Vintage Polo Shirt — Forest Green
  wanted  lst_029 score=2 matched=['green', 'silk']   Silk Button-Down — Sage Green

QUERY: 'small tan purse'
  picked  lst_002 score=1 matched=['small']           Y2K Baby Tee — Butterfly Print
  wanted  lst_039 score=1 matched=['tan']             Mini Shoulder Bag — Tan Leather
```

Both are exact ties. `matches.sort(key=lambda pair: pair[0], reverse=True)` is
a stable sort, so a tie leaves the two in the order they came out of
`listings.json`, and `lst_024` and `lst_002` are simply earlier in the file.
The agent is not choosing badly. It is not choosing at all.

Phrasing 4 is the one that bothers me most. `lst_002` scored its single point
on the word `small`, which appears in the description as "tag says medium but
fits like a small". The shopper meant small as a size, the data meant small as
a comparison, and a plain substring count cannot tell those apart. Meanwhile
`purse` scored nothing anywhere, because the data says `Mini Shoulder Bag` and
never once says `purse`. That is exactly the phrasing gap I wrote about under
criterion 1 last unit, showing up in the one place I had not thought to look:
not as a zero result, but as a confident answer to a different question.

---

**The pattern, and what it says about the other four criteria.**

Four criteria MET and one MISSED is a flattering split, and the honest reading
is less flattering than it looks.

Criteria 2, 3 and 5 are all deterministic and all passed 5 of 5 across two full
runs. They are worth having, because they are what tells me the MCP move did
not change the shape of anything, and criterion 5 caught the inclusive boundary
I could easily have got wrong. But none of them could have been failed by the
problem criterion 1 just found. Criterion 3 in particular passes *perfectly*
on the try that styled a baby tee for someone shopping for a purse, because it
only asks whether the selected item is the styled item, never whether the
selected item was the right one.

So my five criteria had a hole in them, and it was not a small one: **nothing I
wrote checked whether search returned the right item.** Four of the five
measure that the machinery holds together, and the machinery does hold
together. Only criterion 1 looks at whether the answer is any good, and in its
original wording it did not do that either, which is why I revised it.

**Were my targets too low?** Two of them, yes, on the evidence I now have.
Criterion 4 is set at 4 of 5 and has gone 10 of 10 across two runs, so the
allowance I made for the model rounding the price has not been needed once.
Criterion 3 is set at 5 of 5 and passes trivially, because the value it checks
is moved by a single assignment with nothing in between that could change it.

**The one I would tighten** is criterion 3. As written it compares an id to
itself a few lines later. The version worth having would say that the id in
`session["selected_item"]` is the id of the highest scoring listing for the
query, which would have caught phrasings 3 and 4 and is a claim that can
actually fail. I have not changed it, because tightening a criterion I passed
is not one of the two moves this unit allows, and I would rather say plainly
here which criterion is weak than quietly rewrite it.

---

**What this points at for Milestone 5.** Mechanism A and mechanism B are both
in `search_listings`, and I am allowed one change. They are not equally
valuable:

- Fixing **A** turns phrasing 1 from FAIL to PASS, taking criterion 1 to 3 of 5.
  Still MISSED, but it removes the worst outcome for a user, which is being told
  nothing exists when it does.
- Fixing **B** could turn phrasings 3 and 4 from FAIL to PASS, taking criterion
  1 to 4 of 5 and MET.

B moves the number further. A fixes the more serious failure. I am picking one
in the next section and saying why.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

Produced with `python app.py ask '...' --trace`. The `trace.step()` calls live
in `agent.py::run_agent`, one per stage of the loop.

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace

[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: 10 results, carrying on
[3] select_item
      in:  10 results, taking index 0
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item id is lst_002
[4] suggest_outfit
      in:  item lst_002, wardrobe with 10 items
      out: Pair your new Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for a cute, casual thro…
[5] create_fit_card
      in:  item lst_002, outfit of 187 chars
      out: Obsessed with this Y2K butterfly tee I just scored! It’s yours on Depop for just $18.00. Pair it with baggy je…
[6] done
      →    all three tools ran, returning the session

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair your new Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for a cute, casual throwback look. Throw on the black cropped zip hoodie if you need an extra layer!

  Fit card: Obsessed with this Y2K butterfly tee I just scored! It’s yours on Depop for just $18.00. Pair it with baggy jeans and chunky sneakers for the ultimate throwback fit! ✨🦋

0 model calls this session, 2 served from cache
```

Step 2 is the MCP call. It is the only step that leaves my program: it starts
`mcp_server.py`, asks it for `search_listings`, and shuts it down again. Steps 4
and 5 are still direct calls into `tools.py`.

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5'


  I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.

0 model calls this session
```

Two steps instead of six, and the last line says `0 model calls this session`.
That is the branch doing its job: it reads the empty list at step 2 and returns
before `suggest_outfit` is ever reached, so neither model call happens.

### The three failure modes, triggered on purpose

**1. Empty search.** Already handled before this unit, because it is the branch
criterion 2 is about. Triggered with a query the data cannot match:

```
$ python app.py ask 'designer ballgown size XXS under $5'

  I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.
```

No handler needed. The message names three things the user can actually change,
and the trace above shows the loop stopping at step 2.

**2. Empty wardrobe.** Triggered with the `--empty-wardrobe` flag, which hands
`suggest_outfit` a wardrobe with no items in it:

```
$ python app.py ask 'platform sneakers size 8' --empty-wardrobe

(running with an empty wardrobe)

  Found:    Platform Sneakers — White Chunky Sole — $48.0 on poshmark

  Outfit:   Hey there! Those chunky platform sneakers are such a fun Y2K find. You can easily style them with a simple graphic tee and some cargo pants for a cool streetwear vibe. Or, try pairing them with a denim skirt and a cropped hoodie for the ultimate 90s throwback!

  Fit card: Score! I just found these chunky platform sneakers on Poshmark for only $48, and I am obsessed. They are giving me all the best 90s vibes and I can't wait to style them!

0 model calls this session, 2 served from cache
```

No handler needed either. `suggest_outfit` already checks `wardrobe["items"]`
and switches to a general advice prompt when the list is empty, which is the
empty case I committed to in my Tool Inventory last unit. It returns a real
non empty string and names no pieces the user does not own. With `--trace` the
step reads `wardrobe with 0 items` and notes `empty wardrobe, so general advice`,
so I can see which prompt it took rather than guessing.

**3. Model unavailable.** This is the one that was genuinely broken.

I triggered it by running one command with a deliberately wrong key in front of
it, which beats editing `.env` because there is no way to forget to put the real
key back:

```
GEMINI_API_KEY="AIzaSyBadKeyForTestingOnly_NotARealKey00" python app.py ask 'denim jacket under $50'
```

The query has to be one I have not asked before. An old query comes back out of
the build cache without the model being called at all, and the last line says
`served from cache`, which looks like a pass and proves nothing.

*Before the handler*, calling `run_agent` directly gave a raw stack trace:

```
  File "agent.py", line 201, in run_agent
    session["outfit_suggestion"] = suggest_outfit(
  File "tools.py", line 191, in suggest_outfit
    return generate(prompt, system=system)
  File "generate.py", line 332, in generate
    raise ModelUnavailable(_explain(exc)) from exc
generate.ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

*After the handler*:

```
$ GEMINI_API_KEY="<a wrong key>" python app.py ask 'denim jacket under $50' --trace

[1] parse_query
      in:  denim jacket under $50
      out: description='denim jacket', size=None, max_price=50.0
[2] search_listings (via MCP)
      in:  description='denim jacket', size=None, max_price=50.0
      out: 7 items: Denim Jacket — Light Wash, Cropped, Vintage Levi's 501 Jeans — Medium Wash, 90s Track Jacket — Navy/White Stripe … +4 more
      →    branch: 7 results, carrying on
[3] select_item
      in:  7 results, taking index 0
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      →    selected_item id is lst_007
[4] suggest_outfit
      in:  item lst_007, wardrobe with 10 items
      out: ModelUnavailable
      →    handler: stopping, search results are still good

  I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.

1 model calls this session
```

**What the handler is, and why it reads like that.** I wrapped both model
calling stages in `agent.py::run_agent` in `try` / `except ModelUnavailable`,
and each one puts a message in `session["error"]` and returns the session,
rather than letting the exception escape.

The thing I changed my mind about while writing it was how much to say. My first
message was just "the model could not be reached", and reading it back there was
nothing a user could do with it. So each message now carries the work that did
succeed. The search found a real jacket at a real price before the model died,
and throwing that away makes the failure look total when it is partial. The
fit card handler goes further and prints the whole outfit inside the error,
because by that point two of the three tools have worked and the user should
still get to keep the outfit.

The fit card handler is harder to trigger from the command line, because if the
key is wrong then `suggest_outfit` dies first and the loop never reaches step 5.
I checked it separately by swapping in a `create_fit_card` that raises, which
gave `error set? True`, `outfit kept? True`, `fit_card: None`, and a step 5 in
the trace reading `handler: stopping, outfit is still good`.

**One note on `trace.py`.** My `trace.step()` calls sit inside `run_agent`, so
they run on every query, and a plain `python app.py ask '...'` was printing all
six steps on top of the answer. `app.py` only calls `start_trace()` when you
pass `--trace`, so I added a `_enabled` flag in `trace.py` that `start_trace()`
switches on, and `step()` returns early when it is off. The formatting is
untouched.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I moved `search_listings` onto MCP. It was the easy one to pick because it is
the only tool that doesn't call the model, so nothing is slow and the same query
gives the same answer every time while I was figuring out the shape.

**What changed in my code, in two places.**

1. `mcp_server.py`: I uncommented the `@mcp.tool()` block and registered
   `search_listings` with the same three inputs as my Tool Inventory
   (`description: str`, `size: str | None`, `max_price: float | None`). The body
   just calls `_search_listings_impl`, which is the real function in `tools.py`
   under an alias. The part that took the longest was the description, because
   it has to make sense to someone who can't see my code. I spelled out that
   `max_price` is in whole dollars and inclusive, that `size` is matched as a
   whole token so "M" matches "S/M" but not "XL", and that nothing matching gives
   back `[]` and not `null`.

2. `agent.py`: in `run_agent()`, the search stage used to be a direct call:

   ```python
   results = search_listings(parsed["description"], size=..., max_price=...)
   ```

   and it is now:

   ```python
   results = call_tool("search_listings", {
       "description": parsed["description"],
       "size": parsed["size"],
       "max_price": parsed["max_price"],
   })
   ```

   I also dropped `search_listings` out of the `from tools import ...` line, so
   the agent genuinely cannot reach it directly any more. `suggest_outfit` and
   `create_fit_card` stayed as direct calls.

**Did anything behave differently? No, and I checked instead of assuming.**

```
$ python mcp_client.py
Asking mcp_server.py what it offers...

  search_listings
    Search a fixed catalogue of 40 secondhand clothing listings and return the
    ones that match, best match first.
    [...full description...]
    - description: string
    - size: string  (optional)
    - max_price: number  (optional)
```

Then I ran the same arguments both ways and compared the lists:

```
$ python -c "from tools import search_listings; from mcp_client import call_tool; args={'description':'looking for a vintage graphic tee','size':None,'max_price':30.0}; d=search_listings(args['description'],args['size'],args['max_price']); m=call_tool('search_listings',args); print('direct:',len(d),'items   mcp:',len(m),'items'); print('same?', d==m)"
direct: 10 items   mcp: 10 items
same? True
```

`d == m` is True, so the dicts came back identical field for field, not just the
same length. I checked the empty case separately too, because that is what my
branch in criterion 2 reads:

```
$ python -c "from mcp_client import call_tool; print(call_tool('search_listings', {'description':'designer ballgown','size':'XXS','max_price':5.0}))"
[]
```

That mattered more than it looks. MCP sends results back as text containing
JSON, so I half expected the empty list to arrive as `None` or as the string
`"[]"`, which would have made `if not results:` behave by accident rather than
on purpose. It comes back as a real empty list, so the branch still works for the
right reason.

The one thing that *is* different is speed. `mcp_client.call_tool` starts the
server, asks, and shuts it down again on every single call, so a run that used to
be instant now has a visible pause at the search step.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** one filter, in one tool, in `tools.py::search_listings`.
A size written as a plain number is now also allowed to match a waist token.

```python
# before
if size is not None:
    size_tokens = listing["size"].lower().replace("/", " ").split()
    if size.strip().lower() not in size_tokens:
        continue

# after
if size is not None:
    size_tokens = listing["size"].lower().replace("/", " ").split()
    wanted = size.strip().lower()
    matches_size = wanted in size_tokens

    if not matches_size and wanted.isdigit():
        matches_size = ("w" + wanted) in size_tokens

    if not matches_size:
        continue
```

That is the whole change. Four lines. Nothing else in the repo moved:
`agent.py`, `mcp_server.py`, `trace.py`, the prompts, the scenarios and the
criteria are all byte for byte what they were for the before run.

Two things I decided on purpose while writing it.

I match the `w` token only, never `l`. A listing sized `W28 L30` is a 28 waist
with a 30 inseam, so letting a `30` match the `L` token would hand someone
trousers that do not fit and would look like the search working.

I kept the whole token rule as the first test rather than replacing it. It is
the right rule, and it is the thing standing between me and the substring trap
the starter warned about. The number rule only runs when the whole token test
has already failed and the request is all digits, so it can only ever add
listings that the old rule rejected. It cannot loosen anything else.

**Which failure it was meant to fix:** mechanism A from my diagnosis, the one
that cost me try 1 of criterion 1. `levis jeans size 30` returned an empty list
because `lst_001` is sized `W30 L30`, which tokenises to `['w30', 'l30']`, and
`'30'` is equal to neither. Every pair of bottoms in the data is sized that
way, so the filter was discarding all of them for any numeric size.

**Which failure it was not meant to fix:** mechanism B, the scoring ties that
cost me tries 3 and 4. I am allowed one change and I picked the one that
produces the worse experience. Being told nothing exists when it does is a
dead end for a user. Being handed the wrong item at least gives them something
to react to. Mechanism B is untouched and I expect tries 3 and 4 to fail again,
which is the point of saying so before the run rather than after.

### Run Log — Before

Repeated here so the two are side by side. Full file:
`results/run_2026-10-11_1825_before.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | **MISSED (2/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Run Log — After

`python run_eval.py --label after`, same ten scenarios, five tries each,
caching off. Full file: `results/run_2026-10-11_2000_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | **PASS** | PASS | FAIL | FAIL | PASS | **MISSED (3/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 1 try by try, before against after:

| Try | Query | Before | After | Selected after the change |
|---|---|---|---|---|
| 1 | `levis jeans size 30` | FAIL, nothing found | **PASS** | lst_001 Vintage Levi's 501 Jeans, $38.0 |
| 2 | `black bomber jacket` | PASS | PASS | lst_022 90s Leather Bomber |
| 3 | `a green silk shirt` | FAIL, wrong item | FAIL, wrong item | lst_024 Vintage Polo Shirt, still not lst_029 |
| 4 | `small tan purse` | FAIL, wrong item | FAIL, wrong item | lst_002 Y2K Baby Tee, still not lst_039 |
| 5 | `chunky knit cardigan` | PASS | PASS | lst_008 Knit Cardigan |

**Did it help, and how do I know:**

Yes, and only as much as I said it would. Criterion 1 went from 2 of 5 to 3 of
5. It is still MISSED, because the target is 4 of 5 and the target does not
move.

The try it was aimed at is the try that changed. Here is try 1 after the
change, from `agent.py::run_agent` via `run_eval.py::run_once`:

```
- stopped early: no
- selected_item: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
- search_results: 1

Fit card:
Scored these dreamy medium wash Vintage Levi's 501 Jeans and I'm obsessed! Grab this absolute steal for just $38.0 over on my depop before someone else snatches them up. Go build your dream fit and tag me in your pics!

Trace:
[1] parse_query
      in:  levis jeans size 30
      out: description='levis jeans', size='30', max_price=None
[2] search_listings (via MCP)
      in:  description='levis jeans', size='30', max_price=None
      out: 1 items: Vintage Levi's 501 Jeans — Medium Wash
      →    branch: 1 results, carrying on
[3] select_item
      in:  1 results, taking index 0
      out: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
      →    selected_item id is lst_001
[4] suggest_outfit
      in:  item lst_001, wardrobe with 10 items
      out: Hey friend! Those medium wash Vintage Levi's 501 Jeans are an incredible find.   Try pairing your new jeans wi…
[5] create_fit_card
      in:  item lst_001, outfit of 353 chars
      out: Scored these dreamy medium wash Vintage Levi's 501 Jeans and I'm obsessed! Grab this absolute steal for just $…
[6] done
      →    all three tools ran, returning the session
```

Two steps became six. The same query that returned an empty list five times in
a row now finds `lst_001`, which is the exact listing my revised criterion
named, and takes it all the way through to a fit card. All five tries did it.

Tries 3 and 4 failed again, with the same two wrong items as before, which is
what I predicted above and is the correct outcome. Mechanism B is a scoring
tie, this change touched the size filter, and a change that had somehow fixed
tries 3 and 4 as well would mean I had not understood either problem.

**What I checked that could have gone wrong.** A size filter that lets more
through can let the wrong things through, and the rule I loosened is the one
guarding the substring trap. So I tested the edges directly against
`tools.py::search_listings` before running the eval:

```
  size='s'   on 'jeans'    ->  0 results, sizes []
  size='l'   on 'hoodie'   ->  1 results, sizes ['L']
  size='32'  on 'jeans'    ->  1 results, sizes ['W32']
  size='28'  on 'jeans'    ->  1 results, sizes ['W28']
  size='8'   on 'sneakers' ->  1 results, sizes ['US 8']
  size='m'   on 'tee'      ->  2 results, sizes ['S/M']
```

A small still does not match `US 9` or any waist. An `L` still does not match
`XL`. A 32 returns `W32` and not `W30`, so the number rule is matching the
whole waist token and not a prefix. Shoes and tops behave exactly as they did
before.

The other four criteria were all 5 of 5 before and are all 5 of 5 after, which
is the result I wanted from them. Criterion 5 in particular I measured again the
same way, printing every returned price rather than just the selected one:

```
try 1: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 2: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 3: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 4: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 5: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
```

Identical to before, which is what a change confined to the size filter should
do to a query that has no size in it.

**One honest limit on this result.** Three of five is a better number than two
of five, but the fix is narrower than the diagnosis. I taught the filter one
convention, `W` for waist, because that is the only one in these 40 listings.
A real catalogue would also have `30x32`, `UK 10`, `EU 38` and sizes written as
words, and none of those would work. What I fixed is this data's spelling of a
waist size, not the general problem of reading a size written a different way
from the one the seller typed.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
