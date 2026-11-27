"""Tests de rag/plan.py, sans appel à l'API ni à la vraie base : le LLM, les embeddings
et ChromaDB sont remplacés par de faux objets. Lancer depuis la racine du projet : pytest -v"""
import os
os.environ.setdefault("LLM_API_KEY", "cle-de-test")    # rag.llm exige une clé à l'import (jamais utilisée ici)

import pytest
import rag.plan as plan


class FakeCollection:
    """Imite une collection ChromaDB : renvoie des morceaux fixés à l'avance et note la requête reçue."""
    def __init__(self, chunks):
        self.chunks = chunks            # liste de (texte, métadonnées)
        self.last_query = None

    def query(self, **kwargs):
        self.last_query = kwargs
        where = kwargs.get("where")
        kept = [(d, m) for d, m in self.chunks
                if not where or all(m.get(k) == v for k, v in where.items())]
        kept = kept[:kwargs["n_results"]]
        return {"documents": [[d for d, _ in kept]], "metadatas": [[m for _, m in kept]]}


def chunk(vid, stage):
    return (f"texte de {vid}", {"verbatim_id": vid, "adkar_stage": stage})


@pytest.fixture
def fake_rag(monkeypatch):
    """Branche de fausses dépendances ; le test choisit les morceaux et la réponse du LLM."""
    state = {"chunks": [], "answer": "Plan [hn_1]", "prompts": []}
    collections = {}

    def fake_get_collection(name):
        if name not in collections:
            data = state["chunks"] if name == "verbatims" else [("## Knowledge\nFormer", {})]
            collections[name] = FakeCollection(data)
        return collections[name]

    def fake_ask(prompt, temperature=0.0):
        state["prompts"].append(prompt)
        return state["answer"]

    monkeypatch.setattr(plan, "embed", lambda texts: [[0.0] * 3 for _ in texts])
    monkeypatch.setattr(plan, "get_collection", fake_get_collection)
    monkeypatch.setattr(plan, "ask", fake_ask)
    state["collections"] = collections
    return state


def test_only_the_requested_stage_is_used(fake_rag):
    fake_rag["chunks"] = [chunk("hn_1", "Knowledge"), chunk("hn_2", "Ability")]
    r = plan.make_plan("Knowledge")
    assert fake_rag["collections"]["verbatims"].last_query["where"] == {"adkar_stage": "Knowledge"}
    assert [s["verbatim_id"] for s in r["sources"]] == ["hn_1"]


def test_one_verbatim_cut_in_pieces_is_one_source(fake_rag):
    fake_rag["chunks"] = [chunk("hn_1", "Knowledge"), chunk("hn_1", "Knowledge"), chunk("hn_2", "Knowledge")]
    r = plan.make_plan("Knowledge")
    assert [s["verbatim_id"] for s in r["sources"]] == ["hn_1", "hn_2"]
    assert len(r["extraits"]) == len(r["sources"])


def test_at_most_8_sources(fake_rag):
    fake_rag["chunks"] = [chunk(f"hn_{i}", "Ability") for i in range(20)]
    r = plan.make_plan("Ability")
    assert len(r["sources"]) == 8


def test_prompt_contains_ids_and_question(fake_rag):
    fake_rag["chunks"] = [chunk("hn_7", "Desire")]
    plan.make_plan("Desire", "Quelle première action ?")
    prompt = fake_rag["prompts"][0]
    assert "[hn_7]" in prompt and "Quelle première action ?" in prompt and "Desire" in prompt


def test_invented_citations_are_flagged(fake_rag):
    fake_rag["chunks"] = [chunk("hn_1", "Awareness")]
    fake_rag["answer"] = "Action 1 [hn_1]. Action 2 [hn_999, hn_1]."
    r = plan.make_plan("Awareness")
    assert r["citations_inventees"] == ["hn_999"]


def test_empty_llm_answer_does_not_crash(fake_rag):
    fake_rag["chunks"] = [chunk("hn_1", "Awareness")]
    fake_rag["answer"] = None
    r = plan.make_plan("Awareness")
    assert r["plan"] == "" and r["citations_inventees"] == []


def test_no_classified_verbatim_gives_clear_error(fake_rag):
    fake_rag["chunks"] = [chunk("hn_1", "unknown")]          # base pas encore réindexée
    with pytest.raises(RuntimeError, match="rag.index"):
        plan.make_plan("Knowledge")


def test_unknown_stage_is_refused(fake_rag):
    with pytest.raises(ValueError):
        plan.make_plan("knowledge")                            # minuscule
    with pytest.raises(ValueError):
        plan.make_plan("none")                                 # pas de plan pour « hors sujet »


def test_llm_error_is_retried(fake_rag, monkeypatch):
    fake_rag["chunks"] = [chunk("hn_1", "Ability")]
    calls = []
    def flaky_ask(prompt, temperature=0.0):
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("coupure")
        return "Plan [hn_1]"
    monkeypatch.setattr(plan, "ask", flaky_ask)
    monkeypatch.setattr(plan.time, "sleep", lambda s: None)   # pas d'attente réelle pendant le test
    assert plan.make_plan("Ability")["plan"] == "Plan [hn_1]"
    assert len(calls) == 2
