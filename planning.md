# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

I will filter out the user query by fetching the keywords like product name, size , condition, etc and match with the mock listings dataset and sort the top 3 items, then return the top ranked item to the user.

**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `description` (str): ...Keywords describing what the user is looking for
  (e.g., "vintage graphic tee").
- `size` (str): ...Size string to filter by, or None to skip size filtering.
  Matching is case-insensitive (e.g., "M" matches "S/M").
- `max_price` (float): ...Maximum price (inclusive), or None to skip price filtering.

**What it returns:**

<!-- Describe the return value — what fields does a result contain? -->

It will return the string which contain the information about the matched top ranked item to the user which contain the item name, product size and it condition.

**What happens if it fails or returns nothing:**

<!-- What should the agent do if no listings match? -->

A list of matching listing dicts, sorted by relevance (best match first).
Returns an empty list if nothing matches — does NOT raise an exception.

### Tool 2: suggest_outfit

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

suggest_outfit(new_item, wardrobe) this tool comapre the new_item with the user wardrobe to suggest 1-2 complete outfit combination.

**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `new_item` (dict): ... A listing dict (the item the user is considering buying).
- `wardrobe` (dict): ... A wardrobe dict with an 'items' key containing a list of
  wardrobe item dicts. May be empty — handle this gracefully.

**What it returns:**

<!-- Describe the return value -->

A non-empty string with outfit suggestions.

**What happens if it fails or returns nothing:**

<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

If the wardrobe is empty, offer general styling advice for the item
rather than raising an exception or returning an empty string.

---

### Tool 3: create_fit_card

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

Generate a short, shareable outfit caption for the thrifted find.
**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `outfit` (str): ...The outfit suggestion string from suggest_outfit().
- `new_item` (dict): ...The listing dict for the thrifted item.

**What it returns:**

<!-- Describe the return value -->

A 2–4 sentence string usable as an Instagram/TikTok caption.
**What happens if it fails or returns nothing:**

<!-- What should the agent do if the outfit data is incomplete? -->

If outfit is empty or missing, return a descriptive error message
string — do NOT raise an exception.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**

<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

The agent follows a sequential workflow based on the results of each tool call.

Parse the user's query and extract description, size, and max_price.
Call search_listings() to find matching thrift items.
If no items are returned, stop the process and return a helpful error message.
If matches exist, select the top-ranked item and store it in the session.
Call suggest_outfit() using the selected item and the user's wardrobe information.
Store the outfit recommendation in the session.
Call create_fit_card() to generate a social-media-style caption for the outfit.
Return all stored session information to the user.

The agent knows it is finished when either:

No listings are found (early termination), or
The fit card has been successfully generated.

---

## State Management

**How does information from one tool get passed to the next?**

<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

Step 1: Initialize the session with new_session().

Step 2: Parse the user's query to extract a description, size, and max_price, using the string splitting.Store the result in session["parsed"].

Step 3: Call search_listings() with the parsed parameters.
Store results in session["search_results"].
If no results: set session["error"] to a helpful message and return the session early. Do NOT proceed to suggest_outfit with empty input.

Step 4: Select the item to use (e.g., the top result).
Store it in session["selected_item"].

Step 5: Call suggest_outfit() with the selected item and wardrobe. Store the result in session["outfit_suggestion"].

Step 6: Call create_fit_card() with the outfit suggestion and selected item. Store the result in session["fit_card"].

Step 7: Return the session.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool                                                                    | Failure mode                          | Agent response                                                            |
| ----------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------- |
| search_listings                                                         | No results match the query            | A list of matching listing dicts, sorted by relevance (best match first). |
| Returns an empty list if nothing matches — does NOT raise an exception. |
| suggest_outfit                                                          | Wardrobe is empty                     | If the wardrobe is empty, offer general styling advice for the item       |
| rather than raising an exception or returning an empty string.          |
| create_fit_card                                                         | Outfit input is missing or incomplete | If outfit is empty or missing, return a descriptive error message         |
| string — do NOT raise an exception.                                     |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

User Query
│
▼
┌──────────────────────────────┐
│ Planning Loop │
│ (parse + decide next step) │
└──────────────────────────────┘
│
▼
┌──────────────────────────────┐
│ search_listings() │
│ input: description, size, │
│ max_price │
└──────────────────────────────┘
│
▼
┌──────────────────────────────────────────────┐
│ results == [] ? │
└──────────────────────────────────────────────┘
│ YES │ NO
▼ ▼
┌──────────────────────┐ ┌────────────────────────────┐
│ Return error message │ │ Select top item │
│ "No listings found" │ │ session["selected_item"] │
└──────────────────────┘ └────────────────────────────┘
│
▼
┌──────────────────────────────┐
│ suggest_outfit() │
│ input: selected_item, │
│ wardrobe │
└──────────────────────────────┘
│
▼
┌──────────────────────────────┐
│ wardrobe empty? │
└──────────────────────────────┘
│ YES │ NO
▼ ▼
┌──────────────────────┐ ┌────────────────────────┐
│ fallback styling │ │ LLM outfit suggestion │
│ advice string │ └────────────────────────┘
└──────────────────────┘ │
│ │
└──────────┬───────────┘
▼
session["outfit_suggestion"]
│
▼
┌──────────────────────────────┐
│ create_fit_card() │
│ input: outfit + item │
└──────────────────────────────┘
│
▼
┌──────────────────────────────┐
│ outfit empty? │
└──────────────────────────────┘
│ YES │ NO
▼ ▼
┌──────────────────────┐ ┌────────────────────────┐
│ return error string │ │ LLM generates caption │
└──────────────────────┘ └────────────────────────┘
│ │
└──────────┬───────────┘
▼
session["fit_card"]
│
▼
Return Session

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
search_listings() using load_listings() from the data loader — then test it against 3 queries
before trusting it.

Then tool 2 spec (inputs, return value, failure mode)and ask it to implement
suggest_outfit() using new_item with the user wardrobe — then test it against 3 queries
before trusting it.

Then tool 3 spec (inputs, return value, failure mode) and ask it to implement create_fit_card() Generate a short, shareable outfit caption for the thrifted find. Using the `outfit` (str): ...The outfit suggestion string from suggest_outfit() and `new_item` (dict): ...The listing dict for the thrifted item.

**Milestone 4 — Planning loop and state management:**
I will give Claude my Planning Loop, State Management section, and Architecture diagram from this planning.md file and ask it to implement the agent orchestration logic.

I expect Claude to produce:

A new_session() function that initializes session state.
Query parsing logic for extracting description, size, and max_price.
Sequential tool calls:
search_listings()
suggest_outfit()
create_fit_card()
Error handling that stops execution when no listings are found.
Session storage for all intermediate outputs.

I will verify the implementation by testing at least three scenarios:

A query with multiple matching listings.
A query with no matching listings.
A query where the user's wardrobe is empty.

## I will confirm that the session dictionary is updated correctly at every step and that all error cases follow the specification.

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**

<!-- What does the agent do first? Which tool is called? With what input? -->

The agent reads the query and extracts:

Description: "vintage graphic tee"
Size: None
Maximum price: $30

It stores this information in session["parsed"].

Then agent calls search_listings() with the extracted information.

The tool returns:

Vintage Nirvana Graphic Tee
Size: L
Condition: Excellent
Price: $25

The agent stores the results in session["search_results"] and saves the best item in session["selected_item"].

**Step 2:**

<!-- What happens next? What was returned from step 1? What tool is called now? -->

The agent calls suggest_outfit() using the selected item and the user's wardrobe.

The tool returns:

"Pair the Vintage Nirvana Graphic Tee with baggy jeans and chunky sneakers for a relaxed streetwear look."

The agent stores this in session["outfit_suggestion"].

**Step 3:**

<!-- Continue until the full interaction is complete -->

The agent calls create_fit_card() using the outfit suggestion and the selected item.

The tool returns:

"Just thrifted a Vintage Nirvana Graphic Tee in excellent condition for $25. Styled it with baggy jeans and chunky sneakers for a cool streetwear vibe."

The agent stores this in session["fit_card"].
**Final output to user:**

<!-- What does the user actually see at the end? -->

Top Match:
Vintage Nirvana Graphic Tee
Size: L
Condition: Excellent
Price: $25

Outfit Suggestion:
Pair it with baggy jeans and chunky sneakers for a relaxed streetwear look.

Fit Card:
Just thrifted a Vintage Nirvana Graphic Tee in excellent condition for $25. Styled it with baggy jeans and chunky sneakers for a cool streetwear vibe.
