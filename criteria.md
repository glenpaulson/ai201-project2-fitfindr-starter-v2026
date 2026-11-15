# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search is a plain keyword overlap match. It scores a listing by how many of
the user's words show up in the title, description, and style tags. That works
when the user names words the listing actually uses, but a shopper can describe
the same item in words the data does not contain (saying "tee" for a listing
titled "baby tee", or a synonym the seller never wrote), and then a real match
scores zero and gets dropped. 4 of 5 leaves room for that phrasing gap. It is
my search being literal, not the loop failing.

> **Revised in unit 4:** Given these five queries, each one the way a shopper
> would describe an item that really is in `data/listings.json`, the agent
> returns a fit card for at least 4 of the 5.
>
> | # | Query | The item it should find |
> |---|---|---|
> | 1 | `levis jeans size 30` | lst_001, Vintage Levi's 501 Jeans, W30 L30 |
> | 2 | `black bomber jacket` | lst_022, 90s Leather Bomber, Black |
> | 3 | `a green silk shirt` | lst_029, Silk Button-Down, Sage Green |
> | 4 | `small tan purse` | lst_039, Mini Shoulder Bag, Tan Leather |
> | 5 | `chunky knit cardigan` | lst_008, Oversized Knit Cardigan, Chunky Brown |
>
> **Why revised:** The original says "given a query that matches at least one
> listing", which makes search already having worked a precondition. That
> leaves the criterion measuring only whether the loop finishes afterwards,
> and the loop is five plain `if` branches with nothing random in them. So the
> original could not fail for the reason I wrote underneath it. The reason is
> about a shopper using words the seller never typed, and the original wording
> defines that case away instead of testing it.
>
> It also could not be measured the way I ran it. I tested it with one query
> five times, and `search_listings` is plain Python, so those were the same
> search five times. Five tries of a deterministic function measure
> determinism, not the phrasing gap.
>
> The revision fixes both. Five different phrasings means the five tries are
> five real tries, and every item named above is one I confirmed is in the data
> first, so a zero result is my search being literal and not the shopper asking
> for something that does not exist. I picked the wordings before running any
> of them.
>
> **The target stays at 4 of 5.** This is a revision because the old one
> measured the wrong thing, not because I missed it. I had not missed it.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never calls the model and never depends on wording. search_listings is
plain Python, so an impossible query returns an empty list every single time, and
the loop's branch is one `if` on that empty list. There is no randomness and no
second service that could behave differently between tries, so if it stops once
it stops every time. That is why 5 of 5 is fair here when criterion 1 is not.

---

## 3. The item found is the item that gets styled

In 5 of 5 runs, the item id stored in `session["selected_item"]["id"]` is the
same id that reaches `suggest_outfit`, which is the `new_item` it is called with.
I check it by comparing `session["selected_item"]["id"]` against the item
recorded going into the suggest_outfit step. If the two ids ever differ, the
outfit was built for a different item than the one search picked.

**Why this target:**
The selected item travels from search to suggest_outfit through one field in the
session dict, set once by a plain assignment. Nothing random touches it, so the
id that goes in should always be the id that comes back out. I set 5 of 5 because
a single mismatch means the session is being overwritten or the wrong index is
being read, and that is a real bug I want to catch, not acceptable noise.



---

## 4. The fit card names the price

In at least 4 of 5 runs, the fit card contains the item's price, meaning the
number from `new_item["price"]` appears somewhere in the caption. A caption that
never mentions what the item costs is not doing its job, since the price is half
the reason anyone reposts a thrift find.

**Why this target:**
The fit card is written by the model at temperature 0.9, so the exact words
change every run and I cannot pin it to one fixed sentence. What I can ask for is
that the price always lands in the caption. I set 4 of 5 rather than 5 of 5
because the model sometimes rounds the number or writes around it ("just under
twenty"), and that is model variance I can live with, not a broken tool.



---

## 5. The price ceiling is never crossed

When the user gives a max price, every listing `search_listings` returns has a
`price` less than or equal to that ceiling, in 5 of 5 runs. For the query
"vintage graphic tee under $30", no returned listing is above $30.

**Why this target:**
This is a pure filter inside search_listings with no model involved, so it is
deterministic: the same query gives the same results every time. A ceiling that
leaks even once is a plain logic bug, not variance, so there is no reason to
accept anything below 5 of 5. I picked this one because it is the thing a shopper
cares about most and the easiest to get silently wrong, for example when a
PowerShell double quote eats the `$30` before my code ever sees it.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->


---

# Capstone criteria (unit 9)

Written on November 15, 2026, before running any Milestone 5 test. These are
about the logging I added to `serve.py` for the capstone, not about the agent
from units 3 and 4. All five are checked by sending requests to a running
`python serve.py` with `AI201_CACHE=0`, and each one gets three trials.

**The test queries.** Criteria 1, 2 and 3 use the same ten matching queries
from my Milestone 3 session:

1. `vintage graphic tee under $30`
2. `90s track jacket in size M`
3. `silk slip dress in midi length under $40`
4. `platform sneakers size 8`
5. `denim jacket under $50`
6. `black leather jacket under $80`
7. `baggy jeans size 32`
8. `cozy oversized hoodie`
9. `chunky knit sweater under $45`
10. `brown leather belt`

## 1. Every request leaves exactly one complete log line

When I send the ten test queries, the no match query
`designer ballgown size XXS under $5`, and the five bad bodies from criterion
5 (16 requests in total), `logs/requests.jsonl` gets exactly 16 new lines.
Each request id sent back to me shows up in exactly one of them, and every one
of those lines has a value (not missing and not null) for `timestamp`,
`request_id`, `outcome`, `status_code` and `duration_ms`. Target: 16 of 16 in
each trial.

**Why this target:** this is the whole point of the extension. A request that
doesn't leave a line is exactly the kind of failure I'd never find, because it
only shows up as something missing. 15 of 16 would mean one request
disappeared, so anything below all of them is a miss. I'm checking the request
ids and not just the count, because two lines for one request and zero for
another would still add up to 16.

## 2. A matching query answers in under 8 seconds

For the ten test queries sent one after another, with nothing else hitting the
server, at least 8 of the 10 have `duration_ms` under 8000 in their log line.
The first request after starting the server counts like any other, and so
does any time a request spends waiting on the rate limiter in `generate.py`,
because the shopper waits for that too. Each trial starts at least 60 seconds
after the last one finished, so one trial's calls don't eat into the next
one's per minute limit.

**Why this target:** a shopper waiting on a thrift search would give up
somewhere around ten seconds. My Milestone 3 session had a median of 5.7
seconds but 3 of 10 over 10 seconds, so 8 seconds for 8 of 10 is a little
tighter than what I saw and could really fail. I'm allowing two slow ones
because both tools call Gemini and I don't control how long Gemini takes, but
more than two slow ones out of ten would mean a lot of shoppers waiting too
long. I'm using `duration_ms` (the whole request) and not `agent_ms`, because
the shopper waits for the whole thing.

## 3. One matching query costs 2 model calls and no more than 600 tokens

For the ten test queries, every log line shows `model_calls` equal to 2, and
`prompt_tokens + output_tokens` between 1 and 600. Target: 10 of 10 in each
trial.

**Why this target:** FitFindr should call the model exactly twice per answer,
once for `suggest_outfit` and once for `create_fit_card`. A 3 would mean a
retry or a call I didn't know about, and on a paid tier that's money. In
Milestone 3 the runs used between 412 and 504 tokens, so 600 leaves room for a
longer listing or a longer caption but would catch a prompt that grew a lot,
or a retry being counted twice. The lower limit of 1 is there because a 0 on
an ok run would mean the counting is broken, and then the cost number in my
README means nothing.

## 4. When the model can't be reached, the caller gets an error code, not a 200

With the server started with a wrong `GEMINI_API_KEY`, sending
`denim jacket under $50` gets back an HTTP status of 500 or higher, and the
log line for that request has the same number in `status_code` and an `error`
that mentions the API key. Target: 3 of 3 requests in each trial.

**Why this target:** without the model FitFindr can find an item but can't
style it or write a fit card, so the request didn't do its job. Anything that
only looks at status codes (a host's health check, or me counting 200s in the
log) would count a broken key as a success. It's 3 of 3 because a broken key
breaks every request the same way, so there's no reason it should only be
reported right some of the time.

## 5. Bad input gets a 400 and uses no model calls

Each of these five bodies sent to `/ask` gets status 400 back, with an error
message that has the word `query` in it, and a log line with `outcome` equal
to `bad_request`, `model_calls` either 0 or not there at all, and `raw_body`
showing what was sent:

1. `{}`
2. `{"query": ""}`
3. `["vintage", "tee"]` (a list, not an object)
4. `{"query": 42}` (a number, not text)
5. `hello` sent as plain text, not JSON

Target: 5 of 5 in each trial.

**Why this target:** these are mistakes someone calling the server would
really make, and before my change, 3 and 4 crashed `serve.py` with a stack
trace instead of a 400. A bad request should never get as far as the model,
because that would be paying for a call that can't produce anything. It's 5 of
5 because the code that checks these doesn't involve the model at all, so
there's nothing random about it. If one fails it will fail every time.
