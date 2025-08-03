from flask import Flask, request, render_template, send_file, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import os
import re
from datetime import datetime
import uuid

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('court_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries
                 (id TEXT PRIMARY KEY, case_type TEXT, case_number TEXT, filing_year TEXT,
                  response TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

async def fetch_case_data(case_type, case_number, filing_year, captcha_token):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to Delhi High Court case status page
        url = "https://delhihighcourt.nic.in/case-status"
        await page.goto(url)
        
        # Fill form
        await page.select_option('select[name="case_type"]', value=case_type)
        await page.fill('input[name="case_number"]', case_number)
        await page.fill('input[name="filing_year"]', filing_year)
        await page.fill('input[name="captcha"]', captcha_token)
        
        # Submit form
        await page.click('button[type="submit"]')
        
        # Wait for results
        await page.wait_for_selector('div.result-table', timeout=10000)
        
        # Parse results
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        data = {
            'parties': '',
            'filing_date': '',
            'next_hearing': '',
            'pdf_links': []
        }
        
        try:
            # Extract parties
            parties_elem = soup.select_one('div#parties')
            if parties_elem:
                data['parties'] = parties_elem.text.strip()
            
            # Extract dates
            filing_elem = soup.select_one('div#filing-date')
            if filing_elem:
                data['filing_date'] = filing_elem.text.strip()
                
            hearing_elem = soup.select_one('div#next-hearing')
            if hearing_elem:
                data['next_hearing'] = hearing_elem.text.strip()
            
            # Extract latest order PDF
            pdf_elem = soup.select_one('a.order-link:last-child')
            if pdf_elem and 'href' in pdf_elem.attrs:
                data['pdf_links'].append(pdf_elem['href'])
                
        except Exception as e:
            return {'error': f'Parsing failed: {str(e)}'}
            
        await browser.close()
        return data

def store_query(case_type, case_number, filing_year, response):
    conn = sqlite3.connect('court_data.db')
    c = conn.cursor()
    query_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    c.execute('INSERT INTO queries (id, case_type, case_number, filing_year, response, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
              (query_id, case_type, case_number, filing_year, str(response), timestamp))
    conn.commit()
    conn.close()
    return query_id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
async def fetch():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    filing_year = request.form['filing_year']
    captcha_token = request.form['captcha_token']
    
    if not all([case_type, case_number, filing_year, captcha_token]):
        return jsonify({'error': 'All fields are required'}), 400
        
    try:
        result = await fetch_case_data(case_type, case_number, filing_year, captcha_token)
        query_id = store_query(case_type, case_number, filing_year, result)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch data: {str(e)}'}), 500

@app.route('/download/<path:pdf_url>')
def download_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        return send_file(
            response.raw,
            as_attachment=True,
            download_name='court_order.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Failed to download PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)