#!/usr/bin/env python3
"""
سكريبت للمراقبة التلقائية للملفات ودفع التغييرات إلى GitHub و Odoo.sh
"""

import os
import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto-push.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class GitAutoCommitHandler(FileSystemEventHandler):
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.last_commit_time = time.time()
        self.commit_delay = 30  # انتظار 30 ثانية قبل الـ commit
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # تجاهل ملفات معينة
        ignored_extensions = ['.pyc', '.log', '.tmp', '.swp']
        ignored_dirs = ['.git', '__pycache__', '.vscode', 'node_modules']
        
        file_path = event.src_path
        
        # تحقق من الملفات المتجاهلة
        if any(file_path.endswith(ext) for ext in ignored_extensions):
            return
            
        if any(ignored_dir in file_path for ignored_dir in ignored_dirs):
            return
            
        logging.info(f"تم تعديل الملف: {file_path}")
        
        # انتظار قبل الـ commit لتجميع التغييرات
        current_time = time.time()
        if current_time - self.last_commit_time > self.commit_delay:
            self.auto_commit_and_push()
            self.last_commit_time = current_time
    
    def auto_commit_and_push(self):
        try:
            os.chdir(self.repo_path)
            
            # التحقق من وجود تغييرات
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                logging.info("لا توجد تغييرات للـ commit")
                return
            
            # إضافة جميع التغييرات
            subprocess.run(['git', 'add', '.'], check=True)
            
            # إنشاء commit
            commit_message = f"تحديث تلقائي - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # دفع إلى GitHub
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            logging.info("✅ تم دفع التغييرات إلى GitHub بنجاح")
            
            # دفع إلى Odoo.sh إذا كان مُعداً
            try:
                subprocess.run(['git', 'push', 'odoo', 'main'], check=True)
                logging.info("✅ تم دفع التغييرات إلى Odoo.sh بنجاح")
            except subprocess.CalledProcessError:
                logging.warning("⚠️ لم يتم العثور على remote للـ Odoo.sh")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ خطأ في العملية: {e}")
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع: {e}")

def main():
    repo_path = os.getcwd()
    
    # التحقق من وجود Git repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        logging.error("❌ هذا المجلد ليس Git repository")
        sys.exit(1)
    
    logging.info(f"🚀 بدء مراقبة المجلد: {repo_path}")
    
    event_handler = GitAutoCommitHandler(repo_path)
    observer = Observer()
    observer.schedule(event_handler, repo_path, recursive=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("🛑 إيقاف المراقبة...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()