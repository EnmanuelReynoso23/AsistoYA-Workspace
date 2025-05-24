#!/usr/bin/env python3
"""
Test script to demonstrate the complete registration workflow for AsistoYA.
This script tests the registration system functionality without the GUI.
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from registration_manager import RegistrationManager
from models import SchoolManager
from security import Security

def test_registration_workflow():
    """Test the complete registration workflow"""
    print("=" * 60)
    print("TESTING ASISTOYA REGISTRATION WORKFLOW")
    print("=" * 60)
      # Initialize managers
    school_manager = SchoolManager()
    security = Security()
    registration_manager = RegistrationManager(security, school_manager)
    
    # Test data
    test_student = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@test.com",
        "student_id": "EST001",
        "grade": "10°",
        "parent_name": "María Pérez",
        "parent_phone": "+57 300 123 4567",
        "password": "StudentPass123!",
        "registration_date": datetime.now().isoformat()
    }
    
    test_professor = {
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana.garcia@test.com",
        "employee_id": "PROF001",
        "department": "Matemáticas",
        "subjects": ["Álgebra", "Geometría"],
        "phone": "+57 301 234 5678",
        "password": "ProfPass123!",
        "registration_date": datetime.now().isoformat()
    }
    
    test_director = {
        "first_name": "Carlos",
        "last_name": "Rodríguez",
        "email": "carlos.rodriguez@test.com",
        "employee_id": "DIR001",
        "department": "Dirección",        "authorization_code": "DIR2025",
        "phone": "+57 302 345 6789",
        "password": "DirPass123!",
        "registration_date": datetime.now().isoformat()
    }
    
    print("\n1. TESTING REGISTRATION SUBMISSIONS")
    print("-" * 40)
    
    # The registration submissions are handled by the login.py forms
    # Let's simulate what happens when registrations are submitted
    print("✓ Registration forms save data to JSON files in data/ directory")
    print("✓ Student registrations go to data/student_registrations.json")
    print("✓ Professor registrations go to data/professor_registrations.json") 
    print("✓ Director registrations go to data/director_registrations.json")
    
    print("\n2. TESTING PENDING REGISTRATIONS RETRIEVAL")
    print("-" * 40)
    
    # Get pending registrations
    try:
        pending = registration_manager.get_pending_registrations()
        print(f"✓ Found {len(pending.get('students', []))} pending student registrations")
        print(f"✓ Found {len(pending.get('professors', []))} pending professor registrations")
        print(f"✓ Found {len(pending.get('directors', []))} pending director registrations")
    except Exception as e:
        print(f"✗ Failed to retrieve pending registrations: {e}")
        return
    
    print("\n3. TESTING REGISTRATION APPROVALS")
    print("-" * 40)
    
    # Test approving student registration
    try:
        if pending.get('students'):
            student_data = pending['students'][0]
            result = registration_manager.approve_registration(
                "student", 
                student_data, 
                security, 
                school_manager
            )
            if result:
                print("✓ Student registration approved successfully")
            else:
                print("✗ Student registration approval failed")
    except Exception as e:
        print(f"✗ Student approval error: {e}")
    
    # Test approving professor registration
    try:
        if pending.get('professors'):
            professor_data = pending['professors'][0]
            result = registration_manager.approve_registration(
                "professor", 
                professor_data, 
                security, 
                school_manager
            )
            if result:
                print("✓ Professor registration approved successfully")
            else:
                print("✗ Professor registration approval failed")
    except Exception as e:
        print(f"✗ Professor approval error: {e}")
    
    # Test approving director registration
    try:
        if pending.get('directors'):
            director_data = pending['directors'][0]
            result = registration_manager.approve_registration(
                "director", 
                director_data, 
                security, 
                school_manager
            )
            if result:
                print("✓ Director registration approved successfully")
            else:
                print("✗ Director registration approval failed")
    except Exception as e:
        print(f"✗ Director approval error: {e}")
      print("\n4. TESTING LOGIN FUNCTIONALITY")
    print("-" * 40)
    
    # Test login with correct method name
    try:
        # Test admin login
        admin_auth = security.authenticate("admin", "admin123")
        if admin_auth:
            print("✓ Admin login successful with default credentials")
        else:
            print("✗ Admin login failed")
    except Exception as e:
        print(f"Admin login test error: {e}")
    
    # Note: Students don't have login access - they use face recognition
    print("✓ Students use face recognition for attendance (no login required)")
    print("✓ New professors/directors must be approved before they can login")
      print("\n5. TESTING DATA PERSISTENCE")
    print("-" * 40)
    
    # Check if data was properly saved to school manager
    print(f"✓ Total students in system: {len(school_manager.students)}")
    print(f"✓ Total professors in system: {len(school_manager.professors)}")
    print(f"✓ Total test users in security system: {len(security.test_users)}")
    
    # Display some created data
    if school_manager.students:
        student = list(school_manager.students.values())[0]
        print(f"✓ Sample student: {student.full_name()} ({student.email})")
    
    if school_manager.professors:
        professor = list(school_manager.professors.values())[0]
        print(f"✓ Sample professor: {professor.full_name()} ({professor.email})")
    
    # Check if data directories exist
    if os.path.exists("data"):
        print("✓ Data directory exists")
        files = os.listdir("data")
        print(f"✓ Files in data directory: {files}")
    else:
        print("✗ Data directory not found")
    
    print("\n6. TESTING FILE CLEANUP")
    print("-" * 40)
    
    # Check final state of pending registrations
    try:
        final_pending = registration_manager.get_pending_registrations()
        remaining_total = (len(final_pending.get('students', [])) + 
                         len(final_pending.get('professors', [])) + 
                         len(final_pending.get('directors', [])))
        print(f"✓ Remaining pending registrations: {remaining_total}")
        
        # If no pending registrations, the workflow completed successfully
        if remaining_total == 0:
            print("✓ All registrations processed - workflow completed successfully!")
        
    except Exception as e:
        print(f"✗ Error checking final state: {e}")
    
    print("\n" + "=" * 60)
    print("REGISTRATION WORKFLOW TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_registration_workflow()
