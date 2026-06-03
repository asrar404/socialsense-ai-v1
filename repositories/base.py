from database import db


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, entity_id):
        return self.model.query.get(entity_id)

    def get_all(self):
        return self.model.query.all()

    def create(self, **kwargs):
        entity = self.model(**kwargs)
        db.session.add(entity)
        db.session.commit()
        return entity

    def update(self, entity, **kwargs):
        for key, value in kwargs.items():
            setattr(entity, key, value)
        db.session.commit()
        return entity

    def delete(self, entity):
        db.session.delete(entity)
        db.session.commit()

    def count(self):
        return self.model.query.count()
