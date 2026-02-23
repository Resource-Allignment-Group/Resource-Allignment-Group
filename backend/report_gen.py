from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# Formats and builds monthly reports from existing log files
# The monthly reports are not stored in the backend or Oracle volume
# They are either immediately emailed to the admin(s) or downloaded
class ReportGenerator:
    def __init__(self, db, log_file_path="large_files_db/reports/system_logs.txt"):
        self.db = db
        self.log_file_path = Path(log_file_path)
        self.styles = getSampleStyleSheet()

    # Parse the system_logs.txt file for system interactions
    def parse_logs(self, start_date, end_date):
        entries = []
        
        if not self.log_file_path.exists():
            return entries
        
        # Regex to parse: 2026-02-09 10:46:58,053 - INFO - [User: ID] [Action: ACTION] [Target: TEXT] - [Details: TEXT]
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - \w+ - \[User: ([^\]]+)\] \[Action: ([^\]]+)\](?: \[Target: ([^\]]+)\])?(?: \[Details: ([^\]]+)\])?'
        
        # Open the file and use the regex to parse out UUIDs and other info
        with open(self.log_file_path, 'r') as f:
            for line in f:
                match = re.match(pattern, line.strip())
                if not match: continue
                try:
                    timestamp_str = match.group(1)
                    entry_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Captures each part of the log within the monthly date range
                    if start_date <= entry_date <= end_date:
                        entries.append({
                            'timestamp': entry_date,
                            'user_id': match.group(2),
                            'action': match.group(3),
                            'target_id': match.group(4) or '',
                            'details': match.group(5) or '',
                        })
                # If one log/line is malformed, skip it
                except:
                    continue
        return entries
    
    # Generates a summary for the cover page of the monthly report
    def generate_stats(self, entries):
        stats = {
            'total': len(entries),
            'unique_users': len(set(e['user_id'] for e in entries if e['user_id'])),
            'by_action': defaultdict(int)
        }
        for entry in entries:
            stats['by_action'][entry['action']] += 1
        return stats
    
    # Convert the log actions into more informative text
    def map_actions(self, action):
        action_vals = {
            "CHECK_OUT": "Equipment Checkout",
            "CHECK_IN": "Equipment Return",
            "ADD_USER": "User Registered",
            "DELETE_USER": "User Deleted",
            "UPDATE_ROLE": "Role Updated",
            "ADD_EQUIPMENT": "Equipment Added",
            "DELETE_EQUIPMENT": "Equipment Deleted"
        }
        return action_vals.get(action, action.replace("_", " ").title())

    # Displays text based on the logged action
    def get_detailed_info(self, entry):
        action = entry['action']
        details = entry['details']
        # Output role in human readible format
        if action == "UPDATE_ROLE":
            role_map = {'a': 'Admin', 'u': 'User', 's': 'Superintendent'}
            return f"Role changed to: {role_map.get(details.strip(), details)}"
        # Report if equip is damaged
        if action == "CHECK_IN":
            return f"{details}" if details else "No condition noted"

        return details

    # Generates the monthly report with all relevant data
    # The start and end of the reporting period is also displayed
    def generate_report(self, start_date, end_date, output_path):
        # Retrieve logs and statistics from existing file
        entries = self.parse_logs(start_date, end_date)
        stats = self.generate_stats(entries)
        
        # Define margins to maximize space
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            leftMargin=0.4*inch, 
            rightMargin=0.5*inch,
            topMargin=0.75*inch, 
            bottomMargin=0.75*inch
        )
        story = []
        
        # Create the doc title
        story.append(Paragraph("Monthly Activity Report", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("MAFES Equipment Management System", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Adjust font style/size
        meta_style = self.styles['Normal']
        meta_style.fontSize = 11
        
        # Display date range for logging info being displayed
        # Display date the report was generated
        date_range_text = f"<b>Period:</b> {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(date_range_text, meta_style))
        story.append(Spacer(1, 0.05*inch))
        gen_text = f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        story.append(Paragraph(gen_text, meta_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary content
        story.append(Paragraph("Executive Summary", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        summary_data = [['Activity Metric', 'Total Count']]
        summary_data.append(['Total System Interactions', str(stats['total'])])
        summary_data.append(['Active Staff Members', str(stats['unique_users'])])
        
        for action, count in sorted(stats['by_action'].items()):
            summary_data.append([self.map_actions(action), str(count)])

        st = Table(summary_data, colWidths=[3*inch, 1.5*inch], hAlign='LEFT')
        st.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.silver),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(st)
        story.append(PageBreak())

        # Table of all log data
        story.append(Paragraph("Detailed Transaction Log", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        column_name = [['Time', 'User', 'Action', 'Target', 'Details']]
        cell_style = self.styles['Normal']
        cell_style.fontSize = 10
        cell_style.leading = 10

        # Load parsed log data into the table
        for entry in sorted(entries, key=lambda x: x['timestamp']):
            user_name = entry['user_id']
            action_name = self.map_actions(entry['action'])
            target_name = entry['target_id'] or "N/A"
            
            report_text = self.get_detailed_info(entry)
            # Format log entries into table rows
            column_name.append([
                Paragraph(entry['timestamp'].strftime('%m/%d %H:%M'), cell_style),
                Paragraph(user_name, cell_style),
                Paragraph(action_name, cell_style),
                Paragraph(target_name, cell_style),
                Paragraph(report_text, cell_style)
            ])

        # Format the table
        lt = Table(column_name, colWidths=[.9*inch, 1.1*inch, 1.2*inch, 2.6*inch, 1.7*inch], hAlign='LEFT')
        lt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.silver),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
        ]))
        
        # Build the doc
        story.append(lt)
        doc.build(story)
        return output_path

    # Delete all old log entries from the system_logs.txt file every 60 days
    # This is so that even the day after the monthly report is generated,
    # the admin can still generate a report with the data from the month prior
    def clear_old_logs(self, days_to_keep=60):
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
        