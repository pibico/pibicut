# PibiCut

**URL Shortener and QR Code Generator for Frappe/ERPNext**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/pibico/pibicut)
[![Frappe](https://img.shields.io/badge/Frappe-v15-orange.svg)](https://frappeframework.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

PibiCut is a simple Frappe App to create shortened URLs and generate QR codes. When users access a short URL (e.g., `https://yoursite.com/MnOpQ`), they are automatically redirected to the original long URL. The QR code can also be scanned to access the short URL.

---

## Table of Contents

- [Features](#-features)
- [Version Compatibility](#-version-compatibility)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Code Structure](#-code-structure)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## Features

### Core Capabilities

- **URL Shortening** - Convert long URLs into 5-character short codes
- **Custom Short Codes** - Define your own memorable short codes (3-20 chars)
- **Custom Code Rename** - Change custom codes on existing URLs (auto-rename)
- **QR Code Generation** - Automatic styled QR code creation for each short URL
- **QR Code Sizes** - Choose Small, Medium, or Large QR code output
- **Custom Logo Support** - Embed your logo in the center of QR codes
- **Click Analytics** - Track click count and last clicked timestamp
- **Link Expiration** - Set optional expiration dates for time-limited links
- **Instant Redirect** - Short URLs redirect immediately to target destinations
- **UPI Support** - Works with UPI payment links in addition to HTTP/HTTPS URLs
- **Guest Access** - Short URLs work without authentication (public redirect pages)
- **Bulk Export** - Export multiple QR codes as a ZIP file

### QR Code Features

| Feature | Description |
|---------|-------------|
| **Styled Design** | Radial gradient (steelblue → black) with gapped squares |
| **Size Options** | Small, Medium, Large output sizes |
| **Embedded Logo** | Optional PNG image in the center of QR code |
| **Error Correction** | Uses ERROR_CORRECT_H level for reliable logo embedding |
| **Base64 Storage** | QR codes stored as data URLs (no separate files) |
| **Instant Preview** | Live QR code preview in the form |
| **Download Button** | One-click download as PNG file |

### Limitations

- Short codes are 5 random characters (or custom 3-20 chars)
- Logo images must be PNG format with white background (not transparent)
- Custom codes: letters, numbers, and hyphens only

---

## Version Compatibility

| Frappe Version | PibiCut Branch | Status | Notes |
|----------------|----------------|--------|-------|
| **v15** | `version-15` | Active Development | Recommended for new installations |
| **v14** | `version-14` | Stable | Production ready |
| **v13** | `version-13` | Stable | Production ready |
| **v12** | `version-12` | Legacy | No longer maintained |

---

## Requirements

### System Requirements

- **Frappe/ERPNext**: v12, v13, v14, or v15
- **Python**: 3.10+ (included with Frappe v15)

### Python Dependencies

```txt
qrcode>=7.0.0
pillow>=9.0.0
six>=1.16.0
```

These are automatically installed via `pyproject.toml`.

---

## Installation

### Standard Installation

```bash
# Navigate to your frappe-bench directory
cd ~/frappe-bench

# Download the app
bench get-app pibicut https://github.com/pibico/pibicut.git

# Install on your site
bench --site your-site-name install-app pibicut

# Restart bench to apply changes
bench restart
```

### Multi-tenant Installation

```bash
bench --site site_name install-app pibicut
```

### Updating

```bash
# Update the app
cd ~/frappe-bench
bench update

# If you encounter dependency issues
bench update --requirements

# Restart
bench restart
```

### Uninstalling

```bash
bench --site your-site-name uninstall-app pibicut
bench remove-app pibicut
```

---

## Configuration

No configuration required! PibiCut works out of the box after installation.

### Permissions

By default, the Shortener DocType has the following permissions:

| Role | Create | Read | Write | Delete | Export | Print |
|------|--------|------|-------|--------|--------|-------|
| **System Manager** | Yes | Yes | Yes | Yes | Yes | Yes |
| **All** | Yes | Yes | Yes | No | Yes | Yes |

To modify permissions, navigate to **Shortener** > **Settings** > **Role Permissions Manager**.

---

## Usage

### Creating a Short URL

1. Navigate to **Shortener** in the sidebar or search bar
2. Click **+ Add Shortener** (or **New**)
3. Enter the **Long URL** (must start with `http://`, `https://`, or `upi:`)
4. (Optional) Enter a **Custom Short Code** (3-20 chars, letters/numbers/hyphens)
5. (Optional) Set **Expires On** date for time-limited links
6. (Optional) Select **QR Code Size** (Small/Medium/Large)
7. (Optional) Attach a **Logo** image (PNG with white background)
8. Click **Save**

### Result

After saving, you will get:

- **Short URL**: `https://yoursite.com/MnOpQ` (random) or `https://yoursite.com/your-code` (custom)
- **QR Code**: Styled QR code image with optional logo
- **Copy Button**: One-click copy of short URL to clipboard
- **Download Button**: Download QR code as PNG
- **Web Page**: Accessing the short URL redirects to the long URL

### Changing Custom Code (Existing URLs)

You can change the custom code of an existing short URL:

1. Open the existing Shortener document
2. Enter a new **Custom Short Code**
3. Click **Save**
4. Document is renamed, QR code regenerated with logo preserved
5. Browser automatically redirects to the new URL

### Sharing the Short URL

You can share the short URL in two ways:

1. **Direct Link**: Copy the short URL and share it
2. **QR Code**: Download or print the QR code for scanning

### Example

| Field | Value |
|-------|-------|
| **Long URL** | `https://example.com/very/long/path/to/page?param1=value1&param2=value2` |
| **Short URL** | `https://yoursite.com/xK9Pb` |
| **Redirect** | Accessing `https://yoursite.com/xK9Pb` goes to the long URL |

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PibiCut Flow                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  User creates Shortener doc                               │
│            ↓                                              │
│  ┌──────────────────────────────────────────────────┐    │
│  │ autoname()                                        │    │
│  │ - Generates 5-char random code (e.g., "MnOpQ")   │    │
│  │ - Checks for uniqueness                           │    │
│  └──────────────────────────────────────────────────┘    │
│            ↓                                              │
│  ┌──────────────────────────────────────────────────┐    │
│  │ before_save()                                     │    │
│  │ - Sets route = short code                         │    │
│  │ - Generates QR code with optional logo            │    │
│  │ - Sets published = True for WebsiteGenerator      │    │
│  └──────────────────────────────────────────────────┘    │
│            ↓                                              │
│  Document saved with short URL and QR code               │
│                                                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    Redirect Flow                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  User visits: https://yoursite.com/MnOpQ                 │
│            ↓                                              │
│  ┌──────────────────────────────────────────────────┐    │
│  │ WebsiteGenerator serves shortener.html template  │    │
│  │ - JavaScript: window.location.replace(long_url)  │    │
│  │ - HTML fallback: Link to long_url                │    │
│  └──────────────────────────────────────────────────┘    │
│            ↓                                              │
│  Browser redirects to: https://example.com/long/url      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### WebsiteGenerator

The Shortener DocType extends `WebsiteGenerator`, which enables:

- Public web pages without authentication
- Custom routes based on document fields
- Template-based rendering

#### QR Code Generation

QR codes are generated using:

- **qrcode** library with `StyledPilImage`
- **Radial gradient** color mask (steelblue center → black edges)
- **Gapped square** module drawer for modern look
- **Optional logo** embedding with PIL

---

## Code Structure

### Directory Layout

```
pibicut/
├── pibicut/
│   ├── __init__.py
│   ├── hooks.py                 # Frappe integration hooks
│   └── pibicut/
│       ├── __init__.py
│       ├── custom.py            # QR code generation (get_qrcode)
│       └── doctype/
│           └── shortener/
│               ├── __init__.py
│               ├── shortener.json      # DocType schema
│               ├── shortener.py        # Server controller
│               ├── shortener.js        # Client form script
│               ├── shortener_list.js   # List view config
│               ├── test_shortener.py   # Test file
│               └── templates/
│                   ├── shortener.html      # Redirect template
│                   └── shortener_row.html  # List row template
├── pyproject.toml              # Python dependencies
├── README.md                   # This file
├── CLAUDE.md                   # AI assistant context
└── license.txt                 # MIT License
```

### Key Files

#### `pibicut/hooks.py`

**Purpose**: Defines app metadata and Frappe integration

```python
app_name = "pibicut"
app_title = "Pibicut"
app_publisher = "PibiCo"
app_description = "Frappe/ERPNext URL Shortener"
app_license = "MIT"
```

#### `pibicut/pibicut/custom.py`

**Purpose**: QR code generation logic

```python
def get_qrcode(input_data, logo):
    """
    Generate a styled QR code with optional embedded logo.

    Args:
        input_data: The URL to encode
        logo: Path to logo image (PNG) or None

    Returns:
        Base64-encoded data URL of the QR code PNG
    """
```

**Features**:
- Radial gradient color mask (steelblue → black)
- Gapped square module drawer
- Square eye drawer
- Optional logo embedding
- Returns base64 data URL

#### `pibicut/pibicut/doctype/shortener/shortener.py`

**Purpose**: Server-side controller for Shortener DocType

**Key Methods**:

| Method | Purpose |
|--------|---------|
| `autoname()` | Use custom_code or generate random 5-char code (new docs) |
| `_validate_custom_code()` | Validate custom code format and availability |
| `short_url` | Property returning full short URL |
| `validate()` | Validate URL format (http/https/upi) |
| `before_save()` | Generate QR code with logo and set route |
| `on_update()` | Rename document if custom_code changed (existing docs) |
| `get_context()` | Handle redirect with click tracking and expiration |

**Code Flow**:

```python
class Shortener(WebsiteGenerator):
    def autoname(self):
        # For NEW documents
        if self.custom_code:
            self._validate_custom_code(self.custom_code)
            self.name = self.custom_code
        else:
            random_code = random_string(5)
            while frappe.db.exists("Shortener", random_code):
                random_code = random_string(5)
            self.name = random_code

    def on_update(self):
        # For EXISTING documents - rename if custom_code changed
        if self.custom_code and self.custom_code != self.name:
            self._validate_custom_code(self.custom_code)
            frappe.rename_doc("Shortener", self.name, self.custom_code)
            # Regenerate QR with logo
            doc = frappe.get_doc("Shortener", self.custom_code)
            doc.qr_code = get_qrcode(get_url(self.custom_code), logo, size)
            doc.db_update()

    def before_save(self):
        # Generate QR code with size and logo
        self.qr_code = get_qrcode(get_url(self.name), logo_path, self.qr_size)
        self.published = True
        self.route = self.name

    def get_context(self, context):
        # Check expiration, increment click count, redirect
        if self.expires_on and get_datetime(self.expires_on) < now_datetime():
            context.expired = True
            return context
        frappe.db.set_value("Shortener", self.name, {
            "click_count": (self.click_count or 0) + 1,
            "last_clicked": now_datetime()
        }, update_modified=False)
        context.redirect_url = self.long_url
```

#### `pibicut/pibicut/doctype/shortener/shortener.js`

**Purpose**: Client-side form script

**Features**:
- QR code preview in form
- Short URL display with clickable link
- Copy URL button with clipboard support
- Download QR code as PNG button
- Real-time URL validation indicator
- Custom code availability check
- Auto-redirect after custom code rename (`after_save` handler)

#### `templates/shortener.html`

**Purpose**: Redirect template served at short URL

```html
{% block head %}
  <script type="text/javascript">
    window.location.replace("{{ long_url }}");
  </script>
{% endblock %}

{% block page_content %}
  <p>Redirecting to</p>
  <a href='{{ long_url }}'>{{ long_url }}</a>
{% endblock %}
```

**Redirect Method**: JavaScript `window.location.replace()` with HTML fallback

---

## API Reference

### DocType: Shortener

#### Fields

| Fieldname | Type | Required | Description |
|-----------|------|----------|-------------|
| `long_url` | Small Text | Yes | Original URL to redirect to |
| `custom_code` | Data | No | User-defined short code (3-20 chars) |
| `expires_on` | Datetime | No | Optional expiration date |
| `qr_size` | Select | No | QR code size: Small/Medium/Large |
| `logo` | Attach | No | Logo image to embed in QR code |
| `click_count` | Int | - | Number of times URL was accessed |
| `last_clicked` | Datetime | - | Timestamp of last access |
| `created_on` | Date | - | Document creation date |
| `short_url` | Virtual Data | - | Computed full short URL |
| `qr_code` | Attach Image | - | Generated QR code (base64) |
| `route` | Data | - | WebsiteGenerator route (hidden) |
| `published` | Check | - | WebsiteGenerator flag (hidden) |

#### Properties

```python
@property
def short_url(self):
    """Returns the full short URL including domain"""
    return get_url(self.name)  # e.g., https://yoursite.com/MnOpQ
```

### Utility Function

#### `get_qrcode(input_data, logo, size)`

**Location**: `pibicut.pibicut.custom`

**Purpose**: Generate styled QR code with size options

**Parameters**:
- `input_data` (str): URL to encode in QR code
- `logo` (str|None): Path to logo image file
- `size` (str): QR code size - "Small", "Medium", or "Large"

**Returns**: `str` - Base64-encoded data URL (`data:image/png;base64,...`)

**Size Configuration**:
```python
SIZE_CONFIG = {
    "Small": {"box_size": 4, "version": 5},
    "Medium": {"box_size": 6, "version": 7},
    "Large": {"box_size": 10, "version": 7},
}
```

**Usage**:

```python
from pibicut.pibicut.custom import get_qrcode

# Without logo, medium size
qr = get_qrcode("https://example.com", None, "Medium")

# With logo, large size
qr = get_qrcode("https://example.com", "/path/to/logo.png", "Large")
```

#### `get_qrcode_binary(input_data, logo, size)`

**Location**: `pibicut.pibicut.custom`

**Purpose**: Generate styled QR code as binary data (for ZIP export)

**Parameters**: Same as `get_qrcode()`

**Returns**: `bytes` - Binary PNG image data

### API Endpoints (`pibicut.pibicut.api`)

#### `check_custom_code(code)`

Check if a custom short code is available.

**Parameters**:
- `code` (str): The custom code to check

**Returns**: `dict` with `available` (bool) and `message` (str)

#### `validate_url(url)`

Validate URL format and optionally check if reachable.

**Parameters**:
- `url` (str): The URL to validate

**Returns**: `dict` with `valid` (bool) and `message` (str)

#### `export_qr_codes_zip(shortener_names)`

Export multiple QR codes as a ZIP file.

**Parameters**:
- `shortener_names` (list): List of Shortener document names

**Returns**: `dict` with `success`, `file_url`, `filename`, `count`

#### `get_shortener_stats()`

Get statistics about all shorteners.

**Returns**: `dict` with `total`, `total_clicks`, `active`, `expired`, `most_clicked`, `recent`

---

## Troubleshooting

### Common Issues

#### "Try again, generated code is repeated"

**Cause**: Randomly generated code already exists (rare collision)

**Solution**: Simply save again - a new code will be generated

#### "Please enter a proper URL or UPI"

**Cause**: URL doesn't start with `http://`, `https://`, or `upi:`

**Solution**: Ensure your URL includes the protocol prefix

#### QR Code Not Displaying

**Causes**:
- Browser not rendering base64 images
- QR code field is empty

**Solutions**:
1. Refresh the page (Ctrl+Shift+R)
2. Check if `qr_code` field has data
3. Try a different browser

#### Logo Not Appearing in QR Code

**Cause**: Logo image format issues

**Solutions**:
- Use PNG format only (not JPG, GIF)
- Use white background (not transparent)
- Ensure image is attached before saving

#### Short URL Returns 404

**Causes**:
- Document not saved properly
- `published` flag is False
- Cache issues

**Solutions**:
```bash
# Clear cache
bench --site your-site-name clear-cache

# Check document
bench --site your-site-name console
>>> frappe.get_doc("Shortener", "MnOpQ")
```

### Debug Mode

```bash
# Enable developer mode
# Edit sites/your-site-name/site_config.json:
{
    "developer_mode": 1
}

# Restart
bench restart

# Check logs
tail -f ~/frappe-bench/logs/web.log
```

---

## Development

### Development Setup

```bash
# Clone repository
cd ~/frappe-bench/apps
git clone https://github.com/pibico/pibicut.git

# Install
bench --site your-site-name install-app pibicut

# Enable developer mode
bench --site your-site-name set-config developer_mode 1

# Restart
bench restart
```

### Running Tests

```bash
bench --site your-site-name run-tests --app pibicut
```

### Code Style

- **Python**: Follow PEP 8
- **Formatting**: black (line-length 99)
- **Imports**: isort

### Customizing Short Code Length

To change the short code length from 5 characters:

Edit `shortener.py`:

```python
def autoname(self):
    random_code = random_string(8)  # Change from 5 to 8
    # ...
```

### Customizing QR Code Style

Edit `custom.py` to modify:

```python
# Colors (RGB tuples)
center_color = (70, 130, 180)  # steelblue
edge_color = (0, 0, 0)         # black
back_color = (255, 255, 255)   # white

# Module drawer options:
# - SquareModuleDrawer
# - GappedSquareModuleDrawer
# - CircleModuleDrawer
# - RoundedModuleDrawer
# - VerticalBarsDrawer
# - HorizontalBarsDrawer
```

---

## Contributing

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`
6. **Create Pull Request** on GitHub

### PR Requirements

- Clear description of changes
- Test results (screenshots if applicable)
- Follows code style

---

## License

MIT License - see [license.txt](license.txt) for details

Copyright (c) 2021-2026 PibiCo

---

## Support

- **GitHub Issues**: https://github.com/pibico/pibicut/issues
- **Email**: pibico.sl@gmail.com

---

## Credits

- **Developed by**: PibiCo (pibico.sl@gmail.com)
- **QR Code Library**: [python-qrcode](https://github.com/lincolnloop/python-qrcode)
- **Image Processing**: [Pillow](https://python-pillow.org/)
- **Framework**: [Frappe](https://frappeframework.com)

---

**Made with care by PibiCo**

For the latest updates, visit: https://github.com/pibico/pibicut
