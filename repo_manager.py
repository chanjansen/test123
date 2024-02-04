from git import Repo
import os
import logging

class RepositoryManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        logging.info(f"Initializing repository management for {repo_url}")
        self.local_repo_path = self.clone_repo()
        self.repo = Repo(self.local_repo_path)

    def clone_repo(self):
        repo_name = self.repo_url.split('/')[-1].replace('.git', '')
        local_repo_path = os.path.join(os.getcwd(), repo_name)
        if not os.path.exists(local_repo_path):
            logging.info(f"Cloning repository from {self.repo_url} into {local_repo_path}")
            Repo.clone_from(self.repo_url, local_repo_path)
        else:
            logging.info(f"Using existing repository at {local_repo_path}")
        return local_repo_path

    def get_all_files(self):
        logging.info("Retrieving all files currently tracked by Git")
        return [item.path for item in self.repo.tree().traverse() if item.type == 'blob']

    def get_file_commits(self, file_path):
        logging.info(f"Getting commit history for file: {file_path}")
        return list(self.repo.iter_commits(paths=file_path))

    def get_file_content_at_commit(self, file_path, commit):
        try:
            blob = commit.tree / file_path
            return blob.data_stream.read().decode('utf-8')
        except Exception as e:
            logging.error(f"Failed to retrieve content for {file_path} at commit {commit.hexsha}: {e}")
            return None