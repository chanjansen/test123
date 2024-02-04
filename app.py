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





# from flask import Flask, request, send_from_directory, render_template
# import logging
# import os
# from datetime import datetime
# from fpdf import FPDF
# from git import Repo
# import difflib
# import fnmatch

# app = Flask(__name__)
# logging.basicConfig(level=logging.INFO)
# # Directory to save PDF reports
# REPORT_FOLDER = 'pdf_reports'
# os.makedirs(REPORT_FOLDER, exist_ok=True)

# class PDF(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 12)
#         self.cell(0, 10, 'Repository Authorship Report', 0, 1, 'C')

#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


# class CommitComparer:
#     def __init__(self, repo_url):
#         app.logger.info(f"Initializing repository analysis for {repo_url}")
#         self.repo_analyzer = RepositoryAnalyzer(repo_url)
#         self.repo = self.repo_analyzer.repo
#         self.THRESHOLD = 0.6
#         self.SKIP_PATTERNS = ['*package.json', '*package-lock.json', '*node_modules/*', '*.lock', '*.pptx', '*.docx', '*.pdf', '*.jpg', '*.png', '*.gif', '*.exe', '*.dll', '*.json']
        
#     def file_should_be_skipped(self, file_path):
#       skipped = any(fnmatch.fnmatch(file_path, pattern) for pattern in self.SKIP_PATTERNS)
#       if skipped:
#             app.logger.info(f"Skipping file: {file_path}")
#       return skipped
    
#     def calculate_similarity(self, old_content, new_content):
#         ratio = difflib.SequenceMatcher(None, old_content, new_content).ratio()
#         app.logger.info(f"Similarity ratio: {ratio}")
#         return ratio

#     def compare_commits_for_file(self, file_path):
#         app.logger.info(f"Analyzing file: {file_path}")
#         if self.file_should_be_skipped(file_path):
#             app.logger.info(f"Skipping file based on pattern: {file_path}")
#             return None
          
#         commits = list(self.repo.iter_commits(paths=file_path, reverse=True))
#         if not commits:
#             app.logger.info(f"No commits found for file: {file_path}")
#             return None

#         for i in range(len(commits)-1):
#             old_commit = commits[i]
#             new_commit = commits[i+1]
#             old_file_content = self.get_file_content_at_commit(file_path, old_commit)
#             new_file_content = self.get_file_content_at_commit(file_path, new_commit)

#             similarity = self.calculate_similarity(old_file_content, new_file_content)
#             app.logger.info(f"Comparing {old_commit.hexsha} to {new_commit.hexsha} for file {file_path}, similarity: {similarity}")
#             if similarity < self.THRESHOLD:
#                 app.logger.info(f"Significant change detected in {file_path}. Attributing to author of commit {new_commit.hexsha}")
#                 return new_commit.author.name
#         app.logger.info(f"No significant change detected in {file_path}. Attributing to the initial author.")
#         return commits[-1].author.name

#     def get_file_content_at_commit(self, file_path, commit):
#         try:
#             blob = commit.tree / file_path
#             return blob.data_stream.read().decode('utf-8')
#         except (KeyError, UnicodeDecodeError):
#             return None

#     def analyze_repository(self):
#         app.logger.info("Starting repository analysis")
#         file_authorship = {}
#         for file_path in self.repo_analyzer.get_all_files():
#             app.logger.info(f"Starting analysis for file: {file_path}")
#             author = self.compare_commits_for_file(file_path)
#             if author:
#                 file_authorship[file_path] = author
#                 app.logger.info(f"File: {file_path}, Author: {author}")
#         app.logger.info("Repository analysis completed")
#         return file_authorship

# def generate_pdf_report(authorship_data, report_path):
#     pdf = PDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     line_height = pdf.font_size * 1.5
#     for file_path, author in authorship_data.items():
#         pdf.cell(0, line_height, f"File: {file_path}, Author: {author}", ln=True)
#     pdf.output(report_path)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         repo_url = request.form.get('repositoryURL')
#         app.logger.info(f"Received repository URL for analysis: {repo_url}")
#         comparer = CommitComparer(repo_url)
#         repository_authorship = comparer.analyze_repository()

#         # Generate a PDF report
#         project_name = repo_url.split('/')[-1].replace('.git', '')
#         current_date = datetime.now().strftime("%Y-%m-%d")
#         report_filename = f"{project_name}_authorship_report_{current_date}.pdf"
#         report_path = os.path.join(REPORT_FOLDER, report_filename)
        
#         generate_pdf_report(repository_authorship, report_path)

#         # Provide the PDF report for download
#         return send_from_directory(directory=REPORT_FOLDER, path=report_filename, as_attachment=True)
    
#     return render_template('index.html')