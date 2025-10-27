#!/bin/bash

echo "======================================"
echo "File Upload Fix Verification Script"
echo "======================================"
echo ""

echo "1. Checking for JavaScript syntax errors..."
node --check static/chatbot/js/main.js 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ main.js - No syntax errors"
else
    echo "   ✗ main.js - HAS ERRORS!"
fi

node --check static/chatbot/js/multifileupload.js 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ multifileupload.js - No syntax errors"
else
    echo "   ✗ multifileupload.js - HAS ERRORS!"
fi

echo ""
echo "2. Checking Fix #1: Duplicate handler removed from main.js..."
if grep -q "NOTE: File upload button handler is now in multifileupload.js" static/chatbot/js/main.js; then
    echo "   ✓ Comment found - duplicate handler removed"
else
    echo "   ✗ Comment NOT found - fix may not be applied"
fi

echo ""
echo "3. Checking Fix #2: Mobile delay added to multifileupload.js..."
if grep -q "Delay clearing to ensure mobile browsers process files properly" static/chatbot/js/multifileupload.js; then
    echo "   ✓ Mobile delay fix applied"
else
    echo "   ✗ Mobile delay fix NOT found"
fi

echo ""
echo "4. Checking debug logging..."
if grep -q "\[DEBUG\]" static/chatbot/js/multifileupload.js; then
    echo "   ✓ Debug logging enabled"
else
    echo "   ℹ Debug logging not enabled (optional)"
fi

echo ""
echo "5. Checking HTML elements..."
if grep -q 'id="files-preview"' templates/chatbot/chat.html; then
    echo "   ✓ files-preview element exists"
else
    echo "   ✗ files-preview element NOT found"
fi

if grep -q 'id="files-list"' templates/chatbot/chat.html; then
    echo "   ✓ files-list element exists"
else
    echo "   ✗ files-list element NOT found"
fi

if grep -q 'id="file-input"' templates/chatbot/chat.html; then
    echo "   ✓ file-input element exists"
else
    echo "   ✗ file-input element NOT found"
fi

echo ""
echo "6. Checking initialization..."
if grep -q "initializeMultiFileUpload()" static/chatbot/js/main.js; then
    echo "   ✓ MultiFileUploadManager initialization found"
else
    echo "   ✗ Initialization NOT found"
fi

echo ""
echo "======================================"
echo "Verification Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Clear browser cache (Ctrl+F5)"
echo "2. Open developer console (F12)"
echo "3. Test file upload"
echo "4. Check console for [DEBUG] messages"
echo ""
echo "See FILE_UPLOAD_TEST_GUIDE.md for detailed testing instructions"
echo ""
