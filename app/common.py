import os
import pyodbc
import hashlib
import requests
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Depends, Header, status
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.data_type_validation.data_validate import Correct_Data
from bs4 import BeautifulSoup
from app.base_classes.base_classes import BaseModels
from typing import Optional
from datetime import datetime
from fastapi import APIRouter