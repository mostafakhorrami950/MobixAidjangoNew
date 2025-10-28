// =================================
// مدیریت آپلود چند فایل - ویژگی جدید
// Multiple File Upload Management - New Feature  
// =================================

/**
 * سیستم جدید مدیریت آپلود فایل‌های چت
 * New Chat File Upload Management System
 */
class ChatFileUploadManager {
    constructor() {
        // تنظیمات فایل
        this.uploadedFiles = [];
        this.maxFileSize = 10 * 1024 * 1024; // 10 مگابایت
        this.maxFileCount = 10;
        this.supportedFileTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf',
            'text/plain', 'text/csv',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        
        // عناصر رابط کاربری
        this.uiElements = {
            uploadButton: null,
            fileInput: null,
            clearButton: null,
            previewContainer: null,
            fileList: null,
            fileCounter: null,
            sendButton: null,
            messageInput: null
        };
        
        // راه‌اندازی سیستم
        this.initializeSystem();
        setTimeout(() => this.updateSendButtonStatus(), 100);
    }
    
    /**
     * راه‌اندازی اولیه سیستم آپلود
     * Initialize Upload System
     */
    initializeSystem() {
        this.setupUIElements();
        this.setupEventHandlers();
        this.setupDragAndDrop();
    }
    
    /**
     * تنظیم عناصر رابط کاربری
     * Setup UI Elements
     */
    setupUIElements() {
        this.uiElements = {
            uploadButton: document.getElementById('upload-btn'),
            fileInput: document.getElementById('file-input'),
            clearButton: document.getElementById('clear-all-files'),
            previewContainer: document.getElementById('files-preview'),
            fileList: document.getElementById('files-list'),
            fileCounter: document.getElementById('files-count'),
            sendButton: document.getElementById('send-button'),
            messageInput: document.getElementById('message-input')
        };
    }
    
    /**
     * تنظیم مدیریت رویدادها
     * Setup Event Handlers
     */
    setupEventHandlers() {
        // رویداد کلیک دکمه آپلود
        if (this.uiElements.uploadButton) {
            this.uiElements.uploadButton.onclick = () => this.openFileSelection();
        }
        
        // رویداد تغییر فایل‌های انتخابی
        if (this.uiElements.fileInput) {
            this.uiElements.fileInput.onchange = (event) => this.processSelectedFiles(event);
        }
        
        // رویداد کلیک دکمه پاک کردن همه
        if (this.uiElements.clearButton) {
            this.uiElements.clearButton.onclick = () => this.removeAllFiles();
        }
        
        // رویداد تغییر متن پیام
        if (this.uiElements.messageInput) {
            this.uiElements.messageInput.oninput = () => this.updateSendButtonStatus();
        }
    }
    
    /**
     * تنظیم قابلیت drag and drop
     * Setup Drag and Drop
     */
    setupDragAndDrop() {
        const dropArea = document.body;
        
        if (!dropArea) return;
        
        // جلوگیری از رفتار پیش‌فرض
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // افکت‌های بصری
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('drag-over');
                this.showDropOverlay();
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('drag-over');
                this.hideDropOverlay();
            }, false);
        });
        
        // مدیریت رها کردن فایل
        dropArea.addEventListener('drop', (event) => {
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                this.addFilesToList(files);
            }
        }, false);
    }
    
    /**
     * جلوگیری از رفتارهای پیش‌فرض مرورگر
     * Prevent Default Browser Behaviors
     */
    preventDefaults(event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    /**
     * نمایش overlay برای drag and drop
     * Show Drop Overlay
     */
    showDropOverlay() {
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
        
        // نمایش overlay
        overlay.style.display = 'flex';
    }
    
    /**
     * پنهان کردن overlay drag and drop
     * Hide Drop Overlay
     */
    hideDropOverlay() {
        const overlay = document.getElementById('drag-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    /**
     * باز کردن دیالوگ انتخاب فایل
     * Open File Selection Dialog
     */
    openFileSelection() {
        if (this.uiElements.fileInput) {
            // ریست کردن input برای امکان انتخاب مجدد همان فایل
            this.uiElements.fileInput.value = '';
            this.uiElements.fileInput.click();
        }
    }
    
    /**
     * پردازش فایل‌های انتخابی
     * Process Selected Files
     */
    processSelectedFiles(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.addFilesToList(files);
        }
    }
    
    /**
     * اضافه کردن فایل‌ها به لیست
     * Add Files to List
     */
    addFilesToList(fileList) {
        const files = Array.from(fileList);
        
        for (const file of files) {
            // بررسی حداکثر تعداد فایل
            if (this.uploadedFiles.length >= this.maxFileCount) {
                this.displayErrorMessage(`حداکثر ${this.maxFileCount} فایل قابل انتخاب است.`);
                break;
            }
            
            // اگر این یک چت‌بات تصویری است و تصویر آپلود می‌شود، راهنمایی نشان بده
            if (file.type.startsWith('image/') && currentSessionId) {
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                if (sessionData.chatbot_type === 'image_editing') {
                    this.showImageMergeHint();
                }
            }
            
            // اعتبارسنجی فایل
            if (!this.validateFile(file)) {
                continue;
            }
            
            // بررسی تکراری بودن فایل
            const isDuplicate = this.uploadedFiles.some(
                existingFile => existingFile.name === file.name && existingFile.size === file.size
            );
            
            if (isDuplicate) {
                this.displayErrorMessage(`فایل "${file.name}" قبلاً انتخاب شده است.`);
                continue;
            }
            
            // اضافه کردن فایل به لیست
            this.uploadedFiles.push(file);
        }
        
        this.updateFilePreview();
        this.updateSendButtonStatus();
    }
    
    /**
     * اعتبارسنجی فایل
     * Validate File
     */
    validateFile(file) {
        // بررسی نوع فایل
        if (!this.supportedFileTypes.includes(file.type)) {
            this.displayErrorMessage(`نوع فایل '${file.type}' پشتیبانی نمی‌شود.`);
            return false;
        }
        
        // بررسی حجم فایل
        if (file.size > this.maxFileSize) {
            const maxSizeMB = this.maxFileSize / (1024 * 1024);
            this.displayErrorMessage(`حجم فایل "${file.name}" نباید از ${maxSizeMB} مگابایت بیشتر باشد.`);
            return false;
        }
        
        return true;
    }
    
    /**
     * بروزرسانی پیشنمایش فایل‌ها
     * Update File Preview
     */
    updateFilePreview() {
        if (!this.uiElements.previewContainer || !this.uiElements.fileList || !this.uiElements.fileCounter) {
            return;
        }
        
        // بروزرسانی تعداد فایل‌ها
        this.uiElements.fileCounter.textContent = this.uploadedFiles.length;
        
        // پاک کردن لیست قبلی
        this.uiElements.fileList.innerHTML = '';
        
        // پنهان کردن اگر فایلی وجود ندارد
        if (this.uploadedFiles.length === 0) {
            this.uiElements.previewContainer.style.display = 'none';
            return;
        }
        
        // نمایش container
        this.uiElements.previewContainer.style.display = 'block';
        
        // اضافه کردن هر فایل به لیست
        this.uploadedFiles.forEach((file, index) => {
            const fileItem = this.createFilePreviewItem(file, index);
            this.uiElements.fileList.appendChild(fileItem);
        });
    }
    
    /**
     * ایجاد آیتم پیشنمایش فایل
     * Create File Preview Item
     */
    createFilePreviewItem(file, index) {
        const item = document.createElement('div');
        item.className = 'file-preview-item';
        item.dataset.fileIndex = index;
        
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';
        
        const icon = document.createElement('i');
        icon.className = this.getFileIconClass(file.type);
        
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
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-sm btn-outline-danger';
        removeButton.innerHTML = '<i class="fas fa-times"></i>';
        removeButton.title = 'حذف فایل';
        removeButton.onclick = () => this.removeFile(index);
        
        fileActions.appendChild(removeButton);
        
        item.appendChild(fileInfo);
        item.appendChild(fileActions);
        
        return item;
    }
    
    /**
     * دریافت کلاس آیکون مناسب برای نوع فایل
     * Get Appropriate Icon Class for File Type
     */
    getFileIconClass(fileType) {
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
     * Format File Size
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
     * Remove a File from List
     */
    removeFile(index) {
        if (index >= 0 && index < this.uploadedFiles.length) {
            this.uploadedFiles.splice(index, 1);
            this.updateFilePreview();
            this.updateSendButtonStatus();
        }
    }
    
    /**
     * حذف همه فایل‌ها
     * Remove All Files
     */
    removeAllFiles() {
        this.uploadedFiles = [];
        this.updateFilePreview();
        this.updateSendButtonStatus();
        
        // پاک کردن input فایل
        if (this.uiElements.fileInput) {
            this.uiElements.fileInput.value = '';
        }
    }
    
    /**
     * بروزرسانی وضعیت دکمه ارسال
     * Update Send Button Status
     */
    updateSendButtonStatus() {
        if (!this.uiElements.sendButton || !this.uiElements.messageInput) {
            return;
        }
        
        const hasMessage = this.uiElements.messageInput.value.trim().length > 0;
        const hasFiles = this.uploadedFiles.length > 0;
        
        this.uiElements.sendButton.disabled = !(hasMessage || hasFiles);
    }
    
    /**
     * نمایش راهنمایی ادغام تصاویر
     * Show Image Merge Hint
     */
    showImageMergeHint() {
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
    
    // --- API عمومی ---
    
    /**
     * دریافت فایل‌های انتخابی
     * Get Selected Files
     */
    getSelectedFiles() {
        return this.uploadedFiles;
    }
    
    /**
     * بررسی وجود فایل
     * Check if Files Exist
     */
    hasFiles() {
        return this.uploadedFiles.length > 0;
    }
    
    /**
     * دریافت تعداد فایل‌ها
     * Get File Count
     */
    getFileCount() {
        return this.uploadedFiles.length;
    }
    
    /**
     * نمایش پیام خطا
     * Display Error Message
     */
    displayErrorMessage(message) {
        alert(message);
        console.error('Chat File Upload Error:', message);
    }
    
    /**
     * پاک کردن کامل
     * Complete Cleanup
     */
    cleanup() {
        this.removeAllFiles();
    }
}

// نمونه سراسری مدیریت آپلود
let chatFileUploadManager = null;

/**
 * راه‌اندازی مدیریت آپلود چند فایل
 * Initialize Multiple File Upload Management
 */
function initializeMultiFileUpload() {
    chatFileUploadManager = new ChatFileUploadManager();
}

/**
 * دریافت فایل‌های انتخابی
 * Get Selected Files
 */
function getSelectedFiles() {
    return chatFileUploadManager ? chatFileUploadManager.getSelectedFiles() : [];
}

/**
 * ریست کردن فایل‌ها
 * Reset Files
 */
function resetFilesState() {
    if (chatFileUploadManager) {
        chatFileUploadManager.cleanup();
    }
}

/**
 * بررسی وجود فایل انتخابی
 * Check Selected Files
 */
function hasSelectedFiles() {
    return chatFileUploadManager ? chatFileUploadManager.hasFiles() : false;
}