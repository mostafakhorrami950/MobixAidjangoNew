# File Upload Testing Guide

## Quick Test - Follow These Steps

### 1. Clear Browser Cache
**Important:** Clear cache before testing to ensure you're using the latest code.

**Chrome/Edge:**
- Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Select "Cached images and files"
- Click "Clear data"
- OR simply press `Ctrl+F5` to hard refresh

**Firefox:**
- Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Check "Cache"
- Click "Clear Now"

**Safari:**
- Press `Cmd+Option+E` to empty cache
- Refresh page

---

### 2. Open Developer Console
Press `F12` or right-click → "Inspect" → "Console" tab

This will show you debug messages that help identify any issues.

---

### 3. Test File Upload - Desktop

#### Test A: Single File Upload
1. Click the file upload button (📎 paperclip icon)
2. **CHECK:** File picker should open **only once** (not twice!)
3. Select a single image/PDF/document
4. **CHECK:** You should see these console logs:
   ```
   [DEBUG] triggerFileSelect called
   [DEBUG] File input element found, triggering click
   [DEBUG] handleFileSelect called
   [DEBUG] Files selected: 1 files
   [DEBUG] addFiles called with 1 files
   [DEBUG] Processing file: filename.ext Type: image/jpeg Size: 12345
   [DEBUG] updateFilePreview called. Selected files: 1
   [DEBUG] Showing preview container with 1 files
   ```
5. **CHECK:** File preview should appear below the message input showing:
   - File name
   - File size
   - File icon
   - Remove button (X)
6. **CHECK:** Send button should become enabled

#### Test B: Multiple Files Upload
1. Click the upload button again
2. Select multiple files (2-3 files)
3. **CHECK:** All files appear in the preview list
4. **CHECK:** File count shows correct number: "فایل‌های انتخابی (3)"

#### Test C: Remove Files
1. Click the X button on one file
2. **CHECK:** That file is removed from preview
3. **CHECK:** Other files remain
4. Click "پاک کردن همه" (Clear all)
5. **CHECK:** All files are removed
6. **CHECK:** Preview area disappears
7. **CHECK:** Send button becomes disabled (if no message text)

---

### 4. Test File Upload - Mobile

#### Test on Mobile Device or Browser Dev Tools Mobile Mode

**Chrome Mobile Mode:**
1. Press `F12`
2. Click the mobile device icon (top-left)
3. Select a mobile device (iPhone, Samsung, etc.)
4. Refresh page

**Then test:**
1. Click upload button (📎)
2. **CHECK:** File picker opens once
3. Select a file from gallery/camera
4. **CRITICAL CHECK:** File should appear in preview within 1-2 seconds
5. **CHECK:** You can see the file name and size
6. **CHECK:** File doesn't disappear

---

### 5. Test Drag and Drop

1. Drag a file from your desktop
2. Drop it on the message input area
3. **CHECK:** File is added to preview
4. **CHECK:** Same preview behavior as clicking upload button

---

## Expected Console Output (Success)

When everything works correctly, you should see logs like:

```
Initializing MultiFileUploadManager
MultiFileUploadManager initialized: MultiFileUploadManager {selectedFiles: Array(0), ...}
[DEBUG] triggerFileSelect called
[DEBUG] File input element found, triggering click
[DEBUG] handleFileSelect called, event: Event {...}
[DEBUG] Files selected: 1 files
[DEBUG] addFiles called with 1 files
[DEBUG] Processing file: test-image.jpg Type: image/jpeg Size: 245678
[DEBUG] updateFilePreview called. Selected files: 1
[DEBUG] Preview elements found. Updating display...
[DEBUG] Showing preview container with 1 files
updateSendButtonState - hasMessage: false, hasFiles: true
Send button disabled: false
```

---

## Troubleshooting

### Problem: File picker opens twice
**Status:** Should be FIXED ✅
**If still happening:**
- Clear browser cache completely
- Check console for duplicate "[DEBUG] triggerFileSelect called" messages
- Verify main.js doesn't have duplicate handler

### Problem: Files don't appear in preview after selection
**Possible Causes:**

1. **Mobile browser delay issue**
   - **Status:** Should be FIXED ✅
   - The 100ms delay should solve this
   - Check console for "[DEBUG] Files selected: 0 files" → means files were cleared too early

2. **Elements not found**
   - Check console for "Preview elements are no longer valid"
   - Verify HTML has these IDs:
     - `files-preview`
     - `files-list`
     - `files-count`

3. **JavaScript error**
   - Check console for red error messages
   - If you see errors, copy and share them

### Problem: Console shows "No files were selected"
**Cause:** User clicked "Cancel" in file picker
**Solution:** This is normal behavior - try selecting files again

### Problem: Preview shows but files disappear on mobile
**Status:** Should be FIXED ✅
**If still happening:**
- Verify the setTimeout delay is present in multifileupload.js
- Check if delay is 100ms (not 0 or removed)

---

## Verify Fixes Are Applied

### Check 1: Verify main.js fix
Run this in terminal:
```bash
grep -A2 "NOTE: File upload button handler" static/chatbot/js/main.js
```

**Should show:**
```javascript
// NOTE: File upload button handler is now in multifileupload.js to prevent duplicate handlers
// This prevents the file picker from opening twice
```

### Check 2: Verify multifileupload.js fix
Run this in terminal:
```bash
grep -A3 "Delay clearing to ensure mobile" static/chatbot/js/multifileupload.js
```

**Should show:**
```javascript
// Delay clearing to ensure mobile browsers process files properly
setTimeout(() => {
    event.target.value = '';
}, 100);
```

---

## File Type Support

### Supported File Types:
✅ Images: JPEG, PNG, GIF, WebP
✅ Documents: PDF
✅ Text: TXT, CSV
✅ Office: DOC, DOCX, XLS, XLSX

### File Size Limits:
- Maximum: 10 MB per file
- Maximum files: 10 files at once

### Test Different File Types:
1. Upload an image → Should show image icon
2. Upload a PDF → Should show PDF icon (red)
3. Upload a text file → Should show text icon (blue)
4. Upload a Word doc → Should show Word icon (blue)
5. Upload an Excel file → Should show Excel icon (green)

---

## Performance Check

### Expected Load Times:
- Small files (< 1 MB): Instant preview (< 100ms)
- Medium files (1-5 MB): Preview in < 500ms
- Large files (5-10 MB): Preview in < 1 second

### Mobile Performance:
- Should be same as desktop
- If slower, the 100ms delay ensures files still appear

---

## What to Report

If you find issues, please provide:

1. **Browser & Version:**
   - Example: Chrome 120, Firefox 121, Safari 17, etc.

2. **Device:**
   - Desktop Windows/Mac/Linux
   - Mobile: iPhone 14, Samsung Galaxy S23, etc.

3. **Console Logs:**
   - Copy all [DEBUG] messages
   - Copy any red error messages

4. **Specific Steps:**
   - What did you click?
   - What file did you select?
   - What happened vs. what you expected?

5. **Screenshots:**
   - Screenshot of the issue
   - Screenshot of console logs

---

## Success Criteria

✅ File picker opens only once (not twice)
✅ Files appear in preview immediately after selection
✅ Files work on mobile devices (iOS, Android)
✅ Multiple files can be selected
✅ Files can be removed individually
✅ "Clear all" button works
✅ Drag and drop works
✅ Send button enables/disables correctly
✅ No JavaScript errors in console
✅ All other site features still work

---

## Quick Checklist

- [ ] Cleared browser cache
- [ ] Opened developer console (F12)
- [ ] Clicked upload button - opens once only
- [ ] Selected single file - appears in preview
- [ ] Selected multiple files - all appear
- [ ] Removed individual file - works
- [ ] Cleared all files - works
- [ ] Tested on mobile (or mobile mode)
- [ ] Files appear on mobile after selection
- [ ] Drag and drop works
- [ ] No errors in console
- [ ] Send button enables when files selected

---

## Additional Notes

### Debug Logging
The code now includes extensive debug logging prefixed with `[DEBUG]`. This helps diagnose issues without affecting functionality.

**To disable debug logs later:**
In browser console, run:
```javascript
console.defaultLog = console.log.bind(console);
console.log = function(){
    if (arguments[0] && !arguments[0].startsWith('[DEBUG]')) {
        console.defaultLog.apply(console, arguments);
    }
}
```

### Known Limitations
- Maximum 10 files at once
- Maximum 10 MB per file
- Only supported file types accepted

---

**Last Updated:** 2024
**Status:** Ready for Testing ✅
**Critical Fixes Applied:** 
- ✅ Duplicate handler removed
- ✅ Mobile delay added
- ✅ Debug logging enabled

**Test now and report any issues!**