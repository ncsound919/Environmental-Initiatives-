# Branding Assets

This directory contains official branding assets for Overlay Cheetah and Overlay365.

## Images

### 1. Overlay Cheetah Logo (`overlay-cheetah-logo.svg`)
**Purpose:** Primary product logo for Overlay Cheetah  
**Dimensions:** 400x120px  
**Motto:** "The code of the streets"  
**Usage:**
- Project splash screens
- Application startup logo
- CLI tool branding
- Documentation headers
- README files

**Recommended Usage:**
```python
import os
# In your application
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets/branding/overlay-cheetah-logo.svg")
# Use for splash screen, about dialog, or startup banner
```

### 2. Overlay365 Brand Image (`overlay365-brand.svg`)
**Purpose:** Corporate brand image for Overlay365  
**Dimensions:** 600x200px  
**Usage:**
- About dialogs
- Corporate/company information screens
- Website branding
- Marketing materials
- License information screens

**Recommended Usage:**
```python
import os
BRAND_PATH = os.path.join(os.path.dirname(__file__), "assets/branding/overlay365-brand.svg")
# Use for About dialog, company info, or corporate screens
```

## Integration Guidelines

### IDE/Splash Screen Integration
Use `overlay-cheetah-logo.svg` for:
- Application launch splash screen
- Main window header/title bar
- Tool icons and shortcuts

### About/Corporate Screens
Use `overlay365-brand.svg` for:
- About dialog box
- License information screen
- Company/corporate information pages
- Help > About menu items

### Documentation Integration
Both images should be included in:
- Main README.md (at the top)
- docs/README.md (documentation header)
- User guides and tutorials
- Release notes and changelogs

## File Formats

Both images are provided in SVG format for:
- ✅ Scalability (vector graphics)
- ✅ Small file size
- ✅ Cross-platform compatibility
- ✅ High quality at any resolution
- ✅ Easy integration in web and desktop applications

## Color Scheme

**Primary Colors:**
- Gray Backgrounds: `#4A4A4A`, `#6B6B6B`
- McDonald's Yellow: `#FFC845`, `#FFD700`
- Mauve: `#DDA0DD`
- Light Peach: `#FFDAB9`
- Light Gray Text: `#D3D3D3`

## Accessibility

Both images include:
- High contrast ratios for readability
- Clear, legible text
- Proper alt-text support in markdown
- SVG semantic structure for screen readers

## License

These branding assets are part of the Overlay Cheetah V3 project and are licensed under the Apache License 2.0.

## Notes

- Do not modify the logos without authorization
- Maintain aspect ratios when resizing
- Ensure proper attribution when using in derivative works
- For print materials, convert SVG to high-resolution PNG/PDF
