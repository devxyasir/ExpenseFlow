"""Data models for Expense Flow."""
from datetime import datetime
from bson import ObjectId
from database.connection import db


class Company:
    """Company model."""
    
    def __init__(self, name, _id=None):
        self._id = _id if _id else ObjectId()
        self.name = name
    
    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            _id=data.get('_id')
        )
    
    def save(self):
        """Save company to database."""
        collection = db.get_companies_collection()
        if collection is None:
            raise ConnectionError("Database not connected")
        data = self.to_dict()
        collection.replace_one({'_id': self._id}, data, upsert=True)
        return self._id
    
    @classmethod
    def get_all(cls):
        """Get all companies."""
        collection = db.get_companies_collection()
        if collection is None:
            return []
        return [cls.from_dict(doc) for doc in collection.find().sort('name', 1)]
    
    @classmethod
    def get_by_id(cls, company_id):
        """Get company by ID."""
        collection = db.get_companies_collection()
        if collection is None:
            return None
        doc = collection.find_one({'_id': ObjectId(company_id) if isinstance(company_id, str) else company_id})
        return cls.from_dict(doc) if doc else None
    
    def delete(self):
        """Delete company and all its records."""
        collection = db.get_companies_collection()
        if collection is None:
            return
        # Delete all records for this company
        Record.delete_by_company(self._id)
        # Delete company
        collection.delete_one({'_id': self._id})


class Record:
    """Client record model."""
    
    def __init__(self, company_id, client_name, phone, processes, total_amount, 
                 date=None, _id=None):
        self._id = _id if _id else ObjectId()
        self.company_id = company_id if isinstance(company_id, ObjectId) else ObjectId(company_id)
        self.client_name = client_name
        self.phone = phone
        self.processes = processes  # List of dicts: [{name, amount, fine, ...}]
        self.total_amount = total_amount
        self.date = date if date else datetime.now()
    
    def to_dict(self):
        return {
            '_id': self._id,
            'company_id': self.company_id,
            'client_name': self.client_name,
            'phone': self.phone,
            'processes': self.processes,
            'total_amount': self.total_amount,
            'date': self.date,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            company_id=data.get('company_id'),
            client_name=data.get('client_name'),
            phone=data.get('phone'),
            processes=data.get('processes', []),
            total_amount=data.get('total_amount', 0),
            date=data.get('date'),
            _id=data.get('_id')
        )
    
    def save(self):
        """Save record to database."""
        collection = db.get_records_collection()
        if collection is None:
            raise ConnectionError("Database not connected")
        data = self.to_dict()
        collection.replace_one({'_id': self._id}, data, upsert=True)
        return self._id
    
    @classmethod
    def get_by_company(cls, company_id):
        """Get all records for a company."""
        collection = db.get_records_collection()
        if collection is None:
            return []
        company_id = ObjectId(company_id) if isinstance(company_id, str) else company_id
        return [cls.from_dict(doc) for doc in collection.find({'company_id': company_id}).sort('date', -1)]
    
    @classmethod
    def get_all(cls):
        """Get all records."""
        collection = db.get_records_collection()
        if collection is None:
            return []
        return [cls.from_dict(doc) for doc in collection.find().sort('date', -1)]
    
    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        collection = db.get_records_collection()
        if collection is None:
            return None
        doc = collection.find_one({'_id': ObjectId(record_id) if isinstance(record_id, str) else record_id})
        return cls.from_dict(doc) if doc else None
    
    @classmethod
    def get_recent(cls, limit=5):
        """Get recent records."""
        collection = db.get_records_collection()
        if collection is None:
            return []
        return [cls.from_dict(doc) for doc in collection.find().sort('date', -1).limit(limit)]
    
    @classmethod
    def get_total_revenue(cls):
        """Get total revenue across all records."""
        collection = db.get_records_collection()
        if collection is None:
            return 0
        result = collection.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
        ])
        result = list(result)
        return result[0]['total'] if result else 0
    
    @classmethod
    def delete_by_company(cls, company_id):
        """Delete all records for a company."""
        collection = db.get_records_collection()
        if collection is None:
            return
        company_id = ObjectId(company_id) if isinstance(company_id, str) else company_id
        collection.delete_many({'company_id': company_id})
    
    def delete(self):
        """Delete this record."""
        collection = db.get_records_collection()
        if collection is None:
            return
        collection.delete_one({'_id': self._id})
