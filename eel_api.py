"""
Eel API - Backend functions exposed to JavaScript frontend.
"""
import eel
import os
import sys
from datetime import datetime
from bson import ObjectId

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseConnection
from database.models import Company, Record
from utils.pdf_exporter import PDFExporter
from utils.helpers import get_export_directory
from config import AVAILABLE_PROCESSES, SPECIAL_PROCESSES

# Initialize database
db = DatabaseConnection()

def json_serializable(obj):
    """Convert MongoDB objects to JSON-serializable format."""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

@eel.expose
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        companies = Company.get_all()
        records = Record.get_all()
        revenue = Record.get_total_revenue()
        
        return {
            'success': True,
            'companies': len(companies),
            'records': len(records),
            'revenue': revenue
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_recent_records(limit=5):
    """Get recent records for dashboard."""
    try:
        records = Record.get_recent(limit)
        result = []
        
        for record in records:
            company = Company.get_by_id(record.company_id)
            result.append({
                '_id': str(record._id),
                'client_name': record.client_name,
                'company_name': company.name if company else 'Unknown',
                'total_amount': record.total_amount,
                'date': record.date.isoformat() if record.date else None
            })
        
        return result
    except Exception as e:
        print(f"Error getting recent records: {e}")
        return []

@eel.expose
def get_all_companies():
    """Get all companies."""
    try:
        companies = Company.get_all()
        return [
            {
                '_id': str(c._id),
                'name': c.name
            }
            for c in companies
        ]
    except Exception as e:
        print(f"Error getting companies: {e}")
        return []

@eel.expose
def add_company(name):
    """Add a new company."""
    try:
        # Check if company already exists
        companies = Company.get_all()
        for c in companies:
            if c.name.lower() == name.lower():
                return {'success': False, 'error': 'Company already exists'}
        
        company = Company(name=name)
        company.save()
        return {'success': True, 'id': str(company._id)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def delete_company(company_id):
    """Delete a company and its records."""
    try:
        company = Company.get_by_id(company_id)
        if not company:
            return {'success': False, 'error': 'Company not found'}
        
        company.delete()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_company_records(company_id):
    """Get all records for a company."""
    try:
        records = Record.get_by_company(company_id)
        return [
            {
                '_id': str(r._id),
                'client_name': r.client_name,
                'phone': r.phone,
                'processes': r.processes,
                'total_amount': r.total_amount,
                'date': r.date.isoformat() if r.date else None
            }
            for r in records
        ]
    except Exception as e:
        print(f"Error getting company records: {e}")
        return []

@eel.expose
def save_record(company_name, client_name, phone, processes, total_amount):
    """Save a new record."""
    try:
        # Get or create company
        companies = Company.get_all()
        company = None
        for c in companies:
            if c.name.lower() == company_name.lower():
                company = c
                break
        
        if not company:
            # Create new company
            company = Company(name=company_name)
            company.save()
        
        # Create record
        record = Record(
            company_id=company._id,
            client_name=client_name,
            phone=phone,
            processes=processes,
            total_amount=total_amount
        )
        record.save()
        
        return {'success': True, 'id': str(record._id)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def export_company_pdf(company_id):
    """Export company records to PDF."""
    try:
        company = Company.get_by_id(company_id)
        if not company:
            return {'success': False, 'error': 'Company not found'}
        
        records = Record.get_by_company(company_id)
        
        # Generate PDF
        exporter = PDFExporter()
        output_path = os.path.join(
            get_export_directory(),
            f"{company.name.replace(' ', '_')}_records.pdf"
        )
        
        exporter.export_company_records(company, records)
        
        return {'success': True, 'path': output_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_export_path():
    """Get the default export directory path."""
    try:
        return get_export_directory()
    except:
        return os.path.join(os.path.expanduser('~'), 'Desktop', 'Expense Flow')

# Expose the process configurations to frontend
@eel.expose
def get_process_config():
    """Get process configuration."""
    return {
        'available': AVAILABLE_PROCESSES,
        'special': SPECIAL_PROCESSES
    }
