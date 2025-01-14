import sqlite3
from pathlib import Path
from datetime import datetime
from ..config.generator_list import generators
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.current_db = self.data_dir / "equipment_check.db"
        self.connection = None
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        self.available_tables = []
        self.gen_names = [
            "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
            "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
            "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
            "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
        ]
        self.pre_columns = ["fuel_level", "battery_vdc", "run_hours", "coolant_temp", "leaks", "oil_check", "notes", "last_updated"]
        self.post_columns = ["fuel_level", "battery_vdc", "run_hours", "coolant_temp", "leaks", "notes", "last_updated"]
        self.init_db()

    def init_db(self):
        """Initialize SQLite database connection and tables."""
        self.connection = sqlite3.connect(self.current_db)
        cursor = self.connection.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        self.available_tables = [table[0] for table in cursor.fetchall()]
        
        if not self.available_tables:
            for month in self.months:
                for generator in generators:
                    gen_safe = generator.replace('-', '_').lower()
                    
                    # Create pre-run table
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_pre (
                        fuel_level INTEGER,
                        battery_vdc REAL,
                        run_hours TEXT,
                        coolant_temp TEXT,
                        leaks BOOLEAN,
                        oil_check BOOLEAN,
                        notes TEXT,
                        last_updated DATE
                    )""")
                    
                    # Create post-run table
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_post (
                        fuel_level INTEGER,
                        battery_vdc REAL,
                        run_hours TEXT,
                        coolant_temp TEXT,
                        leaks BOOLEAN,
                        notes TEXT,
                        last_updated DATE
                    )""")
                    
                    # Insert initial empty row for each table
                    cursor.execute(f"""
                    INSERT INTO {month}_{gen_safe}_pre 
                    (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, oil_check, notes, last_updated)
                    VALUES (0, 0.0, '0:0', '', 0, 0, '', CURRENT_DATE)
                    """)
                    
                    cursor.execute(f"""
                    INSERT INTO {month}_{gen_safe}_post
                    (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, notes, last_updated)
                    VALUES (0, 0.0, '0:0', '', 0, '', CURRENT_DATE)
                    """)
            
            self.connection.commit()
            
            # Update available tables list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            self.available_tables = [table[0] for table in cursor.fetchall()]


    def save_check_data(self, generator: str, pre_data: dict, post_data: dict):
        """Save pre and post run check data to database."""
        cursor = self.connection.cursor()
        gen_safe = generator.replace('-', '_').lower()
        current_month = datetime.now().strftime("%B").lower()
        # Update pre-run data
        pre_values = (
            int(pre_data.get('fuel_level', 0)),
            float(pre_data.get('battery_vdc', 0.0)),
            pre_data.get('run_hours', '0:0'),
            pre_data.get('coolant_temp', ''),
            bool(pre_data.get('leaks', False)),
            bool(pre_data.get('oil_check', False)),
            pre_data.get('notes', '')
        )
        
        cursor.execute(f"""
        UPDATE {current_month}_{gen_safe}_pre 
        SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
            oil_check=?, notes=?, last_updated=CURRENT_DATE
        """, pre_values)
        
        # Update post-run data
        post_values = (
            int(post_data.get('fuel_level', 0)),
            float(post_data.get('battery_vdc', 0.0)),
            post_data.get('run_hours', '0:0'),
            post_data.get('coolant_temp', ''),
            bool(post_data.get('leaks', False)),
            post_data.get('notes', '')
        )
        
        cursor.execute(f"""
        UPDATE {current_month}_{gen_safe}_post 
        SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
            notes=?, last_updated=CURRENT_DATE
        """, post_values)
        
        self.connection.commit()

    def get_entries(self, month: str, generator: str):
        """Retrieve entries for a specific month and generator."""
        cursor = self.connection.cursor()
        gen_safe = generator.replace('-', '_').lower()
        
        # Get pre-run entries
        pre_table = f"{month}_{gen_safe}_pre"
        cursor.execute(f"SELECT * FROM {pre_table}")
        pre_entries = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({pre_table})")
        pre_columns = [col[1] for col in cursor.fetchall()]
        
        # Get post-run entries
        post_table = f"{month}_{gen_safe}_post"
        cursor.execute(f"SELECT * FROM {post_table}")
        post_entries = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({post_table})")
        post_columns = [col[1] for col in cursor.fetchall()]
        
        return {
            'pre': {'columns': pre_columns, 'entries': pre_entries},
            'post': {'columns': post_columns, 'entries': post_entries}
        }
    
    def gen_records_month(self, month: str):
        """Return generators if they have records for the month"""
        generators = set() 
        cursor = self.connection.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Filter tables that start with the given month
        for table in tables:
            table_name = table[0]
            if table_name.startswith(month.lower()):
                # Extract generator name from table name (format: month_gen_x_pre/post) if the fields are not default values
                cursor.execute(f"SELECT * FROM {table_name}")   
                records = cursor.fetchall()
                for record in records:
                    # default values are (0, 0.0, '0:0', '', 0, 0, '', '2024-12-28') only check post records, the fourth field is not checked
                    if record[0:3] != (0, 0.0, '0:0') and table_name.endswith('_post'):
                        gen_name = table_name.split('_')[1:]
                        # put the - back in
                        gen_name = '-'.join(gen_name[:-1])
                        # all caps
                        gen_name = gen_name.upper()
                        generators.add(gen_name)
                
        return list(generators)
    
    def get_gen_data(self, month: str, generator: str):
        """Return the data for a specific generator and month"""
        cursor = self.connection.cursor()
        
        # Get pre-run data
        try:    
            pre_table = f"{month}_{generator.replace('-', '_').lower()}_pre"
            cursor.execute(f"SELECT * FROM {pre_table}")
            pre_records = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({pre_table})")
            pre_columns = [col[1] for col in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print(f"Error getting pre-run data: {e}")
            return None
        
        # Get post-run data  
        try:
            post_table = f"{month}_{generator.replace('-', '_').lower()}_post"
            cursor.execute(f"SELECT * FROM {post_table}")
            post_records = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({post_table})")
            post_columns = [col[1] for col in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print(f"Error getting post-run data: {e}")
            return None

        # Create list of dictionaries with proper column names
        pre_data = {}
        post_data = {}
        
        for record in pre_records:
            pre_data[pre_columns[0]] = record[0]
            pre_data[pre_columns[1]] = record[1]
            pre_data[pre_columns[2]] = record[2]
            pre_data[pre_columns[3]] = record[3]
            pre_data[pre_columns[4]] = record[4]
            pre_data[pre_columns[5]] = record[5]
            pre_data[pre_columns[6]] = record[6]
            
        for record in post_records:
            post_data[post_columns[0]] = record[0]
            post_data[post_columns[1]] = record[1]
            post_data[post_columns[2]] = record[2]
            post_data[post_columns[3]] = record[3]
            post_data[post_columns[4]] = record[4]
            post_data[post_columns[5]] = record[5]
            post_data[post_columns[6]] = record[6]
            

        return {
            'pre': pre_data,
            'post': post_data
        }
    
    def all_gen_data(self, month: str, completed_only: bool = False):
        """Return the data for all generators and month"""
        cursor = self.connection.cursor()
        generators = [
            "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
            "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
            "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
            "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
        ]
        data = {}
        if completed_only:
            generators = self.gen_records_month(month)
        for generator in generators:        
            # Get pre-run data
            pre_table = f"{month}_{generator.replace('-', '_').lower()}_pre"
            cursor.execute(f"SELECT * FROM {pre_table}")
            pre_record = cursor.fetchone()
            cursor.execute(f"PRAGMA table_info({pre_table})")
            pre_columns = [col[1] for col in cursor.fetchall()]
        
            # Get post-run data  
            post_table = f"{month}_{generator.replace('-', '_').lower()}_post"
            cursor.execute(f"SELECT * FROM {post_table}")
            post_record = cursor.fetchone()
            cursor.execute(f"PRAGMA table_info({post_table})")
            post_columns = [col[1] for col in cursor.fetchall()]
            data[generator] = {
                'pre': pre_record,
                'post': post_record
            }


        return data



    def __del__(self):
        """Ensure database connection is closed."""
        if self.connection:
            self.connection.close()