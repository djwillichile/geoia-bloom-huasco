#!/usr/bin/env python3
"""
Lee CITATION.cff y actualiza el bloque de citación en README.md e index.html.
Los bloques se delimitan con comentarios <!-- CITATION-START --> / <!-- CITATION-END -->.
"""
import re
import sys
import yaml


def extract_initials(given: str) -> str:
    """'Guillermo S.' → 'G. S.'  |  'Andrés' → 'A.'"""
    parts = given.split()
    result = []
    for part in parts:
        if len(part) <= 2 and part.endswith("."):
            result.append(part)
        else:
            result.append(part[0] + ".")
    return " ".join(result)


def format_author(author: dict) -> str:
    family = author.get("family-names", "")
    given = author.get("given-names", "")
    initials = extract_initials(given) if given else ""
    return f"{family}, {initials}" if initials else family


def build_citation(data: dict) -> str:
    pref = data.get("preferred-citation", data)

    authors = pref.get("authors", data.get("authors", []))
    year = str(pref.get("year", str(data.get("date-released", ""))[:4]))
    title = pref.get("title", data.get("title", "")).strip().replace("\n", " ")
    url = pref.get("url", pref.get("repository-code", data.get("url", "")))

    if len(authors) == 0:
        author_str = ""
    elif len(authors) == 1:
        author_str = format_author(authors[0])
    elif len(authors) == 2:
        author_str = f"{format_author(authors[0])} & {format_author(authors[1])}"
    else:
        author_str = f"{format_author(authors[0])} et al."

    return f"{author_str} ({year}). {title}.\nGitHub. {url}"


MARKER_RE = re.compile(
    r"<!-- CITATION-START -->.*?<!-- CITATION-END -->",
    flags=re.DOTALL,
)


def replace_in(path: str, block: str) -> bool:
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if not MARKER_RE.search(content):
        print(f"  {path}: ERROR — marcadores no encontrados", file=sys.stderr)
        sys.exit(1)

    new_content = MARKER_RE.sub(block, content)

    if new_content == content:
        print(f"  {path}: ya actualizado")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  {path}: actualizado")
    return True


def replace_in_readme(citation: str) -> bool:
    block = f"<!-- CITATION-START -->\n```\n{citation}\n```\n<!-- CITATION-END -->"
    return replace_in("README.md", block)


def replace_in_html(citation: str) -> bool:
    block = f"<!-- CITATION-START -->{citation}<!-- CITATION-END -->"
    return replace_in("index.html", block)


if __name__ == "__main__":
    cff_path = "CITATION.cff"
    with open(cff_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    citation = build_citation(data)
    print(f"Citación generada:\n{citation}\n")

    readme_ok = replace_in_readme(citation)
    html_ok = replace_in_html(citation)

    if not (readme_ok or html_ok):
        print("Archivos ya estaban actualizados.")
