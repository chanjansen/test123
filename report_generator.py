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
        self.set_font('Times', 'B', 16)
        self.cell(0, 10, f'{self.project_name} - Detailed Code Contribution Analysis', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    @staticmethod
    def generate_report(authorship_data, report_path, project_name):
        logging.info("Generating PDF report...")
        pdf = ReportGenerator(project_name)
        
        total_files = len(authorship_data)
        author_contributions = defaultdict(int)
        for author in authorship_data.values():
            author_contributions[author] += 1

        # Summary of Contributions
        pdf.set_font("Times", 'B', 12)
        pdf.cell(0, 10, "Summary of Contributions", ln=True)
        pdf.set_font("Times", size=10)
        pdf.cell(0, 10, f"Total Files Analyzed: {total_files}", ln=True)

        # Uniform Styling for Author Contributions
        for author, count in author_contributions.items():
            percentage = (count / total_files) * 100
            pdf.cell(0, 10, f"{author}: {percentage:.2f}%", ln=True)

        # Directory and File Listings
        directory_mapping = defaultdict(lambda: defaultdict(list))
        for file_path, author in authorship_data.items():
            directory, file_name = os.path.split(file_path)
            directory_mapping[directory][author].append(file_name)

        for directory, authors_files in directory_mapping.items():
            pdf.set_font('Times', 'B', 12)
            pdf.cell(0, 10, f"Directory: {directory if directory else 'Root'}", ln=True)
            pdf.set_font("Times", size=10)

            for author, files in authors_files.items():
                for file_name in files:
                    pdf.cell(0, 10, f"    {file_name} - {author}", ln=True)

        pdf.output(report_path)
        logging.info(f"Report successfully generated at {report_path}")