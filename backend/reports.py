from flask import send_file, after_this_request, jsonify
from datetime import datetime
from pathlib import Path
import tempfile
import os

def setup_report_routes(app, report_generator):
    """Add fixed report routes to Flask app."""
    
    @app.route('/download_monthly_report', methods=['GET'])
    def download_report():
        try:
            today = datetime.now()
            # Default to current month's activity
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today
            
            # Create a unique temp file
            temp_dir = Path(tempfile.gettempdir())
            temp_path = temp_dir / f"manual_report_{os.getpid()}_{datetime.now().strftime('%H%M%S')}.pdf"
            
            # Generate the PDF
            report_generator.generate_report(start_date, end_date, str(temp_path))
            
            # Ensure the file exists before sending
            if not temp_path.exists():
                return "Report generation failed: File not created", 500

            # Register a cleanup function to run after the response is sent
            @after_this_request
            def remove_file(response):
                try:
                    if temp_path.exists():
                        os.remove(temp_path)
                except Exception as e:
                    app.logger.error(f"Error deleting temp file: {e}")
                return response

            return send_file(
                str(temp_path),
                as_attachment=True,
                download_name=f"Report_{start_date.strftime('%Y_%m_%d')}.pdf",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            print(f"Download Route Error: {e}")
            return jsonify({"error": str(e)}), 500