import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import spacy
except Exception:  # pragma: no cover
    spacy = None

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
WEBSITE_RE = re.compile(r"(?:https?://)?(?:www\.)?[\w-]+\.(?:com|org|net|io|in|co)(?:\.[a-z]{2})?", re.I)
SOCIAL_RE = re.compile(r"(?:linkedin\.com|twitter\.com|x\.com|facebook\.com|instagram\.com)/[^\s]+", re.I)
DESIGNATION_HINTS = ("manager", "director", "engineer", "founder", "ceo", "cto", "sales", "marketing", "consultant")
COMPANY_HINTS = ("pvt", "ltd", "llc", "inc", "technologies", "solutions", "systems", "group", "corp")


@dataclass
class ExtractedFields:
    name: str = ""
    designation: str = ""
    company: str = ""
    mobile: str = ""
    alternate_mobile: str = ""
    email: str = ""
    website: str = ""
    address: str = ""
    social_links: str = ""
    confidence_score: float = 0


class BusinessCardFieldExtractor:
    """
    Two-stage field extractor:
      1. Regex + spaCy NER rules (always runs)
      2. Trained sklearn joblib model predictions (runs if a model path is supplied)

    ML model predictions take priority over rule-based results for fields where
    the model returns a non-empty value.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.nlp = None
        self._ml_model = None

        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    self.nlp = spacy.blank("en")
                except Exception:
                    pass

        if model_path:
            self._load_ml_model(model_path)

    # ── ML model management ───────────────────────────────────────────────────

    def _load_ml_model(self, model_path: str) -> None:
        """Load a trained joblib sklearn pipeline.  Fails silently."""
        try:
            import joblib

            model_file = Path(model_path)
            if not model_file.exists():
                logger.warning("ML model file not found: %s — using rules only.", model_path)
                return
            self._ml_model = joblib.load(model_path)
            logger.info("Loaded ML field extractor model: %s", model_path)
        except Exception as exc:
            logger.warning("Failed to load ML model from %s: %s — using rules only.", model_path, exc)
            self._ml_model = None

    def _predict_with_ml(self, raw_text: str) -> dict:
        """Run sklearn pipeline prediction. Returns entity dict or empty dict on failure."""
        if self._ml_model is None:
            return {}
        try:
            prediction = self._ml_model.predict([raw_text])[0]
            # prediction is a JSON-encoded entity dict
            if isinstance(prediction, str):
                return json.loads(prediction)
            return prediction if isinstance(prediction, dict) else {}
        except Exception as exc:
            logger.debug("ML model prediction failed: %s", exc)
            return {}

    # ── Main extraction entry point ───────────────────────────────────────────

    def extract(self, raw_text: str) -> ExtractedFields:
        # Stage 1: rule-based extraction
        rule_fields = self._extract_with_rules(raw_text)

        # Stage 2: ML model prediction (if available)
        ml_entities = self._predict_with_ml(raw_text)

        if not ml_entities:
            return rule_fields

        # Merge: ML wins for fields it provides; rules fill gaps
        return ExtractedFields(
            name=ml_entities.get("name") or rule_fields.name,
            designation=ml_entities.get("designation") or rule_fields.designation,
            company=ml_entities.get("company") or rule_fields.company,
            mobile=ml_entities.get("mobile") or rule_fields.mobile,
            alternate_mobile=ml_entities.get("alternate_mobile") or rule_fields.alternate_mobile,
            email=ml_entities.get("email") or rule_fields.email,
            website=ml_entities.get("website") or rule_fields.website,
            address=ml_entities.get("address") or rule_fields.address,
            social_links=ml_entities.get("social_links") or rule_fields.social_links,
            # Slight confidence boost when ML model contributes
            confidence_score=min(rule_fields.confidence_score + 5.0, 100.0),
        )

    # ── Rule-based extraction ─────────────────────────────────────────────────

    def _extract_with_rules(self, raw_text: str) -> ExtractedFields:
        lines = [line.strip(" |,") for line in raw_text.splitlines() if line.strip()]
        text = "\n".join(lines)
        emails = EMAIL_RE.findall(text)
        phones = [self._clean_phone(match) for match in PHONE_RE.findall(text)]
        websites = WEBSITE_RE.findall(text)
        socials = SOCIAL_RE.findall(text)

        designation = self._first_matching_line(lines, DESIGNATION_HINTS)
        company = self._first_matching_line(lines, COMPANY_HINTS)
        name = self._extract_name(lines, text, emails, phones, designation, company)
        address = self._extract_address(lines, {name, designation, company, *(emails or []), *(websites or [])})
        score = self._confidence([name, designation, company, phones[:1], emails[:1], websites[:1], address])
        return ExtractedFields(
            name=name,
            designation=designation,
            company=company,
            mobile=phones[0] if phones else "",
            alternate_mobile=phones[1] if len(phones) > 1 else "",
            email=emails[0] if emails else "",
            website=websites[0] if websites else "",
            address=address,
            social_links=", ".join(socials),
            confidence_score=score,
        )

    def _extract_name(self, lines: list[str], text: str, emails: list[str], phones: list[str], designation: str, company: str) -> str:
        if self.nlp:
            doc = self.nlp(text)
            for ent in getattr(doc, "ents", []):
                if ent.label_ == "PERSON":
                    return ent.text
        excluded = {designation.lower(), company.lower()}
        for line in lines[:5]:
            clean = line.strip()
            if clean.lower() in excluded or EMAIL_RE.search(clean) or PHONE_RE.search(clean) or WEBSITE_RE.search(clean):
                continue
            if 1 <= len(clean.split()) <= 4 and not any(char.isdigit() for char in clean):
                return clean
        return ""

    def _first_matching_line(self, lines: list[str], hints: tuple[str, ...]) -> str:
        for line in lines:
            if any(hint in line.lower() for hint in hints):
                return line
        return ""

    def _extract_address(self, lines: list[str], excluded: set[str]) -> str:
        candidates = []
        for line in lines:
            lower = line.lower()
            if any(item and item.lower() in lower for item in excluded):
                continue
            if any(token in lower for token in ("road", "street", "floor", "sector", "city", "pin", "india", "suite")):
                candidates.append(line)
        return ", ".join(candidates[:3])

    def _clean_phone(self, value: str) -> str:
        return re.sub(r"[^\d+]", "", value)

    def _confidence(self, field_buckets: list) -> float:
        """Percentage of field buckets that have at least one non-empty value."""
        filled = sum(1 for f in field_buckets if (f[0] if isinstance(f, list) else f))
        return round((filled / len(field_buckets)) * 100, 2) if field_buckets else 0.0

