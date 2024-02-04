from fpdf import FPDF
import logging
from collections import defaultdict
import os

class ReportGenerator(FPDF):
    def __init__(self, project_name):
        super().__init__()
        self.project_name = project_name
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'{self.project_name} - Repository Authorship Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    @staticmethod
    def generate_report(authorship_data, report_path, project_name):
        logging.info("Generating PDF report...")
        pdf = ReportGenerator(project_name)
        pdf.set_font("Arial", size=12)
        
        # Calculate summary information
        total_files = len(authorship_data)
        author_contributions = defaultdict(int)
        for author in authorship_data.values():
            author_contributions[author] += 1
        for author, count in author_contributions.items():
            author_contributions[author] = (count / total_files) * 100
        
        # Summary section
        pdf.cell(0, 10, f"Total Files Analyzed: {total_files}", ln=True)
        for author, percentage in author_contributions.items():
            pdf.cell(0, 10, f"Author: {author}, Contribution: {percentage:.2f}%", ln=True)
        
        pdf.cell(0, 10, "", ln=True)  # Add a space before listing files

        # Organize files by directory
        directory_mapping = defaultdict(lambda: defaultdict(list))
        for file_path, author in authorship_data.items():
            directory, file_name = os.path.split(file_path)
            directory_mapping[directory][author].append(file_name)
        
        # List files by directory
        for directory, authors_files in directory_mapping.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Directory: {directory if directory else 'Root'}", ln=True)
            pdf.set_font("Arial", size=12)
            for author, files in authors_files.items():
                for file_name in files:
                    pdf.cell(0, 10, f"    {file_name} - {author}", ln=True)
        
        pdf.output(report_path)
        logging.info(f"Report successfully generated at {report_path}")