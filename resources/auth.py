from fastapi import APIRouter, Request
from pymongo import MongoClient
from models.user import User
from passlib.hash import bcrypt
from pydantic import BaseModel
from utils.sendOtp import send_otp_email
import pyotp
from fastapi.responses import JSONResponse
from utils.jwtHandler import create_access_token, decode_access_token
import random

client = MongoClient("mongodb+srv://Arvind:Arvind@guidantai.dptv6.mongodb.net/")
db = client["Guidant"]
user_collection = db["User_details"]
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
        # Check if the user exists in the database
        user = user_collection.find_one({"email": login_request.email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return JSONResponse(content=response, status_code=404)

        if not verify_password(login_request.password, user["password"]):
            response.update({"status": 401, "message": "failure", "error": "Invalid password"})
            return JSONResponse(content=response, status_code=401)

        otp_record = db["otp_collection"].find_one({"email": login_request.email})
        if not otp_record:
            response.update({"status": 400, "message": "failure", "error": "OTP not generated or expired"})
            return JSONResponse(content=response, status_code=400)

        if str(otp_record["otp"]) != login_request.otp:
            response.update({"status": 401, "message": "failure", "error": "Invalid OTP"})
            return JSONResponse(content=response, status_code=401)

        token = create_access_token({"email": login_request.email})

        db["otp_collection"].delete_one({"email": login_request.email})

        response["data"] = {"message": "Login successful", "token": token}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return JSONResponse(content=response, status_code=500)

    return JSONResponse(content=response, status_code=200)

@router.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    response = {"status": 200, "message": "success", "data": {}, "error": ""}
    try:
        user = user_collection.find_one({"email": request.email})
        if not user:
            response.update({"status": 404, "message": "failure", "error": "User not found"})
            return JSONResponse(content=response, status_code=404)

        # Generate a random 6-digit OTP
        otp= random.randint(100000, 999999)
        # Update or insert the OTP into the database
        existing_otp = db["otp_collection"].find_one({"email": request.email})
        if existing_otp:
            db["otp_collection"].update_one({"email": request.email}, {"$set": {"otp": otp}})
        else:
            db["otp_collection"].insert_one({"email": request.email, "otp": otp})

        # Send the OTP to the user
        message = f"Your OTP for login is {otp}. Please use it within 5 minutes."
        send_otp_email(request.email, message)

        # Return success response with the OTP (for testing purposes, remove in production)
        response["data"] = {"message": "OTP sent successfully", "otp": otp}
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return JSONResponse(content=response, status_code=500)

    return JSONResponse(content=response)



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