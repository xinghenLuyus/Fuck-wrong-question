// 通用工具函数
class Utils {
    // API 请求封装
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || '请求失败');
            }
            
            return data;
        } catch (error) {
            console.error('API 请求错误:', error);
            throw error;
        }
    }

    // GET 请求
    static async get(url) {
        return this.request(url);
    }

    // POST 请求
    static async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // PUT 请求
    static async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // DELETE 请求
    static async delete(url) {
        return this.request(url, {
            method: 'DELETE',
        });
    }

    // 文件上传
    static async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上传失败');
        }
        
        return response.json();
    }

    // 显示消息
    static showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        // 插入到页面顶部
        const container = document.querySelector('.container');
        container.insertBefore(messageDiv, container.firstChild);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }

    // 显示成功消息
    static showSuccess(message) {
        this.showMessage(message, 'success');
    }

    // 显示错误消息
    static showError(message) {
        this.showMessage(message, 'error');
    }

    // 显示加载状态
    static showLoading(element) {
        const originalText = element.textContent;
        element.innerHTML = '<span class="loading"></span> 加载中...';
        element.disabled = true;
        
        return () => {
            element.textContent = originalText;
            element.disabled = false;
        };
    }

    // 格式化日期
    static formatDate(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleString('zh-CN');
    }

    // 确认对话框
    static confirm(message) {
        return confirm(message);
    }

    // 防抖函数
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 获取URL参数
    static getUrlParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    // 重定向
    static redirect(url) {
        window.location.href = url;
    }

    // 图片预览
    static previewImage(file, callback) {
        if (!file.type.startsWith('image/')) {
            throw new Error('不是有效的图片文件');
        }
        
        const reader = new FileReader();
        reader.onload = (e) => callback(e.target.result);
        reader.readAsDataURL(file);
    }

    // 下载文件
    static downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 图片上传组件
class ImageUploader {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            multiple: true,
            maxFiles: 10,
            enableClipboard: true,  // 启用剪切板功能
            enableTextInput: false, // 是否启用文字输入
            ...options
        };
        this.files = [];
        this.textContent = "";
        this.init();
    }

    init() {
        this.createUploadArea();
        this.createPreviewArea();
        if (this.options.enableTextInput) {
            this.createTextInput();
        }
        this.bindEvents();
    }

    createTextInput() {
        this.textInputArea = document.createElement('div');
        this.textInputArea.className = 'text-input-area';
        this.textInputArea.innerHTML = `
            <label class="form-label">题目文字内容（可选）</label>
            <textarea class="form-textarea" placeholder="请输入题目文字内容..." rows="3"></textarea>
        `;
        this.container.insertBefore(this.textInputArea, this.container.firstChild);
        
        this.textInput = this.textInputArea.querySelector('textarea');
        this.textInput.addEventListener('input', (e) => {
            this.textContent = e.target.value;
            if (this.options.onTextChange) {
                this.options.onTextChange(this.textContent);
            }
        });
    }

    createUploadArea() {
        this.uploadArea = document.createElement('div');
        this.uploadArea.className = 'upload-area';
        
        let uploadText = '点击或拖拽上传图片';
        if (this.options.enableClipboard) {
            uploadText += '<br><small>支持 Ctrl+V 粘贴剪切板图片</small>';
        }
        
        this.uploadArea.innerHTML = `
            <div class="upload-icon">📷</div>
            <div class="upload-text">${uploadText}</div>
            <input type="file" accept="image/*" ${this.options.multiple ? 'multiple' : ''} style="display: none;">
        `;
        this.container.appendChild(this.uploadArea);
        
        this.fileInput = this.uploadArea.querySelector('input[type="file"]');
    }

    createPreviewArea() {
        this.previewArea = document.createElement('div');
        this.previewArea.className = 'image-preview';
        this.container.appendChild(this.previewArea);
    }

    bindEvents() {
        // 点击上传
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // 文件选择
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(Array.from(e.target.files));
        });

        // 拖拽上传
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFiles(Array.from(e.dataTransfer.files));
        });

        // 剪切板支持
        if (this.options.enableClipboard) {
            document.addEventListener('paste', (e) => {
                if (document.activeElement && 
                    (this.container.contains(document.activeElement) || 
                     document.activeElement === this.uploadArea)) {
                    this.handleClipboardPaste(e);
                }
            });
            
            // 使上传区域可以获取焦点
            this.uploadArea.setAttribute('tabindex', '0');
            this.uploadArea.addEventListener('focus', () => {
                this.uploadArea.style.outline = '2px solid #3498db';
            });
            this.uploadArea.addEventListener('blur', () => {
                this.uploadArea.style.outline = 'none';
            });
        }
    }

    // 处理剪切板粘贴
    handleClipboardPaste(e) {
        const items = e.clipboardData.items;
        const files = [];
        
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                files.push(file);
            }
        }
        
        if (files.length > 0) {
            e.preventDefault();
            this.handleFiles(files);
            Utils.showSuccess(`从剪切板添加了 ${files.length} 张图片`);
        }
    }

    async handleFiles(newFiles) {
        const imageFiles = newFiles.filter(file => file.type.startsWith('image/'));
        
        if (imageFiles.length === 0) {
            Utils.showError('请选择图片文件');
            return;
        }

        if (this.files.length + imageFiles.length > this.options.maxFiles) {
            Utils.showError(`最多只能上传 ${this.options.maxFiles} 张图片`);
            return;
        }

        for (const file of imageFiles) {
            try {
                const result = await Utils.uploadFile(file);
                this.files.push(result);
                this.addPreview(result);
            } catch (error) {
                Utils.showError(`上传失败: ${file.name}`);
            }
        }

        // 触发变化事件
        if (this.options.onChange) {
            this.options.onChange(this.files);
        }
    }

    addPreview(fileData, isExisting = false) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item';
        
        const deleteButtonText = isExisting ? '×' : '×';
        const imageClass = isExisting ? 'preview-image existing' : 'preview-image';
        
        previewItem.innerHTML = `
            <img src="${fileData.url}" alt="${fileData.filename}" class="${imageClass}">
            <button type="button" class="preview-remove" data-filename="${fileData.filename}">${deleteButtonText}</button>
        `;

        const removeBtn = previewItem.querySelector('.preview-remove');
        removeBtn.addEventListener('click', () => {
            this.removeFile(fileData.filename);
            previewItem.remove();
        });

        this.previewArea.appendChild(previewItem);
    }

    removeFile(filename) {
        this.files = this.files.filter(file => file.filename !== filename);
        if (this.options.onChange) {
            this.options.onChange(this.files);
        }
    }

    getFiles() {
        return this.files;
    }

    getUrls() {
        return this.files.map(file => file.url).join(',');
    }

    clear() {
        this.files = [];
        this.textContent = "";
        if (this.textInput) {
            this.textInput.value = "";
        }
        this.previewArea.innerHTML = '';
        if (this.options.onChange) {
            this.options.onChange(this.files);
        }
    }

    getTextContent() {
        return this.textContent;
    }

    setTextContent(text) {
        this.textContent = text;
        if (this.textInput) {
            this.textInput.value = text;
        }
    }

    // 从既有图片URL加载（编辑模式）
    loadExistingImages(imageUrls, textContent = '') {
        this.clear();
        
        if (textContent) {
            this.setTextContent(textContent);
        }
        
        if (imageUrls) {
            const urls = imageUrls.split(',').filter(url => url.trim());
            urls.forEach((url, index) => {
                const fileData = {
                    filename: `existing_image_${index}.jpg`,
                    url: url.trim()
                };
                this.files.push(fileData);
                this.addPreview(fileData, true); // true 表示是既有图片
            });
        }
        
        if (this.options.onChange) {
            this.options.onChange(this.files);
        }
    }
}

// 学生选择器组件
class StudentSelector {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            multiple: true,
            searchable: true,
            ...options
        };
        this.students = [];
        this.selectedStudents = [];
        this.init();
    }

    async init() {
        await this.loadStudents();
        this.render();
        this.bindEvents();
    }

    async loadStudents() {
        try {
            this.students = await Utils.get('/api/students/');
        } catch (error) {
            Utils.showError('加载学生列表失败');
        }
    }

    render() {
        let html = '';
        
        if (this.options.searchable) {
            html += `
                <div class="form-group">
                    <input type="text" class="form-input" placeholder="搜索学生姓名或学号..." id="student-search">
                </div>
            `;
        }

        html += '<div class="student-selector">';
        
        this.students.forEach(student => {
            const isSelected = this.selectedStudents.includes(student.id);
            html += `
                <div class="student-item" data-student-id="${student.id}">
                    <input type="${this.options.multiple ? 'checkbox' : 'radio'}" 
                           class="student-checkbox" 
                           value="${student.id}" 
                           ${isSelected ? 'checked' : ''}>
                    <span>${student.name} (${student.student_no})</span>
                </div>
            `;
        });
        
        html += '</div>';
        this.container.innerHTML = html;
    }

    bindEvents() {
        if (this.options.searchable) {
            const searchInput = this.container.querySelector('#student-search');
            searchInput.addEventListener('input', Utils.debounce((e) => {
                this.filterStudents(e.target.value);
            }, 300));
        }

        this.container.addEventListener('change', (e) => {
            if (e.target.classList.contains('student-checkbox')) {
                const studentId = parseInt(e.target.value);
                
                if (this.options.multiple) {
                    if (e.target.checked) {
                        this.selectedStudents.push(studentId);
                    } else {
                        this.selectedStudents = this.selectedStudents.filter(id => id !== studentId);
                    }
                } else {
                    this.selectedStudents = e.target.checked ? [studentId] : [];
                }

                if (this.options.onChange) {
                    this.options.onChange(this.selectedStudents);
                }
            }
        });
    }

    filterStudents(searchTerm) {
        const studentItems = this.container.querySelectorAll('.student-item');
        studentItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            item.style.display = matches ? 'flex' : 'none';
        });
    }

    getSelectedStudents() {
        return this.selectedStudents;
    }

    setSelectedStudents(studentIds) {
        this.selectedStudents = studentIds;
        this.render();
    }

    getSelectedStudentsString() {
        return this.selectedStudents.join(',');
    }
}