from flask import jsonify, session
from datetime import datetime
from pathlib import Path
import tempfile
import os
from bson.objectid import ObjectId

# Route(s) related to downloading monthly reports

def setup_report_routes(app, report_generator):
    
    @app.route('/download_monthly_report', methods=['GET'])
    def download_report():
        """Allow admins to manually download a monthly report from the Dashboard"""
        if "id" not in session:
            return jsonify({"result": False, "message": "Not logged in"}), 401
        try:
            db = app.db
            user_obj = db.get_user_by_id(ObjectId(session["id"]))
            # Role 'a' = admin
            if not user_obj or user_obj.role != "a":
                return jsonify({"result": False, "message": "Admin only"}), 403
        except Exception:
            return jsonify({"result": False, "message": "Invalid session"}), 401
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
            # This will allow the cleanup func to run after the doc
            # has been successfully sent
            return app.response_class(
                stream_and_close(),
                mimetype='application/pdf',
                headers={
                    "Content-Disposition": f"attachment; filename=Report_{start_date.strftime('%Y_%m_%d')}.pdf"
                }
            )
            
        except Exception as e:
            return jsonify({"error": str(e)})