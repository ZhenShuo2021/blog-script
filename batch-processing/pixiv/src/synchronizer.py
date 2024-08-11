
# Todo: Logging if remote path exists.
import os
import subprocess
from datetime import datetime
from typing import Optional

class FileSyncer:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def sync_folders(self, source: str, destination: str):
        self._ensure_directory_exists(source)
        self._ensure_directory_exists(destination)

        log_file = self._get_log_file(source)
        self._run_rsync(source, destination, log_file)

    def _ensure_directory_exists(self, path: str):
        if not os.path.exists(path):
            print(f"警告：目標位置 '{path}' 不存在，已自動新建")
            os.makedirs(path)

    def _get_log_file(self, source: str) -> str:
        return os.path.join(self.log_dir, f'{os.path.basename(source)}.log')

    def _run_rsync(self, source: str, destination: str, log_file: str):
        command = [
            'rsync', '-aq', '--ignore-existing', '--remove-source-files', '--progress',
            f'--log-file={log_file}', f'{source}/', f'{destination}/'
        ]
        subprocess.run(command, check=True)

class LogMerger:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir

    def merge_logs(self):
        output_file = f"{self.log_dir}/rsync_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]

        if not log_files:
            print("No log files found in the directory.")
            return

        merged_content = self._merge_log_files(log_files)
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write(merged_content)
        print(f"All logs have been merged into {output_file}")

    def _merge_log_files(self, log_files: list) -> str:
        merged_content = ""
        for log_file in log_files:
            file_path = os.path.join(self.log_dir, log_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content += f"\n\n====================[{log_file}]====================\n\n{content}"
            os.remove(file_path)
        return merged_content

if __name__ == "__main__":
    from utils.file_utils import PathManager, ConfigLoader
    from src.logger import LogLevel, LogManager, logger
    log_manager = LogManager(level=LogLevel.DEBUG)
    logger = log_manager.get_logger()

    config_loader = ConfigLoader('data/config.toml')
    config_loader.load_config()
    tag_delimiters = config_loader.get_delimiters()

    path_manager = PathManager(config_loader)
    combined_paths = path_manager.get_combined_paths()
    
    log_dir = os.path.join(os.getcwd(), 'gen')
    file_syncer = FileSyncer(log_dir)

    for key in combined_paths:
        file_syncer.sync_folders(combined_paths[key]["local"], combined_paths[key]["remote"])

    log_merger = LogMerger(log_dir)
    log_merger.merge_logs()
