from datetime import datetime

class User:
    def __init__(self, name, email, created_at=None, _id=None):
        self._id = _id
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_db_document(document):
        if not document:
            return None
        return User(
            _id=str(document['_id']),
            name=document['name'],
            email=document['email'],
            created_at=document['created_at']
        )

    def to_dict(self):
        return {
            'id': str(self._id) if self._id else None,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

    def to_document(self):
        return {
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at
        }