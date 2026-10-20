"""Small, read-only NCBI PubMed client; Python standard library only."""
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL = "myologia-medical-literature-research"


def text(node):
    return " ".join("".join(node.itertext()).split()) if node is not None else None


def fields(node):
    return {child.tag: text(child) for child in node} if node is not None else {}


def parse_records(payload):
    root = ET.fromstring(payload)
    if root.tag != "PubmedArticleSet" or root.find(".//ERROR") is not None:
        raise ValueError("EFetch did not return a valid PubmedArticleSet")
    records = []
    for item in root:
        book = item.tag == "PubmedBookArticle"
        citation = item.find("BookDocument" if book else "MedlineCitation")
        if citation is None:
            raise ValueError("Unsupported PubMed record type")
        article = citation if book else citation.find("Article")
        if article is None:
            raise ValueError("Missing article metadata")
        ids = item.findall("./PubmedBookData/ArticleIdList/ArticleId" if book
                           else "./PubmedData/ArticleIdList/ArticleId")
        identifiers = {}
        for ident in ids:
            identifiers.setdefault(ident.get("IdType"), []).append(text(ident))
        authors = [fields(a) for a in article.findall("./AuthorList/Author")]
        pub_date = article.find("./Book/PubDate" if book else "./Journal/JournalIssue/PubDate")
        pmid = text(citation.find("PMID"))
        if not pmid or not re.fullmatch(r"[1-9][0-9]*", pmid):
            raise ValueError("Missing or invalid PMID")
        author_list = article.find("AuthorList")
        records.append({
            "pmid": pmid, "record_type": item.tag,
            "title": text(article.find("ArticleTitle")), "authors": authors,
            "authors_complete": author_list.get("CompleteYN") if author_list is not None else None,
            "journal_or_book": text(article.find("./Book/BookTitle" if book else "./Journal/Title")),
            "publication_date": fields(pub_date),
            "article_dates": [{"type": d.get("DateType"), **fields(d)}
                              for d in article.findall("ArticleDate")],
            "identifiers": identifiers,
            "publication_types": [text(p) for p in article.findall("./PublicationTypeList/PublicationType")],
            "correction_links": [{"type": c.get("RefType"), **fields(c)}
                                 for c in citation.findall("./CommentsCorrectionsList/CommentsCorrections")],
            "abstract_available": article.find("Abstract") is not None,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    return records


class Client:
    def __init__(self):
        self.last_request = 0.0
        self.requests = 0

    def get(self, endpoint, params):
        args = {"db": "pubmed", "tool": TOOL, **params}
        for env, key in (("NCBI_EMAIL", "email"), ("NCBI_API_KEY", "api_key")):
            if os.environ.get(env):
                args[key] = os.environ[env]
        request = Request(BASE + endpoint + ".fcgi?" + urlencode(args),
                          headers={"User-Agent": TOOL + "/1.0"})
        for attempt in range(3):
            time.sleep(max(0, 0.4 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            self.requests += 1
            try:
                with urlopen(request, timeout=25) as response:
                    payload = response.read(10_000_001)
                if len(payload) > 10_000_000:
                    raise ValueError("Response exceeds 10 MB; narrow the request")
                return payload
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise RuntimeError(f"NCBI HTTP {exc.code}") from None
                delay = 2 ** (attempt + 1)
                retry_after = exc.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        try:
                            delay = max(delay, (parsedate_to_datetime(retry_after)
                                               - datetime.now(timezone.utc)).total_seconds())
                        except (ValueError, TypeError):
                            pass
                if delay > 60:
                    raise RuntimeError("NCBI requests a longer wait; retry later") from None
                time.sleep(delay)
            except (URLError, TimeoutError, OSError):
                raise RuntimeError("NCBI network/TLS request failed; no API result confirmed") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--query")
    mode.add_argument("--ids", help="Comma-separated PMID values; maximum 20")
    parser.add_argument("--limit", type=int, default=5, choices=range(1, 21))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.out.exists() and not args.overwrite:
        parser.error("Output exists; reuse it or explicitly pass --overwrite")
    if not args.out.parent.is_dir():
        parser.error("Output parent directory must already exist")
    if args.query is not None and not args.query.strip():
        parser.error("Query must not be empty")
    ids = list(dict.fromkeys(args.ids.split(","))) if args.ids else []
    if args.ids is not None and (not ids or len(ids) > 20 or
                                any(not re.fullmatch(r"[1-9][0-9]*", i) for i in ids)):
        parser.error("Provide 1–20 numeric PMID values")
    client = Client()
    result = {"schema_version": 1, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "api_base": BASE, "query": args.query, "metadata_only": True}
    try:
        if args.query:
            response = json.loads(client.get("esearch", {"term": args.query, "retmode": "json",
                                                        "retmax": args.limit, "sort": "relevance"}))
            if response.get("error") or "esearchresult" not in response:
                raise ValueError("ESearch returned an error or invalid response")
            search = response["esearchresult"]
            if search.get("ERROR"):
                raise ValueError("ESearch rejected the query")
            result["search"] = {k: search.get(k) for k in
                                ("count", "querytranslation", "warninglist", "errorlist")}
            ids = search["idlist"]
        result["requested_pmids"] = ids
        result["records"] = parse_records(client.get("efetch", {"id": ",".join(ids),
                                                                "retmode": "xml"})) if ids else []
        returned = {r["pmid"] for r in result["records"]}
        result["missing_pmids"] = sorted(set(ids) - returned)
        if returned - set(ids):
            raise ValueError("EFetch returned unexpected PMID values")
        result["request_count"] = client.requests
        with args.out.open("w" if args.overwrite else "x", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
        print(json.dumps({"records": len(returned), "requests": client.requests,
                          "missing_pmids": result["missing_pmids"], "out": str(args.out)}, ensure_ascii=False))
        return 1 if result["missing_pmids"] else 0
    except (RuntimeError, ValueError, ET.ParseError, KeyError, OSError) as exc:
        print(f"PubMed check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

