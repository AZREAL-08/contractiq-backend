from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
from services.extract_service import extract_data
from services.gemini_service import gemini_call
from services.firebase_service import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            flash('No files selected.', 'error')
            return redirect(request.url)

        extracted_contents = []
        for file in files:
            try:
                # Extract text/content using our extract_service
                content = extract_data(file, file.filename)
                # Append user_id to filename to prevent conflicts
                filename = f"{user_id}_{file.filename}"
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                extracted_contents.append(content)
            except Exception as e:
                flash(f"Error processing {file.filename}: {str(e)}", 'error')

        if not extracted_contents:
            flash('No valid files to process.', 'error')
            return redirect(request.url)

        # Process extracted content using Gemini AI call
        data = gemini_call(extracted_contents)
        # Save processed data to Firestore under user's documents subcollection
        collection_path = f'users/{user_id}/documents'
        db.collection(collection_path).add(data)
        flash("File(s) processed and data saved successfully.", "success")
        return redirect(url_for('dashboard.dashboard'))

    # GET request: Fetch already uploaded documents for the logged-in user
    collection_path = f'users/{session.get("user_id")}/documents'
    documents = db.collection(collection_path).stream()
    files_data = [doc.to_dict() for doc in documents]

    return render_template('dashboard.html', files_data=files_data)
