// =================================
// تنظیمات اولیه و متغیرهای سراسری
// =================================

// متغیرهای سراسری
let currentSessionId = null;
let isStreaming = false;
let abortController = new AbortController();

// Initialize markdown-it with enhanced configuration
const md = window.markdownit({
    html: false,        // Disable HTML tags in source
    xhtmlOut: false,    // Use '/ >' in void tags
    breaks: true,       // Convert '\n' in paragraphs into <br>
    langPrefix: 'language-',  // CSS language prefix for fenced blocks
    linkify: true,      // Autoconvert URL-like text to links
    typographer: true,  // Enable some language-neutral replacement + quotes beautification
    quotes: ['\u201C', '\u201D', '\u2018', '\u2019'],  // Quote characters
    highlight: function (str, lang) {
        if (lang && hljs && hljs.getLanguage && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(str, { language: lang }).value;
            } catch (error) {
                console.warn('Syntax highlighting error:', error);
            }
        }
        
        // Escape special characters for HTML
        return md.utils.escapeHtml(str);
    }
});

// Add plugins for enhanced Markdown support
try {
    if (window.markdownitSub) md.use(window.markdownitSub);
    if (window.markdownitSup) md.use(window.markdownitSup);
    if (window.markdownitFootnote) md.use(window.markdownitFootnote);
    if (window.markdownitDeflist) md.use(window.markdownitDeflist);
    if (window.markdownitAbbr) md.use(window.markdownitAbbr);
    if (window.markdownitEmoji) md.use(window.markdownitEmoji);
} catch (e) {
    console.warn('Markdown plugins not available:', e);
}

// Initialize highlight.js
if (hljs) {
    hljs.highlightAll();
}