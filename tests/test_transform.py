"""Tests du nettoyage : chaque test vérifie qu'une règle de etl/transform.py fait ce qu'on attend.
Lancer depuis la racine du projet : pytest -v"""
import pandas as pd
from etl.transform import strip_html, anonymize, hash_author, is_about_work, remove_quotes, clean_hn

# --- Les 4 tests du guide (une règle = un test) ---

def test_strip_html():
    assert strip_html("<p>It&#x27;s <i>great</i></p>") == "It's great"

def test_anonymize_email_and_url():
    out = anonymize("Write to bob@acme.com or see https://acme.com/x")
    assert "bob@acme.com" not in out
    assert "https" not in out

def test_hash_is_stable_and_hides_the_name():
    assert hash_author("bob42") == hash_author("bob42")    # même pseudo = même code
    assert hash_author("bob42") != "bob42"                  # le pseudo n'apparaît plus

def test_work_filter():
    assert is_about_work("My manager forced us to use Copilot")
    assert not is_about_work("I like pizza")

# --- Tests ajoutés pour les règles en plus du guide ---

def test_remove_quotes():
    """Une citation d'un autre commentaire (qui commence par '>') est retirée."""
    out = remove_quotes("<p>&gt; someone else said this<p>My manager forced Copilot on us")
    assert "someone else" not in out
    assert "My manager" in out

def test_salt_changes_the_hash(monkeypatch):
    """Avec un sel secret, le code d'un pseudo change : impossible de le retrouver sans le sel."""
    monkeypatch.setenv("HASH_SALT", "sel_A")
    code_a = hash_author("bob42")
    monkeypatch.setenv("HASH_SALT", "sel_B")
    assert hash_author("bob42") != code_a

def test_work_filter_needs_a_whole_word():
    """'network' contient 'work' mais ne parle pas de travail : il ne doit pas passer (revue PR #35)."""
    assert not is_about_work("I fixed my home network with an AI assistant")
    assert is_about_work("Our teams and companies now use AI at work.")    # pluriels et ponctuation OK

def test_context_is_anonymized():
    """Le titre du fil est anonymisé comme le texte (revue PR #35)."""
    long_text = "My manager asked our whole team to adopt an AI assistant for code reviews this year."
    raw = pd.DataFrame({"objectID": ["1"], "comment_text": [long_text],
                        "story_title": ["Contact bob@acme.com or see https://acme.com/post"],
                        "author": ["bob42"], "created_at": ["2026-11-12T10:00:00Z"],
                        "_ingested_at": [1795000000]})
    clean, _ = clean_hn(raw)
    assert "bob@acme.com" not in clean.loc[0, "context"]
    assert "https" not in clean.loc[0, "context"]

def test_save_parquet_refuses_empty_table():
    """Un tableau vide ne doit jamais écraser le bon fichier dans S3 (revue PR #35)."""
    import pytest
    from etl.load import save_parquet
    with pytest.raises(ValueError):
        save_parquet(pd.DataFrame(), "clean/verbatims.parquet")    # s'arrête avant tout envoi à S3

def test_clean_hn_full_pipeline():
    """Test de bout en bout sur 4 faux commentaires : chaque règle retire ce qu'elle doit."""
    long_text = "My manager asked our whole team to adopt an AI assistant for code reviews this year."
    raw = pd.DataFrame({
        "objectID":     ["1", "2", "3", "4"],
        "comment_text": [f"<p>{long_text} Mail me at bob@acme.com",   # gardé, e-mail masqué
                         f"<p>{long_text} Mail me at bob@acme.com",   # même texte : doublon retiré
                         "Too short",                                   # trop court : retiré
                         long_text],                                    # fil d'offres d'emploi : retiré
        "story_title":  ["AI at work", "AI at work", "AI at work", "Ask HN: Who is hiring? (November 2026)"],
        "author":       ["bob42", "ann", "zoe", "max"],
        "created_at":   ["2026-11-12T10:00:00Z"] * 4,
        "_ingested_at": [1795000000] * 4,
    })
    clean, stats = clean_hn(raw)
    assert len(clean) == 1                                              # 1 seul survivant
    assert list(clean.columns) == ["verbatim_id", "source", "text", "context",
                                   "author_id", "created_on", "ingested_on", "lang"]  # le schéma validé
    row = clean.iloc[0]
    assert row["verbatim_id"] == "hn_1"
    assert "@" not in row["text"] and "<" not in row["text"]           # ni e-mail ni HTML
    assert row["author_id"] != "bob42"                                  # pseudo remplacé
    assert stats["entree"] == 4
