# Media Uploads Strategy

## Overview

The platform supports multiple media types for posts:
- **Images**: Handwritten notes, diagrams
- **Slides**: Google Slides embeds
- **YouTube**: Video content
- **Blog Links**: External references

## Development (Local)

For local development, media files are stored in the `static/media/` folder:

```
static/
├── media/
│   └── posts/
│       ├── kadanes-algorithm/
│       │   ├── example_0.jpg
│       │   ├── example_1.jpg
│       │   └── example_2.jpg
│       └── graph-neural-networks/
│           └── ...
```

### URLs in Development:
```json
{
  "type": "image",
  "url": "/static/media/posts/kadanes-algorithm/example_0.jpg",
  "title": "Kadane's Algorithm - Page 1",
  "order": 1
}
```

## Production (Staging/Prod with S3)

In production, media files should be uploaded to S3 and referenced by their CDN URLs.

### S3 Structure:
```
s3://edu-vexxel-media/
├── posts/
│   ├── kadanes-algorithm/
│   │   ├── example_0.jpg
│   │   ├── example_1.jpg
│   │   └── example_2.jpg
│   └── graph-neural-networks/
│       └── ...
```

### URLs in Production:
```json
{
  "type": "image",
  "url": "https://cdn.edu.vexxel.ai/posts/kadanes-algorithm/example_0.jpg",
  "title": "Kadane's Algorithm - Page 1",
  "order": 1
}
```

## Environment-Based URL Strategy

### Option 1: Use Environment Variable Prefix (Recommended)

Add to `.env`:
```bash
# Development
MEDIA_BASE_URL=/static/media

# Production
MEDIA_BASE_URL=https://cdn.edu.vexxel.ai
```

Then in seed scripts/API endpoints, construct URLs:
```python
from app.config import settings

media_url = f"{settings.media_base_url}/posts/kadanes-algorithm/example_0.jpg"
```

### Option 2: Store Full URLs in Database

Store complete URLs in the database and update them based on environment:
- Development: `/static/media/posts/...`
- Production: `https://cdn.edu.vexxel.ai/posts/...`

## Uploading Media to S3

### Manual Upload (Initial Setup)

```bash
# Install AWS CLI
brew install awscli  # or: pip install awscli

# Configure AWS credentials
aws configure

# Upload media files
aws s3 sync static/media/posts/ s3://edu-vexxel-media/posts/ \
  --acl public-read \
  --cache-control "max-age=31536000"
```

### Automated Upload (CI/CD)

Add to your deployment pipeline:

```yaml
# .github/workflows/deploy.yml
- name: Upload media to S3
  run: |
    aws s3 sync static/media/posts/ s3://edu-vexxel-media/posts/ \
      --acl public-read \
      --cache-control "max-age=31536000" \
      --exclude ".DS_Store"
```

## CloudFront CDN Setup

1. **Create CloudFront Distribution**:
   - Origin: S3 bucket (`edu-vexxel-media`)
   - Alternate Domain: `cdn.edu.vexxel.ai`
   - SSL Certificate: ACM certificate for `*.edu.vexxel.ai`

2. **Update DNS**:
   - Add CNAME: `cdn.edu.vexxel.ai` → CloudFront distribution domain

3. **Cache Settings**:
   - Default TTL: 1 year (31536000 seconds)
   - Compress objects: Yes
   - Allowed HTTP Methods: GET, HEAD

## Image Optimization

Before uploading to production:

```bash
# Install ImageMagick
brew install imagemagick

# Optimize images
for file in static/media/posts/**/*.jpg; do
  convert "$file" -quality 85 -strip "$file"
done

# Or use a Node.js tool
npm install -g sharp-cli
sharp-cli resize --width 1200 --quality 85 static/media/posts/**/*.jpg
```

## Security Considerations

### Development:
- ✅ Files served directly from FastAPI static files
- ✅ No authentication needed (public content)

### Production:
- ✅ Use S3 bucket policies to allow public read-only access
- ✅ Enable CloudFront for performance and DDoS protection
- ✅ Use signed URLs for private content (future feature)
- ❌ Don't allow public write access to S3 bucket

## Best Practices

1. **Naming Convention**:
   - Use slugs matching post slugs: `posts/{post-slug}/`
   - Use sequential names: `image_0.jpg`, `image_1.jpg`, etc.

2. **File Sizes**:
   - Images: < 2MB per image
   - Optimize before upload (85% JPEG quality)
   - Consider WebP format for better compression

3. **Organization**:
   - One folder per post
   - Keep metadata.json in sync with actual files
   - Include alt text in `title` field for accessibility

4. **Backup**:
   - Keep original high-res images in separate backup
   - Version S3 bucket for recovery
   - Regular backups of database (includes URLs)

## Migration Script (Dev → Prod)

Create a script to update URLs when moving to production:

```python
# scripts/migrate_urls_to_s3.py
from sqlmodel import select, Session
from app.models import MediaAsset
from app.database import engine

def migrate_urls(cdn_base: str = "https://cdn.edu.vexxel.ai"):
    with Session(engine) as session:
        assets = session.exec(select(MediaAsset)).all()

        for asset in assets:
            if asset.url and asset.url.startswith("/static/media/"):
                # Update to S3 URL
                new_url = asset.url.replace("/static/media/", f"{cdn_base}/")
                asset.url = new_url
                session.add(asset)

        session.commit()
        print(f"✓ Migrated {len(assets)} media assets to CDN URLs")

if __name__ == "__main__":
    migrate_urls()
```

Run during deployment:
```bash
python scripts/migrate_urls_to_s3.py
```

## Troubleshooting

### Images not loading locally:
- Check `static/media/posts/` folder exists
- Verify file permissions: `chmod -R 755 static/media/`
- Restart FastAPI server to remount static files

### Images not loading in production:
- Verify S3 bucket policy allows public read
- Check CloudFront distribution is deployed
- Verify DNS CNAME record points to CloudFront
- Check CORS settings if loading from different domain

### Large files:
- Use S3 multipart upload for files > 5MB
- Consider video transcoding for video content
- Implement lazy loading for image galleries
