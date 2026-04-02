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
def get_recent_records(limit=10, date_filter=None):
    """Get recent records for dashboard with optional date filter."""
    try:
        # If filtering by date, we might want to get all and filter
        if date_filter:
            # Simple filtering logic
            all_records = Record.get_all()
            records = [r for r in all_records if r.date.isoformat().startswith(date_filter)]
            # If limit is specified, slice it
            # records = records[:limit]
        else:
            records = Record.get_recent(limit)

        result = []
        for record in records:
            company = Company.get_by_id(record.company_id)
            result.append({
                '_id': str(record._id),
                'client_name': record.client_name,
                'company_name': company.name if company else 'Unknown',
                'phone': record.phone,
                'processes': record.processes,
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
def save_record(company_name, client_name, phone, processes, total_amount, date_str=None):
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
        
        # Parse date if provided
        record_date = None
        if date_str:
            try:
                record_date = datetime.fromisoformat(date_str)
            except:
                pass

        # Create record
        record = Record(
            company_id=company._id,
            client_name=client_name,
            phone=phone,
            processes=processes,
            total_amount=total_amount,
            date=record_date
        )
        record.save()
        
        return {'success': True, 'id': str(record._id)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def delete_record(record_id):
    """Delete a record by ID."""
    try:
        record = Record.get_by_id(record_id)
        if not record:
            return {'success': False, 'error': 'Record not found'}
        
        record.delete()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def update_record(record_id, client_name, phone, processes, total_amount, date_str=None):
    """Update an existing record."""
    try:
        record = Record.get_by_id(record_id)
        if not record:
            return {'success': False, 'error': 'Record not found'}
        
        # Update fields
        record.client_name = client_name
        record.phone = phone
        record.processes = processes
        record.total_amount = total_amount
        
        if date_str:
            try:
                record.date = datetime.fromisoformat(date_str)
            except:
                pass
        
        record.save()
        return {'success': True}
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
@eel.expose
def get_analysis_data(company_id=None):
    """Aggregate stats and metrics. Supports filtering by specific company_id."""
    try:
        companies = Company.get_all()
        if company_id:
            records = Record.get_by_company(company_id)
        else:
            records = Record.get_all()
        
        # 1. KPI Calculations
        total_revenue = sum(r.total_amount for r in records)
        active_companies = len(companies)
        total_clients = len(records)
        avg_per_client = total_revenue / total_clients if total_clients > 0 else 0
        
        total_processes = 0
        for r in records:
            total_processes += len(r.processes)
            
        # 2. Company Spend & Share
        company_spend = {}
        for r in records:
            c_name = 'Unknown'
            # Find company name
            for c in companies:
                if str(c._id) == str(r.company_id):
                    c_name = c.name
                    break
            company_spend[c_name] = company_spend.get(c_name, 0) + r.total_amount
            
        # 3. Process cost & frequency
        process_stats = {} # {name: {cost: 0, freq: 0}}
        for r in records:
            for p in r.processes:
                name = p.get('name', 'Unknown')
                cost = (p.get('amount') or 0) + (p.get('id_fee') or 0) + (p.get('fine') or 0)
                if name not in process_stats:
                    process_stats[name] = {'cost': 0, 'freq': 0}
                process_stats[name]['cost'] += cost
                process_stats[name]['freq'] += 1
                
        # 4. Timeline Trend (last 30 days)
        from datetime import date, timedelta
        today = date.today()
        timeline = {}
        for i in range(30):
            d = today - timedelta(days=i)
            timeline[d.strftime("%Y-%m-%d")] = 0
            
        for r in records:
            d_str = r.date.strftime("%Y-%m-%d")
            if d_str in timeline:
                timeline[d_str] += r.total_amount
        
        sorted_timeline = sorted(timeline.items())
        
        # 5. Leaderboard (Top 10)
        sorted_records = sorted(records, key=lambda x: x.total_amount, reverse=True)
        leaderboard = []
        for r in sorted_records[:10]:
            c_name = 'Unknown'
            for c in companies:
                if str(c._id) == str(r.company_id):
                    c_name = c.name
                    break
            leaderboard.append({
                'client': r.client_name,
                'company': c_name,
                'amount': r.total_amount,
                'date': r.date.strftime("%b %d, %Y")
            })

        return {
            'success': True,
            'kpis': {
                'total_revenue': total_revenue,
                'active_companies': active_companies,
                'total_clients': total_clients,
                'total_processes': total_processes,
                'avg_per_client': avg_per_client
            },
            'company_data': {
                'labels': list(company_spend.keys()),
                'values': list(company_spend.values())
            },
            'process_data': {
                'labels': list(process_stats.keys()),
                'costs': [s['cost'] for s in process_stats.values()],
                'freqs': [s['freq'] for s in process_stats.values()]
            },
            'timeline_data': {
                'labels': [item[0] for item in sorted_timeline],
                'values': [item[1] for item in sorted_timeline]
            },
            'leaderboard': leaderboard
        }
    except Exception as e:
        print(f"Analysis data error: {e}")
        return {'success': False, 'error': str(e)}
