import pytest
from .client_base import Client

class GroundStation(Client):
    
    def __init__(self):
        super().__init__()