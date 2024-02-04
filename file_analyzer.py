import difflib
import logging

class FileAnalyzer:
    THRESHOLD = 0.6

    @staticmethod
    def calculate_similarity(old_content, new_content):
        if not old_content or not new_content:
            logging.info("One of the file contents is None, skipping similarity calculation.")
            return 0
        ratio = difflib.SequenceMatcher(None, old_content, new_content).ratio()
        logging.debug(f"Calculated similarity ratio: {ratio}")
        return ratio

    @staticmethod
    def analyze_file_authorship(file_commits, file_contents):
        attributed_author = file_commits[0].author.name
        if len(file_commits) == 1:
            # If there's exactly one commit, attribute the file to its author
            logging.info(f"Single commit found, attributing to: {file_commits[0].author.name}")
            return attributed_author
          
        significant_change_detected = False

        for i in range(len(file_contents)-1):
            old_content = file_contents[i]
            new_content = file_contents[i+1]
            if old_content is None or new_content is None:
                continue
            similarity = FileAnalyzer.calculate_similarity(old_content, new_content)
            if similarity < FileAnalyzer.THRESHOLD:
                attributed_author =file_commits[i+1].author.name
                significant_change_detected = True
                logging.info(f"Significant change detected, attributing to author of newer commit: {attributed_author}")
        
        if not significant_change_detected:      
            logging.info("No significant change detected, attributing to the initial author.")
        return file_commits[-1].author.name