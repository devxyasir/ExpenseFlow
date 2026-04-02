"""Seed record database with dummy data."""
import sys
import os
import random
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseConnection
from database.models import Company, Record

def seed():
    print("Initiating database connection...")
    db = DatabaseConnection()
    
    # Configuration
    companies_names = ["Alpha Corp", "Beta Solutions", "Gamma Enterprises", "Delta Logistics", "Epsilon Group"]
    processes_list = [
        'Typing', 'Labour Fees', 'Labour Insurance', 'ILOE Insurance Fine', 
        'Voucher', 'New Establishment', 'Labour Fine', 'Taqeem', 
        'Entry Permit', 'Change Status', 'Tawjeeh Class', 'ILOE Insurance', 
        'Medical + ID', 'Stamping', 'Renew Establishment', 'Update Express', 
        'Immegration Fine', 'Cancellation'
    ]
    
    # Process special handling logic emulations
    # We'll just assign regular amounts for most, and handle id_fee/fine as sub-props for Medical + ID
    
    print(f"Creating {len(companies_names)} companies...")
    for comp_name in companies_names:
        # Check if exists to avoid duplicates
        existing = Company.get_all()
        company = next((c for c in existing if c.name == comp_name), None)
        
        if not company:
            company = Company(name=comp_name)
            company.save()
            print(f"Created Company: {comp_name}")
        else:
            print(f"Found existing Company: {comp_name}")
            
        # Create 10 clients for this company
        for i in range(1, 11):
            client_name = f"{comp_name} Client {i}"
            phone = f"+971 5{random.randint(0,9)} {random.randint(100,999)} {random.randint(1000,9999)}"
            
            # Select 3-5 processes
            num_proc = random.randint(3, 5)
            selected_proc_names = random.sample(processes_list, num_proc)
            
            record_processes = []
            total_amount = 0
            
            for p_name in selected_proc_names:
                amount = random.randint(300, 900)
                p_item = {
                    'name': p_name,
                    'amount': amount,
                    'extra': 0,
                    'extraType': ''
                }
                
                # Special cases for dummy data variety
                if p_name == 'Medical + ID':
                    id_fee = random.randint(100, 300)
                    p_item['id_fee'] = id_fee
                    total_amount += id_fee
                
                total_amount += amount
                record_processes.append(p_item)
            
            # Create a spread of dates over the last 30 days
            days_ago = random.randint(0, 30)
            record_date = datetime.now() - timedelta(days=days_ago)
            
            record = Record(
                company_id=company._id,
                client_name=client_name,
                phone=phone,
                processes=record_processes,
                total_amount=total_amount,
                date=record_date
            )
            record.save()
            
        print(f"  - Added 10 clients to {comp_name}")

    print("\nSuccess! Database seeded with dummy data.")

if __name__ == "__main__":
    seed()
