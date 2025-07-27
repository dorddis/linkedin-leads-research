#!/usr/bin/env python3
"""
LinkedIn Leads Database Export to Excel
This script exports the SQLite database to an Excel file with proper formatting.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def export_database_to_excel(db_name='linkedin_leads.db', output_file=None):
    """Export the LinkedIn leads database to Excel"""
    
    # Check if database exists
    if not os.path.exists(db_name):
        print(f"❌ Database file '{db_name}' not found!")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"linkedin_leads_export_{timestamp}.xlsx"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_name)
        
        # Read data from tables
        print("📊 Reading data from database...")
        
        # Get search results
        search_results_df = pd.read_sql_query("""
            SELECT 
                query,
                title,
                url,
                snippet,
                published_date,
                author,
                score,
                created_at
            FROM search_results 
            ORDER BY created_at DESC
        """, conn)
        
        # Get search sessions
        search_sessions_df = pd.read_sql_query("""
            SELECT 
                user_query,
                total_queries,
                queries_searched,
                created_at
            FROM search_sessions 
            ORDER BY created_at DESC
        """, conn)
        
        # Get summary statistics
        summary_stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_results,
                COUNT(DISTINCT query) as unique_queries,
                COUNT(DISTINCT url) as unique_urls,
                AVG(score) as avg_score,
                MIN(created_at) as first_search,
                MAX(created_at) as last_search
            FROM search_results
        """, conn)
        
        # Get top queries by result count
        top_queries_df = pd.read_sql_query("""
            SELECT 
                query,
                COUNT(*) as result_count,
                AVG(score) as avg_score
            FROM search_results 
            GROUP BY query 
            ORDER BY result_count DESC 
            LIMIT 20
        """, conn)
        
        # Get top URLs by score
        top_urls_df = pd.read_sql_query("""
            SELECT 
                title,
                url,
                snippet,
                score,
                query
            FROM search_results 
            WHERE score > 0
            ORDER BY score DESC 
            LIMIT 50
        """, conn)
        
        conn.close()
        
        print(f"✅ Data loaded successfully!")
        print(f"   - Search Results: {len(search_results_df)} rows")
        print(f"   - Search Sessions: {len(search_sessions_df)} rows")
        print(f"   - Top Queries: {len(top_queries_df)} rows")
        print(f"   - Top URLs: {len(top_urls_df)} rows")
        
        # Create Excel writer
        print(f"📝 Creating Excel file: {output_file}")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Write search results
            search_results_df.to_excel(writer, sheet_name='Search Results', index=False)
            
            # Write search sessions
            search_sessions_df.to_excel(writer, sheet_name='Search Sessions', index=False)
            
            # Write summary statistics
            summary_stats.to_excel(writer, sheet_name='Summary Statistics', index=False)
            
            # Write top queries
            top_queries_df.to_excel(writer, sheet_name='Top Queries', index=False)
            
            # Write top URLs
            top_urls_df.to_excel(writer, sheet_name='Top URLs', index=False)
            
            # Get the workbook and worksheets
            workbook = writer.book
            
            # Format each worksheet
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add filters to headers
                worksheet.auto_filter.ref = worksheet.dimensions
        
        print(f"✅ Excel file created successfully: {output_file}")
        
        # Print summary
        print(f"\n📊 Export Summary:")
        print(f"   - File: {output_file}")
        print(f"   - Sheets: 5 (Search Results, Search Sessions, Summary Statistics, Top Queries, Top URLs)")
        print(f"   - Total Results: {len(search_results_df)}")
        print(f"   - Total Sessions: {len(search_sessions_df)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting database: {str(e)}")
        return False

def show_database_info(db_name='linkedin_leads.db'):
    """Show information about the database"""
    
    if not os.path.exists(db_name):
        print(f"❌ Database file '{db_name}' not found!")
        return
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Database Information: {db_name}")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📋 {table_name}: {count} rows")
        
        # Get recent activity
        cursor.execute("""
            SELECT 
                COUNT(*) as total_results,
                COUNT(DISTINCT query) as unique_queries,
                MAX(created_at) as last_search
            FROM search_results
        """)
        
        stats = cursor.fetchone()
        if stats[0] > 0:
            print(f"\n📈 Recent Activity:")
            print(f"   - Total Results: {stats[0]}")
            print(f"   - Unique Queries: {stats[1]}")
            print(f"   - Last Search: {stats[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")

def main():
    """Main function"""
    print("🚀 LinkedIn Leads Database Export Tool")
    print("=" * 50)
    
    # Show database info
    show_database_info()
    
    print(f"\n📝 Exporting database to Excel...")
    
    # Export to Excel
    success = export_database_to_excel()
    
    if success:
        print(f"\n✅ Export completed successfully!")
        print(f"💡 You can now open the Excel file to view your LinkedIn leads data.")
    else:
        print(f"\n❌ Export failed!")

if __name__ == "__main__":
    main() 