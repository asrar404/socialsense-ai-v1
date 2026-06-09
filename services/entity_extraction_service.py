import re
from flask import current_app
from models.entity import Entity


class EntityExtractionService:
    def __init__(self):
        self._nlp = None

    def _get_nlp(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load('en_core_web_sm')
            except Exception:
                self._nlp = False
        return self._nlp if self._nlp is not False else None

    PERSON_PATTERNS = [
        re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),
        re.compile(r'(?:Mr|Ms|Mrs|Dr|Prof|Sen|Gov|CEO|Founder)\.?\s+[A-Z][a-z]+'),
    ]

    COMPANY_KEYWORDS = ['Inc', 'Corp', 'LLC', 'Ltd', 'Limited', 'Technologies', 'Tech', 'AI',
                        'Software', 'Systems', 'Group', 'Global', 'Industries', 'Enterprises',
                        'Solutions', 'Holdings', 'Company', 'Bancorp', 'Associates']
    COMPANY_PATTERNS = [
        re.compile(r'\b[A-Z][A-Za-z0-9]+(?:Inc|Corp|LLC|Ltd|Limited)\b'),
        re.compile(r'\b[A-Z][a-z]+ (?:and |& )?[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd)\b'),
    ]

    PRODUCT_PATTERNS = [
        re.compile(r'(?:iPhone|iPad|Mac|Windows|Android|PlayStation|Xbox|Kindle|Pixel|Galaxy|Tesla|ChatGPT|GPT-4)'),
        re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+ (?:Pro|Max|Air|Mini|Ultra|Plus)\b'),
    ]

    def extract_from_texts(self, title='', description='', transcript_text='', comments=None):
        entities = {}
        sources_map = {}

        all_texts = []
        if title:
            all_texts.append(('title', title))
        if description:
            all_texts.append(('description', description))
        if transcript_text:
            all_texts.append(('transcript', transcript_text))
        if comments:
            for c in comments:
                all_texts.append(('comment', c if isinstance(c, str) else c.get('text', '')))

        for source, text in all_texts:
            extracted = self._extract_from_single(text)
            for name, entity_type in extracted:
                key = name.lower().strip()
                if key not in entities:
                    entities[key] = {'name': name, 'entity_type': entity_type, 'frequency': 0, 'sources': set()}
                entities[key]['frequency'] += 1
                entities[key]['sources'].add(source)

        nlp = self._get_nlp()
        if nlp:
            for source, text in all_texts:
                doc = nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ('PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'NORP', 'LAW', 'FAC'):
                        mapped = self._spacy_label_to_type(ent.label_)
                        key = ent.text.lower().strip()
                        if key not in entities:
                            entities[key] = {'name': ent.text, 'entity_type': mapped, 'frequency': 0, 'sources': set()}
                        entities[key]['frequency'] += 1
                        entities[key]['sources'].add(source)

        result = []
        for key, data in entities.items():
            source = Entity.SOURCE_COMBINED if len(data['sources']) > 1 else next(iter(data['sources']))
            result.append({
                'name': data['name'],
                'entity_type': data['entity_type'],
                'source': source,
                'frequency': data['frequency'],
            })
        return result

    def _extract_from_single(self, text):
        extracted = []

        for pattern in self.PERSON_PATTERNS:
            for m in pattern.finditer(text):
                extracted.append((m.group(), Entity.PERSON))

        for pattern in self.COMPANY_PATTERNS:
            for m in pattern.finditer(text):
                extracted.append((m.group(), Entity.COMPANY))

        for pattern in self.PRODUCT_PATTERNS:
            for m in pattern.finditer(text):
                extracted.append((m.group(), Entity.PRODUCT))

        for kw in self.COMPANY_KEYWORDS:
            for m in re.finditer(rf'\b[A-Z][A-Za-z0-9]*(?: {re.escape(kw)})', text):
                extracted.append((m.group().strip(), Entity.COMPANY))

        return extracted

    def _spacy_label_to_type(self, label):
        mapping = {
            'PERSON': Entity.PERSON,
            'ORG': Entity.ORGANIZATION,
            'GPE': Entity.LOCATION,
            'PRODUCT': Entity.PRODUCT,
            'EVENT': Entity.EVENT,
            'NORP': Entity.OTHER,
            'LAW': Entity.OTHER,
            'FAC': Entity.LOCATION,
        }
        return mapping.get(label, Entity.OTHER)
