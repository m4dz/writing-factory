"""The seal test's sixth control: chapter material is in no collection."""

from factory.eval import seal


def test_chapter_material_is_collected_from_briefs_and_specs():
    lines = seal.chapter_material()
    assert len(lines) > 20
    assert any("Neuf ans aujourd" in line for line in lines)          # brief.md and spec.yaml
    assert any("la playlist qui tourne encore" in line for line in lines)
    assert seal.chapter_material(seal.CHAPTERS_DIR / "nope") == []


def test_indexed_bible_carries_no_chapter_line(fake_chroma):
    docs = fake_chroma.get_collection("auteur").get(include=["documents"])["documents"]
    assert docs and seal.chapter_leaks(docs) == []
    injected = docs + ["Le brief dit : la playlist qui tourne encore, et la musique tourne."]
    assert seal.chapter_leaks(injected, ["la playlist qui tourne encore, et la musique tourne"])
