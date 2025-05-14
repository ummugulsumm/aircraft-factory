import uuid
import datetime
import random
from typing import Optional


def generate_serial_number(prefix: str, aircraft_type: str, part_type: Optional[str] = None) -> str:

    now = datetime.datetime.now()
    
    date_str = now.strftime("%Y%m%d")
    
    random_number = random.randint(100, 999)
    
    uuid_part = str(uuid.uuid4()).split('-')[0]
    
    type_str = f"-{part_type}" if part_type else ""
    
    serial_number = f"{prefix}-{aircraft_type}{type_str}-{date_str}-{random_number}-{uuid_part}"
    
    return serial_number


def generate_aircraft_serial_number(aircraft_type: str) -> str:

    return generate_serial_number("AC", aircraft_type)


def generate_part_serial_number(part_type: str, aircraft_type: str) -> str:

    return generate_serial_number("PART", aircraft_type, part_type)