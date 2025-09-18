// =================================
// مدیریت آپلود فایل - بازنویسی کامل
// File Upload Management - Complete Rewrite
// =================================

/**
 * کلاس مدیریت آپلود فایل
 * File Upload Manager Class
 */
class FileUploadManager {
    constructor() {
        this.currentFile = null;
        this.maxFileSize = 10 * 1024 * 1024; // 10 مگابایت
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
            removeBtn: null,
            preview: null,
            fileName: null,
            fileIcon: null,
            sendBtn: null,
            messageInput: null
        };
        
        this.init();
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
            removeBtn: document.getElementById('remove-file'),
            preview: document.getElementById('file-preview'),
            fileName: document.getElementById('file-name'),
            fileIcon: document.querySelector('#file-preview i'),
            sendBtn: document.getElementById('send-button'),
            messageInput: document.getElementById('message-input')
        };
    }
    
    /**
     * اتصال event listener ها
     * Attach event listeners
     */
    attachEventListeners() {
        // کلیک روی دکمه آپلود
        if (this.elements.uploadBtn) {
            this.elements.uploadBtn.addEventListener('click', () => this.triggerFileSelect());
        }
        
        // تغییر فایل انتخابی
        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // حذف فایل
        if (this.elements.removeBtn) {
            this.elements.removeBtn.addEventListener('click', () => this.removeFile());
        }
        
        // تغییر متن پیام
        if (this.elements.messageInput) {
            this.elements.messageInput.addEventListener('input', () => this.updateSendButtonState());
        }
    }
    
    /**
     * راه‌اندازی drag and drop
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        const dropZone = this.elements.messageInput;
        if (!dropZone) return;
        
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
            dropZone.addEventListener(eventName, () => this.unhighlight(dropZone), false);
        });
        
        // مدیریت drop
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.unhighlight(dropZone);
            this.handleDrop(e);
        }, false);
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
    }
    
    /**
     * حذف هایلایت از منطقه drop
     */
    unhighlight(element) {
        element.classList.remove('drag-over');
    }
    
    /**
     * مدیریت drop فایل
     */
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    /**
     * باز کردن دیالوگ انتخاب فایل
     * Open file selection dialog
     */
    triggerFileSelect() {
        if (this.elements.fileInput) {
            this.elements.fileInput.click();
        }
    }
    
    /**
     * مدیریت انتخاب فایل از input
     * Handle file selection from input
     */
    handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    /**
     * پردازش فایل انتخاب شده
     * Process selected file
     */
    processFile(file) {
        // اعتبارسنجی فایل
        if (!this.validateFile(file)) {
            return;
        }
        
        this.currentFile = file;
        this.displayFilePreview(file);
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
            this.showError(`حجم فایل نباید از ${maxSizeMB} مگابایت بیشتر باشد.`);
            return false;
        }
        
        return true;
    }
    
    /**
     * نمایش پیشنمایش فایل
     * Display file preview
     */
    displayFilePreview(file) {
        if (!this.elements.preview || !this.elements.fileName || !this.elements.fileIcon) {
            return;
        }
        
        // تنظیم نام فایل
        this.elements.fileName.textContent = file.name;
        
        // تنظیم آیکون بر اساس نوع فایل
        this.setFileIcon(file.type);
        
        // اضافه کردن اطلاعات اضافی
        this.addFileInfo(file);
        
        // نمایش پیشنمایش
        this.elements.preview.style.display = 'block';
        
        // انیمیشن نمایش
        this.elements.preview.style.opacity = '0';
        this.elements.preview.style.transform = 'translateY(-10px)';
        
        requestAnimationFrame(() => {
            this.elements.preview.style.transition = 'all 0.3s ease';
            this.elements.preview.style.opacity = '1';
            this.elements.preview.style.transform = 'translateY(0)';
        });
    }
    
    /**
     * تنظیم آیکون فایل
     * Set file icon
     */
    setFileIcon(fileType) {
        let iconClass = 'fas fa-file text-muted me-2';
        
        if (fileType.startsWith('image/')) {
            iconClass = 'fas fa-file-image text-primary me-2';
        } else if (fileType === 'application/pdf') {
            iconClass = 'fas fa-file-pdf text-danger me-2';
        } else if (fileType.startsWith('text/')) {
            iconClass = 'fas fa-file-alt text-info me-2';
        } else if (fileType.includes('word')) {
            iconClass = 'fas fa-file-word text-primary me-2';
        } else if (fileType.includes('excel') || fileType.includes('sheet')) {
            iconClass = 'fas fa-file-excel text-success me-2';
        }
        
        this.elements.fileIcon.className = iconClass;
    }
    
    /**
     * اضافه کردن اطلاعات اضافی فایل
     * Add additional file information
     */
    addFileInfo(file) {
        const fileSizeKB = Math.round(file.size / 1024);
        let sizeText;
        
        if (fileSizeKB < 1024) {
            sizeText = `${fileSizeKB} KB`;
        } else {
            const fileSizeMB = Math.round(fileSizeKB / 1024 * 100) / 100;
            sizeText = `${fileSizeMB} MB`;
        }
        
        // اگر عنصری برای نمایش اندازه فایل وجود دارد
        const sizeElement = document.getElementById('file-size');
        if (sizeElement) {
            sizeElement.textContent = sizeText;
        } else {
            // اضافه کردن اندازه به نام فایل
            this.elements.fileName.textContent = `${file.name} (${sizeText})`;
        }
    }
    
    /**
     * حذف فایل انتخاب شده
     * Remove selected file
     */
    removeFile() {
        // انیمیشن مخفی کردن
        if (this.elements.preview) {
            this.elements.preview.style.transition = 'all 0.3s ease';
            this.elements.preview.style.opacity = '0';
            this.elements.preview.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                this.elements.preview.style.display = 'none';
                this.elements.preview.style.opacity = '';
                this.elements.preview.style.transform = '';
                this.elements.preview.style.transition = '';
            }, 300);
        }
        
        // پاک کردن فایل
        this.currentFile = null;
        
        // ریست کردن input فایل
        this.resetFileInput();
        
        // به‌روزرسانی وضعیت دکمه ارسال
        this.updateSendButtonState();
    }
    
    /**
     * ریست کردن input فایل
     * Reset file input
     */
    resetFileInput() {
        if (this.elements.fileInput) {
            // ایجاد input جدید
            const newInput = document.createElement('input');
            newInput.type = 'file';
            newInput.id = 'file-input';
            newInput.style.display = 'none';
            
            // جایگزینی input قدیمی
            this.elements.fileInput.parentNode.replaceChild(newInput, this.elements.fileInput);
            
            // به‌روزرسانی رفرنس
            this.elements.fileInput = newInput;
            
            // اتصال event listener جدید
            this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }
    
    /**
     * به‌روزرسانی وضعیت دکمه ارسال
     * Update send button state
     */
    updateSendButtonState() {
        if (!this.elements.sendBtn || !this.elements.messageInput) return;
        
        const hasMessage = this.elements.messageInput.value.trim().length > 0;
        const hasFile = this.currentFile !== null;
        
        this.elements.sendBtn.disabled = !(hasMessage || hasFile);
    }
    
    /**
     * دریافت فایل فعلی
     * Get current file
     */
    getCurrentFile() {
        return this.currentFile;
    }
    
    /**
     * بررسی وجود فایل
     * Check if file exists
     */
    hasFile() {
        return this.currentFile !== null;
    }
    
    /**
     * نمایش خطا
     * Show error message
     */
    showError(message) {
        // می‌توانید از toast یا modal برای نمایش خطا استفاده کنید
        alert(message);
        console.error('File Upload Error:', message);
    }
    
    /**
     * پاک کردن کامل (برای استفاده بعد از ارسال)
     * Complete cleanup (for use after sending)
     */
    cleanup() {
        this.removeFile();
    }
}

// ایجاد instance سراسری
let fileUploadManager = null;

/**
 * راه‌اندازی مدیریت آپلود فایل
 * Initialize file upload management
 */
function initializeFileUpload() {
    fileUploadManager = new FileUploadManager();
}

/**
 * دریافت فایل انتخابی (برای استفاده در سایر بخش‌ها)
 * Get selected file (for use in other sections)
 */
function getSelectedFile() {
    if (!fileUploadManager) {
        return null;
    }
    return fileUploadManager.getCurrentFile();
}

/**
 * ریست کردن فایل (برای استفاده بعد از ارسال)
 * Reset file (for use after sending)
 */
function resetFileInputState() {
    if (fileUploadManager) {
        fileUploadManager.cleanup();
    }
}
