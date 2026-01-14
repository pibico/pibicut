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
        """Generate name from custom code or random string for NEW documents."""
        if self.custom_code:
            self._validate_custom_code(self.custom_code)
            self.name = self.custom_code
        else:
            # Generate random 5-character code
            random_code = random_string(5)
            while frappe.db.exists("Shortener", random_code):
                random_code = random_string(5)
            self.name = random_code

    def _validate_custom_code(self, code, check_exists=True):
        """Validate custom code format and availability."""
        if not re.match(r'^[a-zA-Z0-9\-]{3,20}$', code):
            frappe.throw(_("Custom code must be 3-20 characters, using only letters, numbers, and hyphens"))

        if check_exists and frappe.db.exists("Shortener", code):
            frappe.throw(_("Custom code '{0}' is already taken").format(code))

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

    def on_update(self):
        """Handle custom code change for EXISTING documents."""
        # Check if custom_code was set/changed and differs from current name
        if self.custom_code and self.custom_code != self.name:
            self._validate_custom_code(self.custom_code)

            old_name = self.name
            new_name = self.custom_code

            # Rename the document
            frappe.rename_doc("Shortener", old_name, new_name, force=True)

            # Update route and QR code with new name
            doc = frappe.get_doc("Shortener", new_name)
            doc.route = new_name
            doc.qr_code = get_qrcode(get_url(new_name), None, doc.qr_size or "Medium")
            doc.db_update()

            # Notify client about the rename for redirect
            frappe.local.response["new_name"] = new_name

            frappe.msgprint(
                _("Short URL renamed to: {0}. Redirecting...").format(get_url(new_name)),
                title=_("Renamed"),
                indicator="green"
            )

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
