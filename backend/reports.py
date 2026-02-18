from flask import send_file, after_this_request, jsonify
from datetime import datetime
from pathlib import Path
import tempfile
import os

def setup_report_routes(app, report_generator):
    
    # Route used to manually dowload a monthly report 
    # from the admin dashboard page
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
                return "Report generation failed: File not created"

            # Register a cleanup function to run after the response is sent
            file_handle = open(temp_path, 'rb')
            def stream_and_close():
                yield from file_handle
                file_handle.close()
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as e:
                    app.logger.error(f"Error deleting temp file: {e}")

            # Return the custom response class using the generator
            return app.response_class(
                stream_and_close(),
                mimetype='application/pdf',
                headers={
                    "Content-Disposition": f"attachment; filename=Report_{start_date.strftime('%Y_%m_%d')}.pdf"
                }
            )
            
        except Exception as e:
            return jsonify({"error": str(e)})