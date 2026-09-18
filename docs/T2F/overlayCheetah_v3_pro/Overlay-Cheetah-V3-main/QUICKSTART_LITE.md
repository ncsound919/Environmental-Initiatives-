# Quick Start Guide - OverlayCheetah V3 Lite

Get up and running with OverlayCheetah V3 Lite in 5 minutes! 🚀

---

## Step 1: Prerequisites ✅

Make sure you have:
- **Python 3.7+** installed
  - Check: `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)

---

## Step 2: Download & Install 📦

```bash
# Navigate to the project directory
cd Overlay-Cheetah-V3

# Install required dependency
pip install pyyaml

# Verify installation
python3 -c "import yaml; print('✓ Ready to go!')"
```

---

## Step 3: Launch the App 🎯

```bash
python3 overlay_cheetah_v3_lite.py
```

The app window will open automatically!

---

## Step 4: First-Time Setup 🧙‍♂️

On first launch, you'll see the **Welcome Wizard**:

### Screen 1: Welcome
- Read the introduction
- Click **"Get Started"**

### Screen 2: Choose Template
Pick your starter template:
- **Simple Blog** - For personal sites, portfolios
- **Task List** - For todo apps, simple tools  
- **Landing Page** - For product launches, info pages

### Screen 3: Project Details
- Enter your **Project Name** (e.g., "MyFirstApp")
- Click **"Next"**

### Screen 4: Upgrade Info
- Learn about Lite vs PRO
- Click **"Continue with Lite"** (or upgrade!)

---

## Step 5: Build Your First Project 🏗️

### Main Interface

You'll see:
- **Yellow banner** at top (showing Lite version)
- **Project Setup** section
- **PRO Features** section (locked)
- **Output** area at bottom

### Create a Project

1. **Review Project Name** (from wizard)
2. **Select Project Type**
   - Simple Web App
   - Basic API
3. **Click "Generate Basic Template"**
   - Check output area for confirmation
4. **Click "Build Project (Simple)"**
   - Review generated files

### Generated Files

Look for:
- `generated_template_lite.yaml` - Your project template
- `settings_lite.json` - Your app settings (auto-created)

---

## Step 6: Explore Features 🔍

### What You Can Do

✅ **Generate Templates**
- Choose from 3 starter templates
- Customize project name and type
- Generate YAML structure

✅ **Build Projects**
- Execute template generation
- Review output and files
- Learn the workflow

✅ **Get Help**
- Click "Help" button
- Hover over elements for tooltips
- Read the status bar

### What's Locked 🔒

The Lite version shows (but locks) PRO features:
- LLM integrations
- Advanced templates
- Security scanning
- Project save/load
- EXE builder

**Want to unlock?** Click any "🌟 UPGRADE" button!

---

## Common Tasks 📋

### Start a New Project

1. Change **Project Name** field
2. Select different **Project Type**
3. Click **"Generate Basic Template"**
4. Click **"Build Project"**

### Read Generated Template

```bash
# View the generated YAML
cat generated_template_lite.yaml

# Or open in text editor
code generated_template_lite.yaml  # VS Code
nano generated_template_lite.yaml  # Terminal editor
```

### Reset Settings

Delete the settings file:
```bash
rm settings_lite.json
```

Next launch will show the wizard again!

---

## Troubleshooting 🔧

### "tkinter not found"

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

**Windows:**
- Reinstall Python with "tcl/tk and IDLE" option checked

### "Module 'yaml' not found"

```bash
pip install pyyaml
# or
pip3 install pyyaml
```

### "Permission denied"

Make sure you're in the correct directory:
```bash
cd /path/to/Overlay-Cheetah-V3
ls -la overlay_cheetah_v3_lite.py  # Should exist
```

### Window doesn't appear

Check terminal for errors:
```bash
python3 overlay_cheetah_v3_lite.py 2>&1 | tee error.log
```

Send `error.log` to support@overlayapp.com for help!

---

## Next Steps 🎓

### Learn More
- **[Full Documentation](README_LITE.md)** - Complete guide
- **[Lite vs PRO](LITE_VS_PRO.md)** - Feature comparison
- **[Tutorials](README_LITE.md#-tutorials)** - Step-by-step guides

### Experiment
- Try all 3 templates
- Experiment with different names
- Read generated YAML files
- Learn the workflow

### Upgrade When Ready
When you need more power:
- **Click** any "🌟 UPGRADE" button
- **Visit** [overlayapp.com/upgrade](https://overlayapp.com/upgrade)
- **Email** sales@overlayapp.com

---

## Getting Help 💬

### Free Support (Lite)
- **Documentation**: This guide + [README_LITE.md](README_LITE.md)
- **Community**: [GitHub Discussions](https://github.com/tap919/Overlay-Cheetah-V3/discussions)
- **Email**: support@overlayapp.com (3-5 business days)

### Priority Support (PRO)
- Same-day email response
- Live chat
- Dedicated assistance

---

## Keyboard Shortcuts ⌨️

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quit app |
| `F1` | Help dialog |
| `Tab` | Navigate fields |
| `Enter` | Submit/Continue |

---

## Tips for Success 💡

1. **Start Simple** - Use basic templates first
2. **Read Output** - Check the output area for messages
3. **Experiment** - Try different combinations
4. **Learn** - Study generated files to understand structure
5. **Upgrade** - When you need more, PRO is ready!

---

## Example Workflow 🎬

Here's a typical session:

```
1. Launch app
   → python3 overlay_cheetah_v3_lite.py

2. Complete wizard (first time only)
   → Choose "Task List" template
   → Name it "MyTodos"

3. In main window
   → Review project settings
   → Click "Generate Basic Template"
   → See output: "✓ Template generated"

4. Build project
   → Click "Build Project (Simple)"
   → Check output for files created

5. Review files
   → Open generated_template_lite.yaml
   → See your project structure

6. Start again!
   → Change name to "ShoppingList"
   → Repeat steps 3-5
```

---

## FAQ ❓

**Q: Is this really free?**
A: Yes! No credit card, no trial period, free forever.

**Q: Can I use Lite for real projects?**
A: Yes for personal/educational. No for commercial (need PRO).

**Q: Will I lose work if I upgrade?**
A: No! Everything transfers to PRO seamlessly.

**Q: How long does the wizard take?**
A: About 1-2 minutes. Only shows once (unless you reset).

**Q: Can I skip the wizard?**
A: It only shows on first launch. After that, straight to main app!

---

## Success! 🎉

You're now ready to build with OverlayCheetah V3 Lite!

**Questions?** → support@overlayapp.com

**Ready for more?** → [Upgrade to PRO](LITE_VS_PRO.md)

**Happy building!** 🚀

---

*Last updated: December 2024*
