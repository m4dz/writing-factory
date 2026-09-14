"""The author's attack per beat (quality campaign, lever 1).

The owner writes the first sentence of a beat; the model continues it. The
attack is posed, counted against the beat's sentence cap, guarded like any
served text, and an echo of it at the head of the model's segment is removed.
"""

import textwrap
from dataclasses import replace

import pytest

from factory.chapter_spec import load_chapter
from factory.chapter_spec.loader import ChapterSpecError, load_spec, read_entry_brief
from factory.pipeline import graph
from fakes import fixtures as fx

ATTACK = "Je relis la ligne, le crayon levé, et je ne biffe rien."


def _state_with_attacks(attacks: tuple[str, ...]):
    spec = load_chapter(7)
    entry = spec.entries[1]
    beats = tuple(replace(b, attack=a) for b, a in zip(entry.beats, attacks))
    specs = [spec.entries[0], replace(entry, beats=beats)]
    return {**spec.state(seed=1), "entry_specs": specs, "plan": list(spec.imposed_plan),
            "idx": 1, "scenes": [""], "metrics": [], "warnings": []}


def test_attack_is_posed_served_as_prefix_and_counted(fake_model, fake_chroma, quiet_progress):
    state = _state_with_attacks((ATTACK, "", ""))
    out = graph.write_node(state)
    entry = out["scenes"][-1]
    assert entry.count(ATTACK) == 1
    # The attack closes the "already written" block of its beat; the next beat
    # sees it inside the text already written, once.
    served = dict(out["served_prompts"])
    assert f"\n\n{ATTACK}\n---\n" in served["relève"]
    assert served["découverte"].count(ATTACK) == 1
    # Cap: the beat allows 4 sentences, the attack is one, the model gets 3 —
    # the four-sentence fixture loses its last sentence.
    assert any("attaque d'auteur posée (1 phrase(s)), le modèle borné à 3" in w
               for w in out["warnings"])
    assert "Je reste debout avec mon manteau." not in entry
    assert "Je rentre et la maison est allumée." in entry


def test_attack_echo_is_removed_verbatim_and_paraphrased():
    tail = "Sur la table, la boîte est ouverte."
    assert graph._strip_attack_echo(ATTACK, f"{ATTACK} {tail}") == tail
    echo = "Je relis la ligne, le crayon levé, et je ne biffe rien du tout."
    assert graph._strip_attack_echo(ATTACK, f"{echo} {tail}") == tail
    assert graph._strip_attack_echo(ATTACK, tail) == tail


def test_scoring_bears_on_the_model_text_not_the_attack(fake_model, fake_chroma,
                                                        quiet_progress):
    # An attack that names a presence would sink every variant alike; a
    # resolving variant must still lose to the fixture.
    fake_model.responses["write.beat"] = [fx.BEAT_RESOLVING, fx.BEATS[0], fx.BEATS[0]] * 3
    out = graph.write_node(_state_with_attacks((ATTACK, "", "")))
    assert "Je me souviens soudain" not in out["scenes"][-1]
    assert any("relève : best-of-3 — variant 2 retenu" in w for w in out["warnings"])


def test_brief_blockquote_under_a_beat_is_the_attack(tmp_path):
    brief = tmp_path / "brief-entree-2.md"
    brief.write_text(textwrap.dedent("""
        ## 7. Découpage en beats

        ### Beat A — la relève

        > Je relis la ligne, le crayon levé.

        Elle relit la ligne qu'elle vient de recopier.

        ### Beat B — la découverte

        Autour d'elle, la maison est dressée.
    """), encoding="utf-8")
    parsed = read_entry_brief(brief)
    assert parsed["beats"] == ["Elle relit la ligne qu'elle vient de recopier.",
                               "Autour d'elle, la maison est dressée."]
    assert parsed["attacks"] == ["Je relis la ligne, le crayon levé.", ""]


def test_spec_attack_is_guarded_like_served_text(tmp_path):
    def spec(attack: str):
        d = tmp_path / f"03-{abs(hash(attack)) % 1000}"
        d.mkdir()
        (d / "spec.yaml").write_text(textwrap.dedent(f"""
            chapter: 3
            slug: essai
            narrator: judith
            brief: "Le soir."
            entries:
              - strategy: beats
                beats:
                  - {{name: a, num_predict: 100, sentences_max: 3, instruction: "Elle relit.",
                     attack: "{attack}"}}
        """), encoding="utf-8")
        return d / "spec.yaml"

    assert load_spec(spec("Je relis la ligne.")).entries[0].beats[0].attack == "Je relis la ligne."
    with pytest.raises(ChapterSpecError, match="fichiers de bible"):
        load_spec(spec("Voir fiche-romane.md."))
    with pytest.raises(ChapterSpecError, match="termes d'atelier"):
        load_spec(spec("Couperet : je relis."))
    # Chapter 7 as shipped carries no attack: the owner writes them.
    assert all(b.attack == "" for b in load_chapter(7).entries[1].beats)
