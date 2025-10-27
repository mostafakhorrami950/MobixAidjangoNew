// =================================
// مدیریت آپلود چند فایل - ویژگی جدید
// Multiple File Upload Management - New Feature  
// =================================

/**
 * کلاس مدیریت آپلود چند فایل
 * Multiple Files Upload Manager Class
 */
class MultiFileUploadManager {
    constructor() {
        this.selectedFiles = []; // آرای فایل‌های انتخابی
        this.maxFileSize = 10 * 1024 * 1024; // 10 مگابایت
        this.maxFiles = 10; // حداکثر تعداد فایل
        this.allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf',
            'text/plain', 'text/csv',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        
        this.elements = {
            uploadBtn: null,
            fileInput: null,
            clearAllBtn: null,
            preview: null,
            filesList: null,
            filesCount: null,
            sendBtn: null,
            messageInput: null
        };
        
        this.init();
        // بروزرسانی اولیه وضعیت دکمه ارسال
        setTimeout(() => this.updateSendButtonState(), 100);
    }
    
    /**
     * راه‌اندازی اولیه مدیریت فایل
     * Initialize file management
     */
    init() {
        this.cacheElements();
        this.attachEventListeners();
        this.setupDragAndDrop();
    }
    
    /**
     * ذخیره عناصر DOM برای استفاده بعدی
     * Cache DOM elements for later use
     */
    cacheElements() {
        this.elements = {
            uploadBtn: document.getElementById('upload-btn'),
            fileInput: document.getElementById('file-input'),
            clearAllBtn: document.getElementById('clear-all-files'),
            preview: document.getElementById('files-preview'),
            filesList: document.getElementById('files-list'),
            filesCount: document.getElementById('files-count'),
            sendBtn: document.getElementById('send-button'),
            messageInput: document.getElementById('message-input')
        };
    }
    
    /**
     * Refresh cached DOM elements
     * This should be called if DOM elements are replaced
     */
    refreshElements() {
        this.cacheElements();
        // Re-attach event listeners
        this.attachEventListeners();
    }
    
    /**
     * اتصال event listener ها
     * Attach event listeners
     */
    attachEventListeners() {
        // کلیک روی دکمه آپلود
        if (this.elements.uploadBtn && document.contains(this.elements.uploadBtn)) {
            // Remove any existing listeners to prevent duplicates
            this.elements.uploadBtn.removeEventListener('click', this.triggerFileSelect);
            this.elements.uploadBtn.addEventListener('click', () => this.triggerFileSelect());
        }
        
        // تغییر فایل‌های انتخابی
        if (this.elements.fileInput && document.contains(this.elements.fileInput)) {
            // Remove any existing listeners to prevent duplicates
            this.elements.fileInput.removeEventListener('change', this.handleFileSelect);
            this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // پاک کردن همه فایل‌ها
        if (this.elements.clearAllBtn && document.contains(this.elements.clearAllBtn)) {
            // Remove any existing listeners to prevent duplicates
            this.elements.clearAllBtn.removeEventListener('click', this.clearAllFiles);
            this.elements.clearAllBtn.addEventListener('click', () => this.clearAllFiles());
        }
        
        // تغییر متن پیام
        if (this.elements.messageInput && document.contains(this.elements.messageInput)) {
            // Remove any existing listeners to prevent duplicates
            this.elements.messageInput.removeEventListener('input', this.updateSendButtonState);
            this.elements.messageInput.addEventListener('input', () => this.updateSendButtonState());
        }
    }
    
    /**
     * راه‌اندازی drag and drop
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        // Set up drag and drop for the entire page
        const dropZones = [document.body, this.elements.messageInput].filter(Boolean);
        
        dropZones.forEach(dropZone => {
            // جلوگیری از رفتار پیش‌فرض مرورگر
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, this.preventDefaults, false);
            });
            
            // اضافه کردن کلاس های بصری
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    this.highlight(dropZone);
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    // Only unhighlight if we're really leaving the drop zone
                    if (eventName === 'dragleave' && this.isLeavingDropZone(e, dropZone)) {
                        this.unhighlight(dropZone);
                    } else if (eventName === 'drop') {
                        this.unhighlight(dropZone);
                    }
                }, false);
            });
            
            // مدیریت drop
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.unhighlight(dropZone);
                this.handleDrop(e);
            }, false);
        });
        
        // Create drag overlay for better visual feedback
        this.createDragOverlay();
    }
    
    /**
     * جلوگیری از رفتار پیش‌فرض
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    /**
     * هایلایت کردن منطقه drop
     */
    highlight(element) {
        element.classList.add('drag-over');
        
        // Show drag overlay for body element
        if (element === document.body) {
            this.showDragOverlay();
        }
    }
    
    /**
     * حذف هایلایت از منطقه drop
     */
    unhighlight(element) {
        element.classList.remove('drag-over');
        
        // Hide drag overlay for body element
        if (element === document.body) {
            this.hideDragOverlay();
        }
    }
    
    /**
     * Check if we're really leaving the drop zone (not just entering a child)
     */
    isLeavingDropZone(e, dropZone) {
        if (!e.relatedTarget) return true;
        return !dropZone.contains(e.relatedTarget);
    }
    
    /**
     * Create drag overlay for better visual feedback
     */
    createDragOverlay() {
        if (document.getElementById('drag-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.id = 'drag-overlay';
        overlay.innerHTML = `
            <div class="drag-overlay-content">
                <i class="fas fa-cloud-upload-alt"></i>
                <h3>فایل‌ها را اینجا رها کنید</h3>
                <p>برای آپلود فایل‌ها</p>
            </div>
        `;
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(37, 99, 235, 0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
            color: white;
            text-align: center;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            #drag-overlay .drag-overlay-content {
                pointer-events: none;
                animation: dragPulse 1.5s ease-in-out infinite;
            }
            
            #drag-overlay .drag-overlay-content i {
                font-size: 4rem;
                margin-bottom: 1rem;
                display: block;
            }
            
            #drag-overlay .drag-overlay-content h3 {
                font-size: 2rem;
                margin-bottom: 0.5rem;
                font-weight: bold;
            }
            
            #drag-overlay .drag-overlay-content p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            @keyframes dragPulse {
                0%, 100% { transform: scale(1); opacity: 0.8; }
                50% { transform: scale(1.05); opacity: 1; }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(overlay);
    }
    
    /**
     * Show drag overlay
     */
    showDragOverlay() {
        const overlay = document.getElementById('drag-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    /**
     * Hide drag overlay
     */
    hideDragOverlay() {
        const overlay = document.getElementById('drag-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    /**
     * مدیریت drop فایل
     */
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = Array.from(dt.files);
        
        if (files.length > 0) {
            this.addFiles(files);
        }
    }
    
    /**
     * باز کردن دیالوگ انتخاب فایل
     * Open file selection dialog
     */
    triggerFileSelect() {
        // Check if the file input element is still valid
        if (this.elements.fileInput && document.contains(this.elements.fileInput)) {
            this.elements.fileInput.click();
        } else {
            console.warn('File input element is no longer valid, refreshing elements');
            this.refreshElements();
            // Try again after refreshing
            if (this.elements.fileInput) {
                this.elements.fileInput.click();
            }
        }
    }
    
    /**
     * مدیریت انتخاب چندین فایل از input
     * Handle multiple files selection from input
     */
    handleFileSelect(event) {
        // Check if the event target is still valid
        if (!event.target || !document.contains(event.target)) {
            console.warn('File input element is no longer valid, refreshing elements');
            this.refreshElements();
            return;
        }
        
        const files = Array.from(event.target.files);
        if (files.length > 0) {
            this.addFiles(files);
        }
        // پاک کردن input برای امکان انتخاب مجدد همان فایل‌ها
        event.target.value = '';
    }
    
    /**
     * اضافه کردن چندین فایل به لیست
     * Add multiple files to the list
     */
    addFiles(files) {
        for (const file of files) {
            // بررسی حداکثر تعداد فایل
            if (this.selectedFiles.length >= this.maxFiles) {
                this.showError(`حداکثر ${this.maxFiles} فایل قابل انتخاب است.`);
                break;
            }
            
            // اگر این یک چت‌بات تصویری است و تصویر آپلود می‌شود، راهنمایی نشان بده
            if (file.type.startsWith('image/') && currentSessionId) {
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                if (sessionData.chatbot_type === 'image_editing') {
                    this.showImageMergingTip();
                }
            }
            
            // اعتبارسنجی فایل
            if (!this.validateFile(file)) {
                continue;
            }
            
            // بررسی تکراری بودن فایل
            const isDuplicate = this.selectedFiles.some(
                existingFile => existingFile.name === file.name && existingFile.size === file.size
            );
            
            if (isDuplicate) {
                this.showError(`فایل "${file.name}" قبلاً انتخاب شده است.`);
                continue;
            }
            
            // اضافه کردن فایل به لیست
            this.selectedFiles.push(file);
        }
        
        this.updateFilePreview();
        this.updateSendButtonState();
    }
    
    /**
     * اعتبارسنجی فایل
     * Validate file
     */
    validateFile(file) {
        // بررسی نوع فایل
        if (!this.allowedTypes.includes(file.type)) {
            this.showError(`نوع فایل '${file.type}' پشتیبانی نمی‌شود.`);
            return false;
        }
        
        // بررسی حجم فایل
        if (file.size > this.maxFileSize) {
            const maxSizeMB = this.maxFileSize / (1024 * 1024);
            this.showError(`حجم فایل "${file.name}" نباید از ${maxSizeMB} مگابایت بیشتر باشد.`);
            return false;
        }
        
        return true;
    }
    
    /**
     * بروزرسانی پیشنمایش فایل‌ها
     * Update files preview
     */
    updateFilePreview() {
        // Check if preview elements are still valid
        if (!this.elements.preview || !this.elements.filesList || !this.elements.filesCount ||
            !document.contains(this.elements.preview) || !document.contains(this.elements.filesList) || !document.contains(this.elements.filesCount)) {
            console.warn('Preview elements are no longer valid, refreshing elements');
            this.refreshElements();
            return;
        }
        
        // بروزرسانی تعداد فایل‌ها
        this.elements.filesCount.textContent = this.selectedFiles.length;
        
        // پاک کردن لیست قبلی
        this.elements.filesList.innerHTML = '';
        
        if (this.selectedFiles.length === 0) {
            this.elements.preview.style.display = 'none';
            return;
        }
        
        // نمایش container
        this.elements.preview.style.display = 'block';
        
        // اضافه کردن هر فایل به لیست
        this.selectedFiles.forEach((file, index) => {
            const fileItem = this.createFilePreviewItem(file, index);
            this.elements.filesList.appendChild(fileItem);
        });
    }
    
    /**
     * ایجاد عنصر پیشنمایش فایل
     * Create file preview item
     */
    createFilePreviewItem(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-preview-item';
        fileItem.dataset.fileIndex = index;
        
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';
        
        const icon = document.createElement('i');
        icon.className = this.getFileIcon(file.type);
        
        const fileDetails = document.createElement('div');
        fileDetails.className = 'file-details';
        
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file.name;
        fileName.title = file.name;
        
        const fileSize = document.createElement('div');
        fileSize.className = 'file-size';
        fileSize.textContent = this.formatFileSize(file.size);
        
        fileDetails.appendChild(fileName);
        fileDetails.appendChild(fileSize);
        
        fileInfo.appendChild(icon);
        fileInfo.appendChild(fileDetails);
        
        const fileActions = document.createElement('div');
        fileActions.className = 'file-actions';
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.title = 'حذف فایل';
        removeBtn.onclick = () => this.removeFile(index);
        
        fileActions.appendChild(removeBtn);
        
        fileItem.appendChild(fileInfo);
        fileItem.appendChild(fileActions);
        
        return fileItem;
    }
    
    /**
     * تنظیم آیکون فایل
     * Set file icon
     */
    getFileIcon(fileType) {
        if (fileType.startsWith('image/')) {
            return 'fas fa-file-image text-primary';
        } else if (fileType === 'application/pdf') {
            return 'fas fa-file-pdf text-danger';
        } else if (fileType.startsWith('text/')) {
            return 'fas fa-file-alt text-info';
        } else if (fileType.includes('word')) {
            return 'fas fa-file-word text-primary';
        } else if (fileType.includes('excel') || fileType.includes('sheet')) {
            return 'fas fa-file-excel text-success';
        }
        return 'fas fa-file text-muted';
    }
    
    /**
     * فرمت کردن اندازه فایل
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * حذف یک فایل از لیست
     * Remove a file from the list
     */
    removeFile(index) {
        if (index >= 0 && index < this.selectedFiles.length) {
            this.selectedFiles.splice(index, 1);
            this.updateFilePreview();
            this.updateSendButtonState();
        }
    }
    
    /**
     * پاک کردن همه فایل‌ها
     * Clear all files
     */
    clearAllFiles() {
        this.selectedFiles = [];
        this.updateFilePreview();
        this.updateSendButtonState();
    }
    
    /**
     * به‌روزرسانی وضعیت دکمه ارسال
     * Update send button state
     */
    updateSendButtonState() {
        // Check if send button and message input are still valid
        if (!this.elements.sendBtn || !this.elements.messageInput ||
            !document.contains(this.elements.sendBtn) || !document.contains(this.elements.messageInput)) {
            console.log('Send button or message input not found or no longer valid');
            return;
        }
        
        const hasMessage = this.elements.messageInput.value.trim().length > 0;
        const hasFiles = this.selectedFiles.length > 0;
        
        console.log(`updateSendButtonState - hasMessage: ${hasMessage}, hasFiles: ${hasFiles}`);
        
        const shouldEnable = hasMessage || hasFiles;
        this.elements.sendBtn.disabled = !shouldEnable;
        
        console.log(`Send button disabled: ${this.elements.sendBtn.disabled}`);
    }
    
    /**
     * دریافت فایل‌های انتخابی
     * Get selected files
     */
    getSelectedFiles() {
        return this.selectedFiles;
    }
    
    /**
     * بررسی وجود فایل
     * Check if files exist
     */
    hasFiles() {
        return this.selectedFiles.length > 0;
    }
    
    /**
     * تعداد فایل‌های انتخابی
     * Get selected files count
     */
    getFilesCount() {
        return this.selectedFiles.length;
    }
    
    /**
     * نمایش خطا
     * Show error message
     */
    showError(message) {
        // می‌توانید از toast یا modal برای نمایش خطا استفاده کنید
        alert(message);
        console.error('Multi File Upload Error:', message);
    }
    
    /**
     * نمایش راهنمایی ادغام تصاویر
     * Show image merging tip
     */
    showImageMergingTip() {
        // بررسی اینکه آیا قبلاً نشان داده شده یا نه
        if (sessionStorage.getItem('imageMergingTipShown')) {
            return;
        }
        
        // نمایش راهنمایی در زیر فیلد متن
        const hintElement = document.getElementById('image-merge-hint');
        if (hintElement) {
            hintElement.classList.remove('d-none');
            
            // مخفی کردن بعد از 5 ثانیه
            setTimeout(() => {
                hintElement.classList.add('d-none');
            }, 5000);
        }
        
        // ایجاد نوتیفیکیشن راهنما
        const tip = document.createElement('div');
        tip.className = 'alert alert-info alert-dismissible fade show position-fixed';
        tip.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 350px;';
        tip.innerHTML = `
            <i class="fas fa-lightbulb me-2"></i>
            <strong>نکته:</strong> برای ادغام با تصاویر قبلی، کلمه "ادغام" یا "ترکیب" را در پیام خود بنویسید.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(tip);
        
        // نشان‌دار کردن اینکه نشان داده شده
        sessionStorage.setItem('imageMergingTipShown', 'true');
        
        // حذف خودکار بعد از 10 ثانیه
        setTimeout(() => {
            if (tip.parentNode) {
                tip.remove();
            }
        }, 10000);
    }
    
    /**
     * پاک کردن کامل (برای استفاده بعد از ارسال)
     * Complete cleanup (for use after sending)
     */
    cleanup() {
        this.clearAllFiles();
    }
}

// ایجاد instance سراسری
let multiFileUploadManager = null;

/**
 * راه‌اندازی مدیریت آپلود چند فایل
 * Initialize multiple file upload management
 */
function initializeMultiFileUpload() {
    console.log('Initializing MultiFileUploadManager');
    multiFileUploadManager = new MultiFileUploadManager();
    console.log('MultiFileUploadManager initialized:', multiFileUploadManager);
}

/**
 * دریافت فایل‌های انتخابی (برای استفاده در سایر بخش‌ها)
 * Get selected files (for use in other sections)
 */
function getSelectedFiles() {
    console.log('getSelectedFiles called, multiFileUploadManager:', multiFileUploadManager);
    if (!multiFileUploadManager) {
        console.log('multiFileUploadManager is null, returning empty array');
        return [];
    }
    const files = multiFileUploadManager.getSelectedFiles();
    console.log('getSelectedFiles returning:', files);
    return files;
}

/**
 * ریست کردن فایل‌ها (برای استفاده بعد از ارسال)
 * Reset files (for use after sending)
 */
function resetFilesState() {
    if (multiFileUploadManager) {
        multiFileUploadManager.cleanup();
    }
}

/**
 * بررسی وجود فایل انتخابی
 * Check if any files are selected
 */
function hasSelectedFiles() {
    if (!multiFileUploadManager) {
        return false;
    }
    return multiFileUploadManager.hasFiles();
}

/**
 * Refresh MultiFileUploadManager elements
 * This should be called if DOM elements are replaced
 */
function refreshMultiFileUploadElements() {
    if (multiFileUploadManager) {
        multiFileUploadManager.refreshElements();
    }
}