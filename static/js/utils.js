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
    static async uploadFile(file, paperId = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (paperId) {
            formData.append('paper_id', paperId);
        }
        
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

    // 显示图片大图模态框（全局静态方法）
    static showImageModal(imageUrl) {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="image-modal-content">
                <span class="image-modal-close">&times;</span>
                <img src="${imageUrl}" class="image-modal-img">
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击关闭按钮关闭模态框
        const closeBtn = modal.querySelector('.image-modal-close');
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        // 点击模态框背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // ESC键关闭
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        
        // 模态框移除时清理事件监听
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node === modal) {
                        document.removeEventListener('keydown', escHandler);
                        observer.disconnect();
                    }
                });
            });
        });
        observer.observe(document.body, { childList: true });
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
            paperId: null,          // 试卷ID，用于按试卷分文件夹存储
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
                const result = await Utils.uploadFile(file, this.options.paperId);
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
        
        const deleteButtonText = '×';
        const imageClass = isExisting ? 'preview-image existing' : 'preview-image';
        
        previewItem.innerHTML = `
            <img src="${fileData.url}" alt="${fileData.filename}" class="${imageClass}">
            <div class="preview-actions">
                <button type="button" class="preview-remove" data-filename="${fileData.filename}" title="删除图片">${deleteButtonText}</button>
            </div>
        `;

        // 图片点击查看大图
        const img = previewItem.querySelector('img');
        img.style.cursor = 'pointer';
        img.addEventListener('click', (e) => {
            // 阻止事件冒泡，避免触发其他事件
            e.stopPropagation();
            this.showImageModal(fileData.url);
        });

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

    // 显示图片大图模态框
    showImageModal(imageUrl) {
        // 调用 Utils 的静态方法
        Utils.showImageModal(imageUrl);
    }

}

// 学生选择器组件（微信标签式）
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
        let html = '<div class="student-selector-wrapper">';
        
        // 已选择的学生标签区域
        html += '<div class="selected-students-area">';
        if (this.selectedStudents.length > 0) {
            this.selectedStudents.forEach(studentId => {
                const student = this.students.find(s => s.id === studentId);
                if (student) {
                    html += `
                        <div class="student-tag" data-student-id="${student.id}">
                            <span class="student-tag-text">${student.name}（${student.class_name}-${student.student_no}）</span>
                            <span class="student-tag-remove" data-student-id="${student.id}">×</span>
                        </div>
                    `;
                }
            });
        } else {
            html += '<div class="no-selection-hint">请选择学生</div>';
        }
        html += '</div>';
        
        // 搜索和筛选区域（先筛选后搜索）
        if (this.options.searchable) {
            html += `
                <div class="student-selector-filters">
                    <select class="filter-select" id="class-filter">
                        <option value="">全部班级</option>
                    </select>
                    <input type="text" 
                           class="filter-input" 
                           id="student-search" 
                           placeholder="搜索姓名、学号或拼音...">
                </div>
            `;
        }

        // 学生列表区域（增加高度）
        html += '<div class="student-list" style="max-height: 400px;">';
        html += '</div>';
        
        html += '</div>';
        this.container.innerHTML = html;
        
        // 填充班级筛选器
        if (this.options.searchable) {
            this.renderClassFilter();
        }
        
        // 渲染学生列表
        this.renderStudentList();
    }

    renderClassFilter() {
        const classFilter = this.container.querySelector('#class-filter');
        if (!classFilter) return;
        
        // 获取所有唯一的班级
        const classes = [...new Set(this.students.map(s => s.class_name))].sort();
        
        classes.forEach(className => {
            const option = document.createElement('option');
            option.value = className;
            option.textContent = className;
            classFilter.appendChild(option);
        });
    }

    renderStudentList(filteredStudents = null) {
        const studentList = this.container.querySelector('.student-list');
        if (!studentList) return;
        
        const studentsToShow = filteredStudents || this.students;
        
        let html = '';
        studentsToShow.forEach(student => {
            const isSelected = this.selectedStudents.includes(student.id);
            html += `
                <div class="student-list-item ${isSelected ? 'selected' : ''}" data-student-id="${student.id}">
                    <input type="${this.options.multiple ? 'checkbox' : 'radio'}" 
                           class="student-checkbox" 
                           value="${student.id}" 
                           ${isSelected ? 'checked' : ''}>
                    <span class="student-info">
                        <span class="student-name">${student.name}</span>
                        <span class="student-details">（${student.class_name}-${student.student_no}）</span>
                    </span>
                </div>
            `;
        });
        
        if (html === '') {
            html = '<div class="no-students-hint">没有找到匹配的学生</div>';
        }
        
        studentList.innerHTML = html;
    }

    bindEvents() {
        // 移除已选学生标签
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('student-tag-remove')) {
                const studentId = parseInt(e.target.dataset.studentId);
                this.removeSelectedStudent(studentId);
                return;
            }
            
            // 点击整行选中学生（优化体验）
            const listItem = e.target.closest('.student-list-item');
            if (listItem && !e.target.classList.contains('student-checkbox')) {
                const checkbox = listItem.querySelector('.student-checkbox');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    // 触发 change 事件
                    const event = new Event('change', { bubbles: true });
                    checkbox.dispatchEvent(event);
                }
            }
        });

        // 选择/取消选择学生
        this.container.addEventListener('change', (e) => {
            if (e.target.classList.contains('student-checkbox')) {
                const studentId = parseInt(e.target.value);
                
                if (this.options.multiple) {
                    if (e.target.checked) {
                        this.addSelectedStudent(studentId);
                    } else {
                        this.removeSelectedStudent(studentId);
                    }
                } else {
                    this.selectedStudents = e.target.checked ? [studentId] : [];
                    this.render();
                }

                if (this.options.onChange) {
                    this.options.onChange(this.selectedStudents);
                }
            }
        });

        // 搜索功能
        const searchInput = this.container.querySelector('#student-search');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce((e) => {
                this.filterStudents();
            }, 300));
        }

        // 班级筛选功能
        const classFilter = this.container.querySelector('#class-filter');
        if (classFilter) {
            classFilter.addEventListener('change', () => {
                this.filterStudents();
            });
        }
    }

    filterStudents() {
        const searchTerm = this.container.querySelector('#student-search')?.value.toLowerCase() || '';
        const selectedClass = this.container.querySelector('#class-filter')?.value || '';
        
        let filtered = this.students.filter(student => {
            let matchesSearch = !searchTerm;
            
            if (searchTerm) {
                // 原字符匹配
                if (student.name.toLowerCase().includes(searchTerm) ||
                    student.student_no.toLowerCase().includes(searchTerm) ||
                    student.class_name.toLowerCase().includes(searchTerm)) {
                    matchesSearch = true;
                } else if (window.pinyinPro) {
                    // 拼音匹配
                    try {
                        const { pinyin } = window.pinyinPro;
                        
                        // 姓名全拼匹配
                        const namePinyin = pinyin(student.name, { toneType: 'none' }).replace(/\s+/g, '').toLowerCase();
                        if (namePinyin.includes(searchTerm)) {
                            matchesSearch = true;
                        } else {
                            // 姓名首字母匹配
                            const nameFirst = pinyin(student.name, { pattern: 'first', toneType: 'none' }).replace(/\s+/g, '').toLowerCase();
                            if (nameFirst.includes(searchTerm)) {
                                matchesSearch = true;
                            }
                        }
                    } catch (e) {
                        console.warn('拼音转换失败:', e);
                    }
                }
            }
            
            const matchesClass = !selectedClass || student.class_name === selectedClass;
            
            return matchesSearch && matchesClass;
        });
        
        this.renderStudentList(filtered);
    }

    addSelectedStudent(studentId) {
        if (!this.selectedStudents.includes(studentId)) {
            this.selectedStudents.push(studentId);
            this.updateSelectedArea();
            this.updateStudentListItem(studentId, true);
        }
    }

    removeSelectedStudent(studentId) {
        this.selectedStudents = this.selectedStudents.filter(id => id !== studentId);
        this.updateSelectedArea();
        this.updateStudentListItem(studentId, false);
        
        if (this.options.onChange) {
            this.options.onChange(this.selectedStudents);
        }
    }

    updateSelectedArea() {
        const selectedArea = this.container.querySelector('.selected-students-area');
        if (!selectedArea) return;
        
        let html = '';
        if (this.selectedStudents.length > 0) {
            this.selectedStudents.forEach(studentId => {
                const student = this.students.find(s => s.id === studentId);
                if (student) {
                    html += `
                        <div class="student-tag" data-student-id="${student.id}">
                            <span class="student-tag-text">${student.name}（${student.class_name}-${student.student_no}）</span>
                            <span class="student-tag-remove" data-student-id="${student.id}">×</span>
                        </div>
                    `;
                }
            });
        } else {
            html = '<div class="no-selection-hint">请选择学生</div>';
        }
        
        selectedArea.innerHTML = html;
    }

    updateStudentListItem(studentId, isSelected) {
        const item = this.container.querySelector(`.student-list-item[data-student-id="${studentId}"]`);
        if (item) {
            const checkbox = item.querySelector('.student-checkbox');
            if (checkbox) {
                checkbox.checked = isSelected;
            }
            if (isSelected) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        }
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