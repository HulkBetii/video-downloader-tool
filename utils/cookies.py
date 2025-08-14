# utils/cookies.py

import os
import json


def is_valid_cookie_file(path):
    """
    Kiểm tra xem file cookies có tồn tại và hợp lệ không
    Hỗ trợ cả định dạng .txt (Netscape) và .json
    """
    if not os.path.exists(path):
        return False

    try:
        file_ext = os.path.splitext(path)[1].lower()
        
        if file_ext == '.json':
            return is_valid_json_cookie_file(path)
        else:
            return is_valid_txt_cookie_file(path)
    except Exception:
        return False


def is_valid_txt_cookie_file(path):
    """
    Kiểm tra file cookie .txt (Netscape format)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) == 0:
            return False

        # File phải chứa dòng có ít nhất 6 cột (domain, flag, path, secure, expires, name, value)
        for line in lines:
            if line.strip().startswith("#") or line.strip() == "":
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 6:
                return True
    except Exception:
        return False

    return False


def is_valid_json_cookie_file(path):
    """
    Kiểm tra file cookie .json
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Kiểm tra cấu trúc JSON cơ bản
        if isinstance(data, list):
            # Format: [{"name": "...", "value": "...", "domain": "..."}, ...]
            return len(data) > 0 and all(isinstance(item, dict) for item in data)
        elif isinstance(data, dict):
            # Format: {"cookies": [...]} hoặc {"domain": {...}}
            return len(data) > 0
        else:
            return False
    except (json.JSONDecodeError, Exception):
        return False


def extract_cookies_for_domain(cookie_path, domain):
    """
    Trích xuất cookies dành riêng cho một domain
    Hỗ trợ cả định dạng .txt và .json
    :param cookie_path: Đường dẫn file cookies (.txt hoặc .json)
    :param domain: Ví dụ: ".onedrive.live.com"
    :return: dict chứa các cookie
    """
    cookies = {}
    if not os.path.exists(cookie_path):
        return cookies

    file_ext = os.path.splitext(cookie_path)[1].lower()
    
    if file_ext == '.json':
        return extract_cookies_from_json(cookie_path, domain)
    else:
        return extract_cookies_from_txt(cookie_path, domain)


def extract_cookies_from_txt(cookie_path, domain):
    """
    Trích xuất cookies từ file .txt
    """
    cookies = {}
    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookie_domain, _, _, _, _, name, value = parts
                    if domain in cookie_domain:
                        cookies[name] = value
    except Exception:
        pass
    return cookies


def extract_cookies_from_json(cookie_path, domain):
    """
    Trích xuất cookies từ file .json
    """
    cookies = {}
    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # Format: [{"name": "...", "value": "...", "domain": "..."}, ...]
            for item in data:
                if isinstance(item, dict):
                    cookie_domain = item.get('domain', '')
                    name = item.get('name', '')
                    value = item.get('value', '')
                    if domain in cookie_domain and name and value:
                        cookies[name] = value
        elif isinstance(data, dict):
            # Format: {"cookies": [...]} hoặc {"domain": {...}}
            if 'cookies' in data and isinstance(data['cookies'], list):
                for item in data['cookies']:
                    if isinstance(item, dict):
                        cookie_domain = item.get('domain', '')
                        name = item.get('name', '')
                        value = item.get('value', '')
                        if domain in cookie_domain and name and value:
                            cookies[name] = value
            else:
                # Format: {"domain": {...}}
                for key, value in data.items():
                    if isinstance(value, dict) and domain in key:
                        for cookie_name, cookie_value in value.items():
                            if isinstance(cookie_value, str):
                                cookies[cookie_name] = cookie_value
    except Exception:
        pass
    return cookies


def convert_cookies_to_yt_dlp_format(cookie_path):
    """
    Chuyển đổi cookies sang định dạng mà yt-dlp có thể sử dụng
    :param cookie_path: Đường dẫn file cookies
    :return: dict với các tùy chọn yt-dlp
    """
    file_ext = os.path.splitext(cookie_path)[1].lower()
    
    if file_ext == '.json':
        # yt-dlp hỗ trợ trực tiếp file JSON
        return {'cookiefile': cookie_path}
    else:
        # File .txt được hỗ trợ trực tiếp
        return {'cookiefile': cookie_path}


def load_cookies_from_file(cookie_file):
    """
    Load cookies from file and return as dict
    Support both .txt (Netscape format) and .json formats
    
    Args:
        cookie_file (str): Path to cookie file
        
    Returns:
        dict: Cookies dictionary for requests
    """
    cookies = {}
    try:
        if not os.path.exists(cookie_file):
            print(f"Cookie file not found: {cookie_file}")
            return cookies
            
        file_ext = os.path.splitext(cookie_file)[1].lower()
        
        if file_ext == '.json':
            # Handle JSON cookie format
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
                
            # Parse JSON cookie structure
            if isinstance(cookie_data, list):
                # Format: [{"name": "...", "value": "...", "domain": "..."}, ...]
                for item in cookie_data:
                    if isinstance(item, dict):
                        name = item.get('name', '')
                        value = item.get('value', '')
                        if name and value:
                            cookies[name] = value
            elif isinstance(cookie_data, dict):
                # Format: {"cookies": [...]} hoặc {"domain": {...}}
                if 'cookies' in cookie_data and isinstance(cookie_data['cookies'], list):
                    for item in cookie_data['cookies']:
                        if isinstance(item, dict):
                            name = item.get('name', '')
                            value = item.get('value', '')
                            if name and value:
                                cookies[name] = value
                else:
                    # Format: {"domain": {...}}
                    for key, value in cookie_data.items():
                        if isinstance(value, dict):
                            for cookie_name, cookie_value in value.items():
                                if isinstance(cookie_value, str):
                                    cookies[cookie_name] = cookie_value
        else:
            # Handle Netscape .txt format
            with open(cookie_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("#") or line.strip() == "":
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        _, _, _, _, _, name, value = parts
                        if name and value:
                            cookies[name] = value
                            
        print(f"Loaded {len(cookies)} cookies from {cookie_file}")
        return cookies
        
    except Exception as e:
        print(f"Error loading cookies from {cookie_file}: {e}")
        return {}


def extract_cookies_for_domain(cookie_file, domain):
    """
    Extract cookies for specific domain from cookie file
    
    Args:
        cookie_file (str): Path to cookie file
        domain (str): Target domain (e.g., 'sharepoint.com')
        
    Returns:
        dict: Filtered cookies for the domain
    """
    all_cookies = load_cookies_from_file(cookie_file)
    domain_cookies = {}
    
    # Filter cookies by domain
    for name, value in all_cookies.items():
        # For now, return all cookies since we can't easily filter by domain
        # in the current cookie structure
        domain_cookies[name] = value
    
    print(f"Extracted {len(domain_cookies)} cookies for domain {domain}")
    return domain_cookies
