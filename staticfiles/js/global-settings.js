/**
 * Global File Upload Settings Handler
 * Manages display and validation of file uploads based on global settings
 */

class GlobalFileSettings {
    constructor() {
        this.settings = null;
        this.loadSettings();
    }

    /**
     * Load global file settings from server
     */
    async loadSettings() {
        try {
            const response = await fetch('/api/global-settings/');
            if (response.ok) {
                this.settings = await response.json();
                this.updateUI();
            } else {
                console.error('Failed to load global settings');
            }
        } catch (error) {
            console.error('Error loading global settings:', error);
            // Set default fallback settings
            this.settings = {
                max_file_size_mb: 10,
                max_files_per_message: 5,
                allowed_extensions: ['txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'webp']
            };
            this.updateUI();
        }
    }

    /**
     * Update UI elements with current settings
     */
    updateUI() {
        if (!this.settings) return;

        // Update file input accept attribute
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            const acceptString = this.settings.allowed_extensions
                .map(ext => `.${ext}`)
                .join(',');
            input.setAttribute('accept', acceptString);
            input.setAttribute('multiple', 'true');
        });

        // Update help text or info displays
        this.updateHelpTexts();
    }

    /**
     * Update help texts and info displays
     */
    updateHelpTexts() {
        const helpElements = document.querySelectorAll('.file-upload-help');
        helpElements.forEach(element => {
            element.innerHTML = `
                <div class="upload-limits">
                    <p><strong>محدودیت‌های آپلود فایل:</strong></p>
                    <ul>
                        <li>حداکثر حجم فایل: ${this.settings.max_file_size_mb} مگابایت</li>
                        <li>حداکثر تعداد فایل در هر پیام: ${this.settings.max_files_per_message} عدد</li>
                        <li>فرمت‌های مجاز: ${this.settings.allowed_extensions.join(', ')}</li>
                    </ul>
                </div>
            `;
        });
    }

    /**
     * Validate files before upload
     * @param {FileList} files - Files to validate
     * @returns {Object} - Validation result
     */
    validateFiles(files) {
        if (!this.settings) {
            return { valid: false, message: 'تنظیمات سیستم در حال بارگذاری است. لطفا کمی صبر کنید.' };
        }

        if (!files || files.length === 0) {
            return { valid: true, message: '' };
        }

        // Check number of files
        if (files.length > this.settings.max_files_per_message) {
            return {
                valid: false,
                message: `تعداد فایل‌ها (${files.length}) بیشتر از حد مجاز (${this.settings.max_files_per_message}) است`
            };
        }

        // Check each file
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Check file size
            const maxSizeBytes = this.settings.max_file_size_mb * 1024 * 1024;
            if (file.size > maxSizeBytes) {
                const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                return {
                    valid: false,
                    message: `فایل ${file.name}: حجم (${fileSizeMB} MB) بیشتر از حد مجاز (${this.settings.max_file_size_mb} MB) است`
                };
            }

            // Check file extension
            const fileExtension = file.name.split('.').pop().toLowerCase();
            if (fileExtension && !this.settings.allowed_extensions.includes(fileExtension)) {
                return {
                    valid: false,
                    message: `فایل ${file.name}: فرمت .${fileExtension} مجاز نیست. فرمت‌های مجاز: ${this.settings.allowed_extensions.join(', ')}`
                };
            }
        }

        return { valid: true, message: '' };
    }

    /**
     * Display validation error
     * @param {string} message - Error message
     */
    showError(message) {
        // Remove existing errors
        const existingErrors = document.querySelectorAll('.file-upload-error');
        existingErrors.forEach(error => error.remove());

        // Create error element
        const errorElement = document.createElement('div');
        errorElement.className = 'file-upload-error alert alert-danger';
        errorElement.innerHTML = `<strong>خطا:</strong> ${message}`;

        // Find file input and add error after it
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput && fileInput.parentNode) {
            fileInput.parentNode.insertBefore(errorElement, fileInput.nextSibling);
        }

        // Auto-hide error after 5 seconds
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.parentNode.removeChild(errorElement);
            }
        }, 5000);
    }

    /**
     * Clear validation errors
     */
    clearErrors() {
        const existingErrors = document.querySelectorAll('.file-upload-error');
        existingErrors.forEach(error => error.remove());
    }
}

// Initialize global settings when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.globalFileSettings = new GlobalFileSettings();

    // Add validation to file inputs
    document.addEventListener('change', function(event) {
        if (event.target.type === 'file' && window.globalFileSettings) {
            const validation = window.globalFileSettings.validateFiles(event.target.files);
            
            if (!validation.valid) {
                window.globalFileSettings.showError(validation.message);
                event.target.value = ''; // Clear the invalid selection
            } else {
                window.globalFileSettings.clearErrors();
            }
        }
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GlobalFileSettings;
}