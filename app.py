from flask import Flask, request, send_from_directory, render_template
import logging
import os
from datetime import datetime
from repo_manager import RepositoryManager
from file_filter import FileFilter
from file_analyzer import FileAnalyzer
from report_generator import ReportGenerator

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
REPORT_FOLDER = 'pdf_reports'
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo_url = request.form.get('repositoryURL')
        app.logger.info(f"Received repository URL for analysis: {repo_url}")
        project_name = repo_url.split('/')[-1].replace('.git', '')
        # Initialize RepositoryManager and clone repo if necessary
        repo_manager = RepositoryManager(repo_url)
        all_files = repo_manager.get_all_files()

        authorship_data = {}
        for file_path in all_files:
            if FileFilter.should_skip(file_path):
                app.logger.info(f"Skipping file: {file_path}")
                continue

            file_commits = repo_manager.get_file_commits(file_path)
            file_contents = []
            for commit in file_commits:
                content = repo_manager.get_file_content_at_commit(file_path, commit)
                if content is None:
                    app.logger.info(f"Skipping analysis for {file_path} due to failed content retrieval at some commit.")
                    break  # Skip this file entirely if any content retrieval fails
                file_contents.append(content)

            if not file_contents:  # If file_contents is empty, skip this file
                continue

            author = FileAnalyzer.analyze_file_authorship(file_commits, file_contents)
            authorship_data[file_path] = author

        # Generate and save the PDF report
        report_filename = f"{project_name}_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        report_path = os.path.join(REPORT_FOLDER,  report_filename)
        
        ReportGenerator.generate_report(authorship_data, report_path, project_name)

        return send_from_directory(REPORT_FOLDER, os.path.basename(report_path), as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

