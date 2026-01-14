# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_url, now_datetime
import zipfile
import base64
from io import BytesIO
import json

from pibicut.pibicut.custom import get_qrcode_binary
import re
import requests


@frappe.whitelist()
def check_custom_code(code):
    """
    Check if a custom short code is available.

    Args:
        code (str): The custom code to check

    Returns:
        dict: Contains 'available' boolean and 'message' string
    """
    if not code:
        return {"available": False, "message": _("Code cannot be empty")}

    # Validate format
    if not re.match(r'^[a-zA-Z0-9\-]{3,20}$', code):
        return {
            "available": False,
            "message": _("Code must be 3-20 characters, using only letters, numbers, and hyphens")
        }

    # Check if exists
    exists = frappe.db.exists("Shortener", code)

    if exists:
        return {"available": False, "message": _("This code is already taken")}

    return {"available": True, "message": _("Code is available")}


@frappe.whitelist()
def validate_url(url):
    """
    Validate a URL format and optionally check if it's reachable.

    Args:
        url (str): The URL to validate

    Returns:
        dict: Contains 'valid' boolean and 'message' string
    """
    if not url:
        return {"valid": False, "message": _("URL cannot be empty")}

    # Check URL format
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("upi://")):
        return {"valid": False, "message": _("URL must start with http://, https://, or upi://")}

    # For UPI URLs, just check format
    if url.startswith("upi://"):
        return {"valid": True, "message": _("Valid UPI URL")}

    # Try to reach the URL (with timeout)
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code < 400:
            return {"valid": True, "message": _("Valid URL")}
        else:
            return {
                "valid": True,
                "message": _("URL format valid (server returned {0})").format(response.status_code)
            }
    except requests.exceptions.Timeout:
        return {"valid": True, "message": _("Valid URL format (server timeout)")}
    except requests.exceptions.ConnectionError:
        return {"valid": True, "message": _("Valid URL format (connection failed)")}
    except Exception:
        return {"valid": True, "message": _("Valid URL format")}


@frappe.whitelist()
def export_qr_codes_zip(shortener_names):
    """
    Export multiple QR codes as a ZIP file.

    Args:
        shortener_names (list or str): List of Shortener document names

    Returns:
        dict: Contains file_url to download the ZIP file
    """
    # Parse JSON if string
    if isinstance(shortener_names, str):
        shortener_names = json.loads(shortener_names)

    if not shortener_names:
        return {"success": False, "error": _("No shorteners selected")}

    # Create ZIP file in memory
    zip_buffer = BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for name in shortener_names:
                # Get shortener document
                if not frappe.db.exists("Shortener", name):
                    continue

                doc = frappe.get_doc("Shortener", name)

                # Generate QR code URL
                qr_url = get_url(doc.name)

                # Get QR size
                size = doc.qr_size or "Medium"

                # Generate QR code as binary
                qr_binary = get_qrcode_binary(qr_url, None, size)

                # Add to ZIP with sanitized filename
                filename = f"qr_{sanitize_filename(name)}.png"
                zip_file.writestr(filename, qr_binary)

        # Get ZIP content
        zip_buffer.seek(0)
        zip_content = zip_buffer.read()

        # Create temporary file for download
        timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"qr_codes_{timestamp}.zip"

        # Save as a File document
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": zip_filename,
            "content": zip_content,
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)

        return {
            "success": True,
            "file_url": file_doc.file_url,
            "filename": zip_filename,
            "count": len(shortener_names)
        }

    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="QR Export Error"
        )
        return {"success": False, "error": str(e)}


def sanitize_filename(filename):
    """
    Sanitize filename to remove invalid characters.

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename safe for file systems
    """
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


@frappe.whitelist()
def get_shortener_stats():
    """
    Get statistics about shorteners.

    Returns:
        dict: Statistics including total count, total clicks, etc.
    """
    # Total shorteners
    total = frappe.db.count("Shortener")

    # Total clicks
    total_clicks = frappe.db.sql("""
        SELECT COALESCE(SUM(click_count), 0) as total
        FROM `tabShortener`
    """)[0][0]

    # Active (not expired) shorteners
    active = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabShortener`
        WHERE expires_on IS NULL OR expires_on > NOW()
    """)[0][0]

    # Expired shorteners
    expired = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabShortener`
        WHERE expires_on IS NOT NULL AND expires_on <= NOW()
    """)[0][0]

    # Most clicked
    most_clicked = frappe.db.sql("""
        SELECT name, long_url, click_count
        FROM `tabShortener`
        ORDER BY click_count DESC
        LIMIT 5
    """, as_dict=True)

    # Recently created
    recent = frappe.db.sql("""
        SELECT name, long_url, creation
        FROM `tabShortener`
        ORDER BY creation DESC
        LIMIT 5
    """, as_dict=True)

    return {
        "total": total,
        "total_clicks": total_clicks,
        "active": active,
        "expired": expired,
        "most_clicked": most_clicked,
        "recent": recent
    }


@frappe.whitelist(allow_guest=True)
def track_click(shortener_name):
    """
    Track a click on a shortened URL.

    This is called from the redirect template to track analytics.

    Args:
        shortener_name (str): Name of the Shortener document

    Returns:
        dict: Status of the tracking operation
    """
    if not frappe.db.exists("Shortener", shortener_name):
        return {"success": False, "error": "Shortener not found"}

    try:
        doc = frappe.get_doc("Shortener", shortener_name)

        # Check if expired
        if doc.expires_on and now_datetime() > doc.expires_on:
            return {"success": False, "error": "Link expired"}

        # Increment click count
        frappe.db.set_value(
            "Shortener",
            shortener_name,
            {
                "click_count": (doc.click_count or 0) + 1,
                "last_clicked": now_datetime()
            },
            update_modified=False
        )
        frappe.db.commit()

        return {"success": True, "redirect_url": doc.long_url}

    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Click Tracking Error"
        )
        return {"success": False, "error": str(e)}
