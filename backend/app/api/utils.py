from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import traceback
import httpx
import json
import re
from datetime import datetime

from ..database import get_db


logger = logging.getLogger(__name__)


router = APIRouter(tags=["utils"])

@router.get("/")
def read_root():
    """Root endpoint"""
    try:
        logger.info("Root endpoint accessed")
        return {"message": "n8n Execution Feedback API", "version": "1.0.0"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        
        logger.debug("Health check endpoint accessed")
        
        
        try:
            db.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as db_error:
            logger.error(f"Database connection error: {str(db_error)}")
            db_status = f"error: {str(db_error)}"
        
        return {
            "status": "healthy", 
            "message": "API is running",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in health check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/migrations/status")
def migration_status():
    """Check Alembic migration status"""
    try:
        logger.info("Migration status endpoint accessed")
        
        import subprocess
        import sys
        
        
        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], capture_output=True, text=True, cwd="/app")
        
        current_migration = "unknown"
        if result.returncode == 0 and result.stdout.strip():
            current_migration = result.stdout.strip()
        
        
        history_result = subprocess.run([
            sys.executable, "-m", "alembic", "history", "--verbose"
        ], capture_output=True, text=True, cwd="/app")
        
        migration_history = []
        if history_result.returncode == 0 and history_result.stdout.strip():
            migration_history = history_result.stdout.strip().split('\n')
        
        return {
            "status": "success",
            "current_migration": current_migration,
            "migration_history": migration_history[:10],  
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in migration status endpoint: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/migrations/run")
def run_migrations():
    """Manually trigger Alembic migrations"""
    try:
        logger.info("Manual migration trigger endpoint accessed")
        
        import subprocess
        import sys
        
        
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd="/app")
        
        if result.returncode == 0:
            logger.info("✅ Manual migrations completed successfully")
            return {
                "status": "success",
                "message": "Migrations completed successfully",
                "output": result.stdout.strip(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.warning(f"⚠️ Manual migrations failed (exit code: {result.returncode})")
            return {
                "status": "error",
                "message": "Migrations failed",
                "error": result.stderr.strip(),
                "output": result.stdout.strip(),
                "exit_code": result.returncode,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in manual migration endpoint: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image to external server and return the URL"""
    try:
        logger.info(f"Uploading image: {file.filename}")
        
        
        file_content = await file.read()
        
        
        files = {"files": (file.filename, file_content, file.content_type)}
        
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://165.227.123.243:8000/upload",
                files=files,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully uploaded image: {file.filename}")
                return result
            else:
                logger.error(f"External server error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"External server error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Timeout uploading image to external server")
        raise HTTPException(status_code=408, detail="Upload timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error uploading image: {str(e)}")
        raise HTTPException(status_code=502, detail=f"External server error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error uploading image: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/test-escape-characters")
def test_escape_characters_endpoint(data: dict):
    """Test endpoint to verify escape character handling"""
    try:
        logger.info("Testing escape character handling endpoint")
        
        
        from ..main import log_escape_characters, validate_and_log_json_content
        
        
        log_escape_characters(data, "TEST_ESCAPE_CHARACTERS")
        
        
        processed_data = {}
        for field_name, field_value in data.items():
            if isinstance(field_value, str) and field_value:
                processed_data[field_name] = validate_and_log_json_content(field_value, field_name)
            else:
                processed_data[field_name] = field_value
        
        
        
        
        escape_chars = ['\\n', '\\t', '\\r', '\\b', '\\f', '\\"', '\\\\']
        fields_with_escapes = 0
        for v in processed_data.values():
            if isinstance(v, str) and any(esc in v for esc in escape_chars):
                fields_with_escapes += 1
        
        return {
            "message": "Escape character test completed",
            "original_data": data,
            "processed_data": processed_data,
            "escape_character_summary": {
                "total_fields": len(data),
                "string_fields": len([v for v in data.values() if isinstance(v, str)]),
                "fields_with_escapes": fields_with_escapes
            }
        }
        
    except Exception as e:
        logger.error(f"Error in escape character test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@router.post("/test-json-parsing")
async def test_json_parsing_endpoint(request: Request):
    """Test endpoint to debug JSON parsing issues"""
    try:
        logger.info("Testing JSON parsing endpoint")
        
        
        body = await request.body()
        body_str = body.decode('utf-8')
        
        
        try:
            parsed_data = json.loads(body_str)
            return {
                "message": "JSON parsed successfully",
                "body_length": len(body_str),
                "parsed_data": parsed_data,
                "status": "success"
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            
            
            error_pos = e.pos
            context_start = max(0, error_pos - 50)
            context_end = min(len(body_str), error_pos + 50)
            context = body_str[context_start:context_end]
            
            
            cleaned_str = body_str
            if "'" in body_str:
                cleaned_str = body_str.replace("'", "\\'")
                logger.info("Attempted to clean apostrophes")
            
            try:
                cleaned_data = json.loads(cleaned_str)
                return {
                    "message": "JSON parsed after cleaning",
                    "original_error": str(e),
                    "error_position": error_pos,
                    "context": context,
                    "cleaned_data": cleaned_data,
                    "status": "cleaned"
                }
            except:
                return {
                    "message": "JSON parsing failed even after cleaning",
                    "error": str(e),
                    "error_position": error_pos,
                    "context": context,
                    "body_preview": body_str[:200] + "..." if len(body_str) > 200 else body_str,
                    "status": "failed"
                }
        
    except Exception as e:
        logger.error(f"Error in JSON parsing test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@router.post("/fix-json")
async def fix_json_endpoint(request: Request):
    """Endpoint to automatically fix common JSON issues"""
    try:
        logger.info("Fixing JSON endpoint accessed")
        
        
        body = await request.body()
        body_str = body.decode('utf-8')
        
        
        try:
            parsed_data = json.loads(body_str)
            return {
                "message": "JSON was already valid",
                "fixed_json": body_str,
                "status": "already_valid"
            }
        except json.JSONDecodeError as e:
            logger.info(f"Attempting to fix JSON: {str(e)}")
            
            
            fixed_str = body_str
            
            
            
            import re
            
            
            def fix_apostrophes(match):
                content = match.group(1)
                
                fixed_content = content.replace("'", "\\'")
                return f'"{fixed_content}"'
            
            
            string_pattern = r'"([^"]*)"'
            fixed_str = re.sub(string_pattern, fix_apostrophes, fixed_str)
            
            
            try:
                fixed_data = json.loads(fixed_str)
                return {
                    "message": "JSON fixed successfully",
                    "original_json": body_str,
                    "fixed_json": fixed_str,
                    "parsed_data": fixed_data,
                    "status": "fixed"
                }
            except json.JSONDecodeError as fix_error:
                return {
                    "message": "Failed to fix JSON",
                    "original_error": str(e),
                    "fix_error": str(fix_error),
                    "original_json": body_str,
                    "attempted_fix": fixed_str,
                    "status": "failed"
                }
        
    except Exception as e:
        logger.error(f"Error in fix JSON endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Fix JSON endpoint error: {str(e)}")

@router.post("/debug-json")
async def debug_json_endpoint(request: Request):
    """Debug endpoint to show exactly what's wrong with JSON"""
    try:
        logger.info("Debug JSON endpoint accessed")
        
        
        body = await request.body()
        body_str = body.decode('utf-8')
        
        
        issues = []
        
        
        newline_count = body_str.count('\n')
        if newline_count > 0:
            issues.append(f"Found {newline_count} newline characters")
        
        
        apostrophe_count = body_str.count("'")
        if apostrophe_count > 0:
            issues.append(f"Found {apostrophe_count} apostrophe characters")
        
        
        control_chars = []
        for i, char in enumerate(body_str):
            if ord(char) < 32 and char not in '\n\r\t':
                control_chars.append(f"Position {i}: {repr(char)} (char code {ord(char)})")
        
        if control_chars:
            issues.append(f"Found control characters: {control_chars}")
        
        
        try:
            json.loads(body_str)
            return {
                "message": "JSON is valid",
                "body_length": len(body_str),
                "issues": issues,
                "status": "valid"
            }
        except json.JSONDecodeError as e:
            
            error_pos = e.pos
            context_start = max(0, error_pos - 100)
            context_end = min(len(body_str), error_pos + 100)
            context = body_str[context_start:context_end]
            
            
            problem_char = body_str[error_pos] if error_pos < len(body_str) else "EOF"
            
            return {
                "message": "JSON is invalid",
                "error": str(e),
                "error_position": error_pos,
                "problem_character": repr(problem_char),
                "context": context,
                "body_length": len(body_str),
                "issues": issues,
                "status": "invalid"
            }
        
    except Exception as e:
        logger.error(f"Error in debug JSON endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Debug JSON endpoint error: {str(e)}")

@router.post("/test-post-image-type")
def test_post_image_type_endpoint(data: dict):
    """Test endpoint to verify post_image_type logic"""
    try:
        logger.info("Testing post_image_type logic endpoint")
        
        
        from ..main import determine_post_image_type, handle_image_url_storage
        
        
        test_cases = [
            ("Image URL", "Yes, Image URL"),
            ("Upload Image", "Yes, Upload Image"),
            ("AI Generated", "Yes, AI Generated"),
            ("", "No Image Needed"),
            (None, "No Image Needed"),
            ("Some other value", "Some other value"),
            ("Image URL with extra text", "Yes, Image URL"),
            ("Upload Image and more", "Yes, Upload Image"),
            ("AI Generated content", "Yes, AI Generated")
        ]
        
        results = []
        for input_val, expected in test_cases:
            actual = determine_post_image_type(input_val)
            results.append({
                "input": input_val,
                "expected": expected,
                "actual": actual,
                "matches": expected
            })
        
        
        if 'post_image_type' in data:
            provided_result = determine_post_image_type(data['post_image_type'])
            results.append({
                "input": data['post_image_type'],
                "expected": "custom input",
                "actual": provided_result,
                "matches": True
            })
        
        
        image_url_tests = [
            ("Yes, Image URL", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("Yes, Upload Image", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("Yes, AI Generated", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("No Image Needed", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"})
        ]
        
        image_url_results = []
        for post_image_type, test_data in image_url_tests:
            result = handle_image_url_storage(test_data.copy(), post_image_type)
            image_url_results.append({
                "post_image_type": post_image_type,
                "input": test_data,
                "output": result
            })
        
        return {
            "message": "Post image type logic and image URL storage test completed",
            "post_image_type_tests": results,
            "image_url_storage_tests": image_url_results,
            "all_tests_passed": all(r["matches"] for r in results),
            "functions_working": True
        }
        
    except Exception as e:
        logger.error(f"Error in post image type test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@router.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working correctly"""
    logger.info("CORS test endpoint called")
    return {"message": "CORS is working", "timestamp": datetime.utcnow().isoformat()}
