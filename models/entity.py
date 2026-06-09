from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Entity(db.Model):
    __tablename__ = 'entities'

    PERSON = 'PERSON'
    COMPANY = 'COMPANY'
    BRAND = 'BRAND'
    PRODUCT = 'PRODUCT'
    ORGANIZATION = 'ORGANIZATION'
    LOCATION = 'LOCATION'
    EVENT = 'EVENT'
    TOPIC = 'TOPIC'
    OTHER = 'OTHER'

    SOURCE_TITLE = 'title'
    SOURCE_DESCRIPTION = 'description'
    SOURCE_TRANSCRIPT = 'transcript'
    SOURCE_COMMENT = 'comment'
    SOURCE_COMBINED = 'combined'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, index=True)
    name = db.Column(db.String(300), nullable=False)
    normalized_name = db.Column(db.String(300), nullable=False)
    entity_type = db.Column(db.String(30), nullable=False, default=OTHER)
    source = db.Column(db.String(20), nullable=False, default=SOURCE_COMBINED)
    frequency = db.Column(db.Integer, default=0)
    importance_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    analysis = db.relationship('Analysis', backref=db.backref('entities', lazy='dynamic', cascade='all, delete-orphan'))
    mentions = db.relationship('EntityMention', backref='entity', lazy='dynamic', cascade='all, delete-orphan')
    contexts = db.relationship('EntityContext', backref='entity', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Entity {self.name} ({self.entity_type})>'
