# Sitemap SEO Implementation Guide

This document outlines the sitemap implementation for the MobixAI project, following professional SEO standards.

## Sitemap Structure

The project implements a two-level sitemap structure:

1. **Main Sitemap** (`sitemap.xml`) - Contains static pages
2. **Articles Sitemap** (`sitemap-articles.xml`) - Dynamically generated for model articles
3. **Sitemap Index** (`sitemap-index.xml`) - References both sitemaps

## Implementation Details

### Automatic Generation

The sitemap is automatically regenerated whenever articles are:
- Created
- Updated
- Deleted

This is implemented using Django signals in `ai_models/signals.py`.

### URL Structure

All URLs use the canonical domain `https://mobixai.ir` with proper HTTPS protocol.

### XML Standards

The sitemaps follow the official sitemap protocol:
- Proper XML declaration and encoding
- Correct namespace declarations
- Valid XML formatting with proper indentation

### Content Standards

#### Articles Sitemap
- **changefreq**: weekly (appropriate for content that may be updated)
- **priority**: 0.8 (high priority for content pages)
- **lastmod**: Uses W3C datetime format (ISO 8601)
- **Images**: Includes image:title and image:caption elements

#### Static Pages Sitemap
- **changefreq**: varies by page type (daily for homepage, monthly for terms)
- **priority**: 0.5-1.0 based on page importance
- **lastmod**: Current date for static pages

## Image Sitemap Extension

Image sitemaps are implemented for pages with relevant images:
- Proper `image:loc` with absolute URLs
- Descriptive `image:title` and `image:caption`
- Following Google's image sitemap guidelines

## Testing

To test sitemap generation:
```bash
python manage.py generate_sitemap
```

To verify sitemap accessibility:
- Visit `https://mobixai.ir/sitemap.xml`
- Visit `https://mobixai.ir/sitemap-articles.xml`

## Best Practices Implemented

1. **Proper Prioritization**: Pages are assigned appropriate priority values
2. **Accurate Change Frequency**: Values reflect actual content update frequency
3. **Valid URLs**: All URLs are absolute and include proper protocol
4. **Image Optimization**: Images include descriptive metadata
5. **Automatic Updates**: Sitemaps regenerate when content changes
6. **Error Handling**: Sitemap generation failures don't affect content operations

## Maintenance

Regular maintenance tasks:
1. Verify sitemap accessibility through Google Search Console
2. Check for broken URLs in sitemaps
3. Monitor sitemap generation logs for errors
4. Ensure all published content appears in relevant sitemaps

## Troubleshooting

Common issues and solutions:
1. **Sitemap not updating**: Check signal registration in apps.py
2. **Invalid URLs**: Verify get_absolute_url() method on models
3. **Permission errors**: Ensure templates directory is writable
4. **XML formatting issues**: Validate generated XML against sitemap schema