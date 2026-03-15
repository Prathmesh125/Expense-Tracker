#!/usr/bin/env python3
"""
Database backup script for MySQL database
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handle database backup operations"""
    
    def __init__(self):
        """Initialize backup configuration"""
        self.backup_dir = Path(__file__).parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Get database credentials from environment
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '3306')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        self.db_name = os.getenv('DB_NAME', 'adms_expense')
    
    def create_backup(self):
        """Create a database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'backup_{self.db_name}_{timestamp}.sql'
        
        logger.info(f"Starting database backup to {backup_file}")
        
        try:
            # Construct mysqldump command
            cmd = [
                'mysqldump',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                self.db_name
            ]
            
            # Execute backup
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                # Get file size
                file_size = backup_file.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"Backup completed successfully: {backup_file.name} ({file_size:.2f} MB)")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                # Remove failed backup file
                if backup_file.exists():
                    backup_file.unlink()
                return False
                
        except FileNotFoundError:
            logger.error("mysqldump command not found. Please install MySQL client tools.")
            return False
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            if backup_file.exists():
                backup_file.unlink()
            return False
    
    def cleanup_old_backups(self, keep_count=7):
        """
        Remove old backup files, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep
        """
        logger.info(f"Cleaning up old backups, keeping {keep_count} most recent")
        
        try:
            # Get all backup files sorted by modification time
            backup_files = sorted(
                self.backup_dir.glob('backup_*.sql'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old backups
            removed_count = 0
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file.name}")
                removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} old backup(s)")
            else:
                logger.info("No old backups to remove")
                
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
    
    def list_backups(self):
        """List all available backups"""
        backups = sorted(
            self.backup_dir.glob('backup_*.sql'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not backups:
            logger.info("No backups found")
            return
        
        logger.info(f"Available backups ({len(backups)}):")
        for backup in backups:
            size_mb = backup.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            logger.info(f"  - {backup.name} ({size_mb:.2f} MB) - {mtime}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database backup utility')
    parser.add_argument(
        '--action',
        choices=['backup', 'cleanup', 'list'],
        default='backup',
        help='Action to perform'
    )
    parser.add_argument(
        '--keep',
        type=int,
        default=7,
        help='Number of backups to keep when cleaning up'
    )
    
    args = parser.parse_args()
    
    backup_manager = DatabaseBackup()
    
    if args.action == 'backup':
        success = backup_manager.create_backup()
        if success:
            backup_manager.cleanup_old_backups(args.keep)
    elif args.action == 'cleanup':
        backup_manager.cleanup_old_backups(args.keep)
    elif args.action == 'list':
        backup_manager.list_backups()

if __name__ == '__main__':
    main()
