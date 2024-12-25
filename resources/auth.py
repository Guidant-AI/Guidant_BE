from fastapi import APIRouter, Request
from pymongo import MongoClient
from models.user import User
from passlib.hash import bcrypt
from pydantic import BaseModel
from utils.sendOtp import generate_otp, validate_otp,send_otp_email
import pyotp
from utils.jwtHandler import create_access_token, decode_access_token

client = MongoClient("mongodb://admin:alwen123@127.0.0.1:27017/?authSource=admin")
db = client["app"]
user_collection = db["users"]
class LoginRequest(BaseModel):
    email: str
    password: str
    otp: str
class LogoutRequest(BaseModel):
    token: str

class SendOtpRequest(BaseModel):
    email: str
    password: str

router = APIRouter()

otp_secrets = {}

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)
@router.post("/signup")
async def signup(user: User):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        existing_user = user_collection.find_one({"email": user.email})
        if existing_user:
            response.update({"status": 400, "message": "failure", "error": "Email already registered"})
            return response
        
        user.password = hash_password(user.password)
        
        user_data = user.dict()
        user_collection.insert_one(user_data)
        
        response["data"] = {"message": "User registered successfully. "}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response

@router.post("/login")
async def login(login_request: LoginRequest):
    response = {"status": 200, "message": "success", "data": {}, "error": ""}
    try:
        user = user_collection.find_one({"email": login_request.email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return response
        
        if not verify_password(login_request.password, user["password"]):
            response.update({"status": 401, "message": "failure", "error": "Invalid password"})
            return response
        
        otp_secret = user.get("otp_secret")
        print(otp_secret)
        if not otp_secret:
            response.update({"status": 400, "message": "failure", "error": "OTP not set"})
            return response

        if not validate_otp(otp_secret, login_request.otp):
            response.update({"status": 401, "message": "failure", "error": "Invalid OTP"})
            return response
        
        token = create_access_token({"email": login_request.email})
        user_collection.update_one({"email": login_request.email}, {"$unset": {"otp": ""}})
        
        response["data"] = {"message": "Login successful", "token": token}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response




@router.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        user = user_collection.find_one({"email": request.email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return response
        
        # Verify the password
        if not verify_password(request.password, user["password"]):
            response.update({"status": 401, "message": "failure", "error": "Invalid password"})
            return response
        
        # Generate OTP secret if not exists
        otp_secret = user.get("otp_secret")
        if not otp_secret:
            otp_secret = pyotp.random_base32()
            user_collection.update_one({"email": request.email}, {"$set": {"otp_secret": otp_secret}})
        
        # Generate OTP and update in database
        otp = generate_otp(otp_secret)
        user_collection.update_one({"email": request.email}, {"$set": {"otp": otp}})
        
        # Send OTP to the email
        email_response = send_otp_email(request.email, otp)
        if email_response["status"] == "failure":
            response.update({"status": 500, "message": "failure", "error": email_response["message"]})
            return response
        
        response["data"] = {"message": "OTP sent to email", "otp": otp}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response



@router.delete("/delete-user")
async def delete_user(email: str):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        result = user_collection.delete_one({"email": email})
        if result.deleted_count == 0:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return response
        response["data"] = {"message": f"User {email} deleted successfully"}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response


@router.post("/logged-in-user") 
async def logged_in_user(token: str):
    response = {"status": 200, "message": "success", "data": {}, "error": ""}
    try:
        payload = decode_access_token(token)
        email = payload.get("email")
        user = user_collection.find_one({"email": email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return response
        response["data"] = {"email": user["email"]}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response


@router.get("/logout")
async def logout(token: str):
    response = {"status": 200, "message": "success", "data": {}, "error": ""}
    try:
        payload = decode_access_token(token)
        email = payload.get("email")
        user = user_collection.find_one({"email": email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return response
        response["data"] = {"message": "Logout successful"}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
    return response
