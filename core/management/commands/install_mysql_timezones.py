from django.core.management.base import BaseCommand
from django.db import connection
import subprocess
import os

class Command(BaseCommand):
    help = 'Install MySQL timezone data to fix datetime issues'

    def handle(self, *args, **options):
        try:
            # Try to install MySQL timezone data
            self.stdout.write('Attempting to install MySQL timezone data...')
            
            # Get database configuration
            db_settings = connection.settings_dict
            host = db_settings.get('HOST', 'localhost')
            port = db_settings.get('PORT', '3306')
            user = db_settings.get('USER')
            password = db_settings.get('PASSWORD')
            
            # Try to run mysql_tzinfo_to_sql command
            try:
                # This command needs to be run on the server where MySQL is installed
                # It's typically available in the MySQL installation directory
                cmd = ['mysql_tzinfo_to_sql', '/usr/share/zoneinfo']
                
                if user:
                    cmd.extend(['-u', user])
                if password:
                    cmd.extend(['-p' + password])
                if host and host != 'localhost':
                    cmd.extend(['-h', host])
                if port and port != '3306':
                    cmd.extend(['-P', str(port)])
                
                cmd.append('mysql')
                
                # Run the command
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.stdout.write(
                        self.style.SUCCESS('Successfully installed MySQL timezone data')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Could not install MySQL timezone data automatically: %s' % result.stderr)
                    )
                    self.stdout.write(
                        'Please manually install MySQL timezone data using the mysql_tzinfo_to_sql command'
                    )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.WARNING('mysql_tzinfo_to_sql command not found')
                )
                self.stdout.write(
                    'Please install MySQL timezone data manually by running:'
                )
                self.stdout.write(
                    'mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql'
                )
            
            # Test if timezone data is available
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM mysql.time_zone_name")
                count = cursor.fetchone()[0]
                if count > 0:
                    self.stdout.write(
                        self.style.SUCCESS('MySQL timezone data is available (%d timezones)' % count)
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('MySQL timezone data is not available')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR('Error installing MySQL timezone data: %s' % str(e))
            )
            self.stdout.write(
                'Please ensure MySQL timezone data is properly installed on your server'
            )