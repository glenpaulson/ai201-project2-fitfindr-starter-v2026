"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2, the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 is about the session, not about what the user typed, so
        # any query that finds something will do. I picked a different one from
        # criterion 1 so a bug that only shows up on one query cannot hide. What
        # I read is the trace: step 3 prints "selected_item id is lst_XXX" and
        # step 4 prints "item lst_XXX" going into suggest_outfit. The two ids
        # have to be the same string.
        "name": "selected item is the item styled",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 is about the fit card naming the price. run_eval.py runs
        # every scenario five times, so this is the same item written up five
        # separate times, which is what the criterion needs. Caching is off for
        # the run, so these are five real captions and not one answer repeated.
        # The top result here is lst_013 at $30.0, so I am looking for 30 in
        # the caption text.
        "name": "fit card names the price",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 names this exact query, so this is the query I run. The
        # ceiling is $30 and the data has an item priced at exactly $30.00,
        # which is the inclusive edge my Tool Inventory promised, so this is a
        # real test of the filter and not a soft one.
        "name": "price ceiling is never crossed",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes. Not
        # one of my five criteria, so it stays a diagnostic run.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
