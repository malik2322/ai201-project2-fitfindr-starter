from unittest.mock import MagicMock, patch

from tools import create_fit_card, search_listings, suggest_outfit


# ── search_listings ──────────────────────────────────────────────────────────

def test_search_listings_returns_results():
    results = search_listings("vintage tee", None, 50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_listings_empty_for_impossible_query():
    results = search_listings("xyznonexistent123", None, None)
    assert results == []


def test_search_listings_respects_max_price():
    results = search_listings("jeans", None, 25)
    for item in results:
        assert item["price"] <= 25


# ── suggest_outfit (mocked LLM) ─────────────────────────────────────────────

@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe(mock_client_fn):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Pair with jeans and sneakers."
    mock_client_fn.return_value.chat.completions.create.return_value = mock_response

    result = suggest_outfit({"name": "tee", "price": 20}, {"items": []})
    assert isinstance(result, str)
    assert len(result) > 0


@patch("tools._get_groq_client")
def test_suggest_outfit_valid_wardrobe(mock_client_fn):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Try the tee with your jeans and boots."
    mock_client_fn.return_value.chat.completions.create.return_value = mock_response

    result = suggest_outfit(
        {"name": "tee", "price": 20},
        {"items": [{"name": "jeans", "category": "bottoms", "colors": ["blue"]}]},
    )
    assert isinstance(result, str)
    assert len(result) > 0


# ── create_fit_card (mocked LLM) ────────────────────────────────────────────

def test_create_fit_card_empty_outfit():
    assert create_fit_card("", {"name": "tee"}) == "Error: missing outfit data"


def test_create_fit_card_none_outfit():
    assert create_fit_card(None, {}) == "Error: missing outfit data"


@patch("tools._get_groq_client")
def test_create_fit_card_valid_input(mock_client_fn):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Just copped this tee for $20!"
    mock_client_fn.return_value.chat.completions.create.return_value = mock_response

    result = create_fit_card("casual with jeans", {"name": "tee", "price": 20})
    assert isinstance(result, str)
    assert len(result) > 0
