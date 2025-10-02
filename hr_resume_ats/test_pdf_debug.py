#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Debug Test Script
This script helps diagnose PDF processing issues
"""

import io
import sys
import os

try:
    import PyPDF2
    print("✓ PyPDF2 is available")
    print(f"PyPDF2 version: {PyPDF2.__version__}")
except ImportError:
    print("✗ PyPDF2 is not installed")
    sys.exit(1)

def test_pdf_file(file_path):
    """Test PDF file processing"""
    print(f"\n=== Testing PDF file: {file_path} ===")
    
    if not os.path.exists(file_path):
        print(f"✗ File does not exist: {file_path}")
        return False
    
    try:
        # Read file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"✓ File size: {len(file_data)} bytes")
        
        # Check PDF header
        if not file_data.startswith(b'%PDF'):
            print(f"✗ Invalid PDF header. First 10 bytes: {file_data[:10]}")
            return False
        
        print(f"✓ Valid PDF header: {file_data[:8]}")
        
        # Create PDF reader
        pdf_file = io.BytesIO(file_data)
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            print(f"✓ PDF reader created successfully")
        except Exception as reader_error:
            print(f"✗ Failed to create PDF reader: {str(reader_error)}")
            print(f"Error type: {type(reader_error).__name__}")
            return False
        
        # Check encryption
        if pdf_reader.is_encrypted:
            print("✗ PDF is encrypted")
            return False
        
        print("✓ PDF is not encrypted")
        
        # Check pages
        num_pages = len(pdf_reader.pages)
        print(f"✓ Number of pages: {num_pages}")
        
        if num_pages == 0:
            print("✗ PDF has no pages")
            return False
        
        # Extract text
        text = ''
        successful_pages = 0
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + '\n'
                    successful_pages += 1
                    print(f"✓ Page {page_num + 1}: {len(page_text)} characters")
                else:
                    print(f"⚠ Page {page_num + 1}: No text found")
            except Exception as page_error:
                print(f"✗ Page {page_num + 1}: Error - {str(page_error)}")
        
        print(f"✓ Successfully processed {successful_pages}/{num_pages} pages")
        
        extracted_text = text.strip()
        if not extracted_text:
            print("✗ No text could be extracted")
            return False
        
        print(f"✓ Total extracted text: {len(extracted_text)} characters")
        print(f"First 200 characters: {extracted_text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("PDF Debug Test Script")
    print("=" * 50)
    
    # Test with a sample PDF file
    test_file = input("Enter PDF file path to test (or press Enter to skip): ").strip()
    
    if test_file:
        success = test_pdf_file(test_file)
        if success:
            print("\n✓ PDF processing test PASSED")
        else:
            print("\n✗ PDF processing test FAILED")
    else:
        print("\nNo file provided. Test skipped.")
        print("\nTo use this script:")
        print("1. Save a PDF file you want to test")
        print("2. Run this script again and provide the file path")
        print("3. Check the detailed output for any issues")