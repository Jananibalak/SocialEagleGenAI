# 📁 Assets Directory

This directory should contain the app's visual assets.

## Required Assets

### 1. App Icons

Create these icon files and place them here:

- **icon.png** (1024x1024px) - Main app icon
- **adaptive-icon.png** (1024x1024px) - Android adaptive icon
- **favicon.png** (48x48px) - Web favicon

**Icon Design Guidelines:**
- Use the EduPath yellow theme (#FFC107)
- Include the graduation cap emoji or a stylized "E"
- Keep it simple and recognizable
- Ensure it looks good at small sizes

### 2. Splash Screen

- **splash.png** (1242x2436px) - App splash screen

**Splash Design:**
- Yellow background (#FFC107)
- EduPath logo in center
- "AI Learning Coach" tagline
- Clean and professional

### 3. Notification Icon

- **notification-icon.png** (96x96px) - Android notification icon

**Design:**
- White icon on transparent background
- Simple shape (graduation cap or "E")
- Must be flat design (no gradients)

## Quick Asset Generation

### Using Figma (Free)

1. Create 1024x1024px canvas
2. Design icon with yellow background
3. Export as PNG
4. Resize for different sizes

### Using Canva (Free)

1. Use "App Icon" template
2. Customize with yellow theme
3. Add graduation cap emoji
4. Download in required sizes

### Using Online Tools

- [App Icon Generator](https://appicon.co/) - Generate all sizes
- [Favicon Generator](https://favicon.io/) - Generate favicons
- [Expo Icon Generator](https://expo.dev/tools) - Expo-specific tools

## Placeholder Instructions

For quick testing, you can use these placeholder commands:

### macOS/Linux

```bash
# Create placeholder icons (colored squares)
mkdir -p assets
cd assets

# Create 1024x1024 yellow square (requires ImageMagick)
convert -size 1024x1024 xc:#FFC107 icon.png
convert -size 1024x1024 xc:#FFC107 adaptive-icon.png
convert -size 48x48 xc:#FFC107 favicon.png
convert -size 1242x2436 xc:#FFC107 splash.png
convert -size 96x96 xc:#FFFFFF notification-icon.png
```

### Windows (PowerShell)

```powershell
# Create assets directory
mkdir assets -Force
cd assets

# Use Paint or online tools to create yellow squares
# Save as icon.png, adaptive-icon.png, etc.
```

### Online Generator

1. Go to https://icon.kitchen/
2. Choose "Text" or "Emoji"
3. Use 🎓 emoji or "EP" text
4. Set background to #FFC107
5. Download all sizes

## Asset Checklist

Before deploying:

- [ ] icon.png (1024x1024px) ✅
- [ ] adaptive-icon.png (1024x1024px) ✅
- [ ] favicon.png (48x48px) ✅
- [ ] splash.png (1242x2436px) ✅
- [ ] notification-icon.png (96x96px) ✅

## Brand Colors Reference

Use these colors in your assets:

```
Primary Yellow: #FFC107
Dark Yellow: #FFA000
Light Yellow: #FFECB3
Orange: #FF6F00
White: #FFFFFF
Black: #212121
```

## Testing Assets

After adding assets:

```bash
# Clear cache and rebuild
expo start -c

# Check if icons appear correctly
# Test on multiple devices
```

## Production Assets

For production deployment:

1. **Hire a designer** (Fiverr, Upwork) - $20-50
2. **Design yourself** (Figma, Canva) - Free
3. **Use AI generator** (DALL-E, Midjourney) - Varies

**Professional assets improve:**
- App store approval chances
- User trust and downloads
- Brand recognition

---

**Note:** The app will work with placeholder assets, but use professional assets for production!