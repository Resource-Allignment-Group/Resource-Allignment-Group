from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re
from bson.objectid import ObjectId
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

class ReportGenerator:
    """
    Generates monthly reports from existing log files.
    Parses format: TIMESTAMP - LEVEL - [User: ID] [Action: ACTION] [Target: ID] - Details: TEXT
    Reports are generated on-demand (not stored permanently).
    """
    
    def __init__(self, db, log_file_path="large_files_db/reports/system_logs.txt"):
        self.db = db
        self.log_file_path = Path(log_file_path)
        self.styles = getSampleStyleSheet()
        
    def parse_logs(self, start_date, end_date):
        """Parse existing log format."""
        entries = []
        
        if not self.log_file_path.exists():
            return entries
        
        # Regex to parse: 2026-02-09 10:46:58,053 - INFO - [User: ID] [Action: ACTION] [Target: ID] - Details: TEXT
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - \w+ - \[User: ([^\]]+)\] \[Action: ([^\]]+)\](?: \[Target: ([^\]]+)\])? - Details: (.+)'
        
        with open(self.log_file_path, 'r') as f:
            for line in f:
                match = re.match(pattern, line.strip())
                if not match:
                    continue
                
                try:
                    timestamp_str = match.group(1)
                    entry_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    if start_date <= entry_date <= end_date:
                        entries.append({
                            'timestamp': timestamp_str,
                            'user_id': match.group(2),
                            'action': match.group(3),
                            'target_id': match.group(4) or '',
                            'details': match.group(5)
                        })
                except:
                    continue
        
        return entries
    
    def get_user_name(self, user_id):
        """Get user name from ID."""
        if not user_id:
            return "Unknown"
        try:
            user = self.db.get_user_by_id(ObjectId(user_id))
            return user.name if user else f"User-{user_id[:8]}"
        except:
            return f"User-{user_id[:8]}"
    
    def get_equipment_name(self, equipment_id):
        """Get equipment name from ID."""
        if not equipment_id:
            return ""
        try:
            equipment = self.db.get_equipment_by_id(ObjectId(equipment_id))
            return equipment.name if equipment else f"Equipment-{equipment_id[:8]}"
        except:
            return f"Equipment-{equipment_id[:8]}"
    
    def generate_stats(self, entries):
        """Generate summary statistics."""
        stats = {
            'total': len(entries),
            'unique_users': len(set(e['user_id'] for e in entries if e['user_id'])),
            'by_action': defaultdict(int)
        }
        
        for entry in entries:
            stats['by_action'][entry['action']] += 1
        
        return stats
    
    def generate_report(self, start_date, end_date, output_path):
        """
        Generate PDF report.
        
        Args:
            start_date: Start of reporting period
            end_date: End of reporting period  
            output_path: Where to save the PDF (temporary location)
        
        Returns:
            Path to generated PDF file
        """
        
        # Parse logs
        entries = self.parse_logs(start_date, end_date)
        stats = self.generate_stats(entries)
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            leftMargin=0.75*inch, 
            rightMargin=0.75*inch,
            topMargin=0.75*inch, 
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        title = Paragraph(
            f"Monthly Activity Report - {start_date.strftime('%B %Y')}", 
            self.styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Date info
        date_text = f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        gen_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        story.append(Paragraph(gen_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("Summary", self.styles['Heading1']))
        summary_data = [
            ['Metric', 'Count'],
            ['Total Actions', str(stats['total'])],
            ['Unique Users', str(stats['unique_users'])]
        ]
        
        # Add action counts
        for action, count in sorted(stats['by_action'].items()):
            summary_data.append([action.replace('_', ' ').title(), str(count)])
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(summary_table)
        story.append(PageBreak())
        
        # Detailed log
        story.append(Paragraph("Detailed Activity Log", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        if entries:
            log_data = [['Date/Time', 'User', 'Action', 'Target', 'Details']]
            
            for entry in sorted(entries, key=lambda x: x['timestamp']):
                user_name = self.get_user_name(entry['user_id'])
                action = entry['action'].replace('_', ' ').title()
                
                # Resolve target based on action type
                target = ""
                if entry['target_id']:
                    if any(word in entry['action'].lower() for word in ['check', 'equipment']):
                        target = self.get_equipment_name(entry['target_id'])
                    else:
                        target = self.get_user_name(entry['target_id'])
                
                # Truncate long details
                details = entry['details'][:60] + '...' if len(entry['details']) > 60 else entry['details']
                
                log_data.append([
                    entry['timestamp'],
                    user_name,
                    action,
                    target,
                    details
                ])
            
            log_table = Table(log_data, colWidths=[1.1*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.7*inch])
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(log_table)
        else:
            story.append(Paragraph("No activity logged in this period.", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def clear_old_logs(self, days_to_keep=60):
        """Remove log entries older than specified days."""
        if not self.log_file_path.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Read all logs
        kept_lines = []
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        
        with open(self.log_file_path, 'r') as f:
            for line in f:
                try:
                    match = re.match(pattern, line)
                    if match:
                        timestamp_str = match.group(1)
                        entry_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        if entry_date >= cutoff_date:
                            kept_lines.append(line)
                    else:
                        kept_lines.append(line)  # Keep non-matching lines
                except:
                    kept_lines.append(line)
        
        # Write back
        with open(self.log_file_path, 'w') as f:
            for line in kept_lines:
                f.write(line)
        
        print(f"Log cleanup: kept {len(kept_lines)} entries from last {days_to_keep} days")