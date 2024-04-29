# thrift_management/management/commands/generate_thrift.py

import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate Python files from Thrift definition'

    def handle(self, *args, **options):
        thrift_file_path = 'webapps2024/utils/timestamp.thrift'
        out_dir = 'generated_code'

        # Ensure the output directory exists
        os.makedirs(out_dir, exist_ok=True)

        # Generate Python files
        os.system(f'thrift -r --gen py -out {out_dir} {thrift_file_path}')

        self.stdout.write(self.style.SUCCESS('Thrift files generated successfully!'))
