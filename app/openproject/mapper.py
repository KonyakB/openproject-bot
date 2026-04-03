import re


def normalize_ref(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower()).strip()


def match_value(ref: str, candidates: list[str]) -> tuple[str | None, bool]:
    if not ref:
        return None, False
    n_ref = normalize_ref(ref)

    for candidate in candidates:
        if ref == candidate:
            return candidate, False

    for candidate in candidates:
        if ref.lower() == candidate.lower():
            return candidate, False

    for candidate in candidates:
        if n_ref == normalize_ref(candidate):
            return candidate, False

    fuzzy = [c for c in candidates if n_ref in normalize_ref(c) or normalize_ref(c) in n_ref]
    if len(fuzzy) == 1:
        return fuzzy[0], True
    return None, len(fuzzy) > 1
