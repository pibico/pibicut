# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import re
import frappe
from frappe.website.website_generator import WebsiteGenerator

from frappe import _, msgprint, throw
from frappe.utils import random_string, get_url, now_datetime, today, get_datetime

from pibicut.pibicut.custom import get_qrcode


class Shortener(WebsiteGenerator):
    def autoname(self):
        """Generate name from custom code or random string."""
        if self.custom_code:
            # Validate custom code format
            if not re.match(r'^[a-zA-Z0-9\-]{3,20}$', self.custom_code):
                frappe.throw(_("Custom code must be 3-20 characters, using only letters, numbers, and hyphens"))

            # Check if custom code already exists
            existing = frappe.db.exists("Shortener", self.custom_code)
            if existing:
                frappe.throw(_("Custom code '{0}' is already taken").format(self.custom_code))

            self.name = self.custom_code
        else:
            # Generate random 5-character code
            random_code = random_string(5)
            while frappe.db.exists("Shortener", random_code):
                random_code = random_string(5)
            self.name = random_code

    @property
    def short_url(self):
        return get_url(self.name)

    def validate(self):
        if not (self.long_url.startswith("http") or self.long_url.startswith("upi")):
            frappe.throw(_("Please enter a proper URL or UPI"))

    def before_save(self):
        # Set created_on for new documents
        if self.is_new():
            self.created_on = today()

        url_short = "".join([self.name])
        qr_code = get_url(url_short)

        # Get logo if attached
        logo_files = frappe.get_all("File",
            fields=["name", "file_name", "file_url", "is_private"],
            filters={
                "attached_to_name": self.name,
                "attached_to_field": "logo",
                "attached_to_doctype": "Shortener"
            },
        )
        logo = None
        if logo_files:
            logo = frappe.utils.get_files_path(
                logo_files[0].file_name,
                is_private=logo_files[0].is_private
            )

        # Generate QR code with size option
        size = self.qr_size if self.qr_size else "Medium"
        self.qr_code = get_qrcode(qr_code, logo, size)
        self.published = True
        self.route = url_short

    def get_context(self, context):
        """Handle redirect with click tracking and expiration check."""
        # Check if link has expired
        if self.expires_on:
            if get_datetime(self.expires_on) < now_datetime():
                context.expired = True
                context.show_sidebar = False
                return context

        # Update click count and last clicked (without triggering hooks)
        frappe.db.set_value(
            "Shortener",
            self.name,
            {
                "click_count": (self.click_count or 0) + 1,
                "last_clicked": now_datetime()
            },
            update_modified=False
        )

        context.redirect_url = self.long_url
        context.show_sidebar = False
        return context
