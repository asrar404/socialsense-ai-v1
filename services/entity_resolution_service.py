from models.entity import Entity


class EntityResolutionService:
    def __init__(self):
        self.aliases = {
            'ai': 'Artificial Intelligence',
            'open ai': 'OpenAI',
            'openai': 'OpenAI',
            'msft': 'Microsoft',
            'microsoft': 'Microsoft',
            'goog': 'Google',
            'alphabet': 'Google',
            'appl': 'Apple',
            'tsla': 'Tesla',
            'amzn': 'Amazon',
            'meta': 'Meta',
            'fb': 'Meta',
            'facebook': 'Meta',
            'twitter': 'X',
            'youtube': 'YouTube',
            'instagram': 'Instagram',
            'telegram': 'Telegram',
            'whatsapp': 'WhatsApp',
            'chatgpt': 'ChatGPT',
            'gpt': 'ChatGPT',
            'gpt4': 'ChatGPT',
            'gpt-4': 'ChatGPT',
            'gpt3': 'ChatGPT',
            'gpt-3': 'ChatGPT',
        }

    def normalize(self, name):
        if not name:
            return name
        key = name.lower().strip()
        if key in self.aliases:
            return self.aliases[key]
        return name.strip()

    def add_alias(self, alias, canonical):
        self.aliases[alias.lower().strip()] = canonical.strip()

    def resolve(self, extracted_entities):
        resolved = {}
        for entity in extracted_entities:
            canonical = self.normalize(entity['name'])
            if canonical not in resolved:
                resolved[canonical] = {
                    'name': canonical,
                    'normalized_name': canonical,
                    'entity_type': entity['entity_type'],
                    'source': entity['source'],
                    'frequency': entity['frequency'],
                }
            else:
                resolved[canonical]['frequency'] += entity['frequency']
        return list(resolved.values())
