# Deep Learning Content - How to Add Your PDFs

This directory contains deep learning lessons with interactive visualizations.

## Directory Structure

```
deep_learning/
├── README.md (this file)
└── mlp_basics/
    ├── metadata.json          # Configuration for this lesson
    ├── mlp_notes.pdf         # Your beautiful PDF notes
    └── thumbnail.png         # (optional) Thumbnail image
```

## How to Add Your Own Content

### Step 1: Create a New Lesson Folder

```bash
mkdir -p content/deep_learning/your_topic_name
```

### Step 2: Add Your PDF

Place your beautifully designed PDF in the folder:

```bash
cp ~/Downloads/your_notes.pdf content/deep_learning/your_topic_name/notes.pdf
```

### Step 3: Create metadata.json

Copy the template from `mlp_basics/metadata.json` and customize it:

```json
{
  "title": "Your Topic Title",
  "slug": "your-topic-name",
  "description": "Brief description of what this lesson covers",
  "content_type": "deep_learning",

  "pdf": {
    "filename": "notes.pdf",
    "path": "/static/content/deep_learning/your_topic_name/notes.pdf",
    "pages": 12
  },

  "learning_objectives": [
    "Objective 1",
    "Objective 2"
  ],

  "visualizations": {
    "viz_id": {
      "type": "mlp_forward",
      "linked_pages": [3, 4],
      "config": {
        "layers": [3, 4, 2],
        "activation": "relu"
      }
    }
  },

  "page_mappings": {
    "3": "viz_id",
    "4": "viz_id"
  }
}
```

### Step 4: Copy PDF to Static Directory

For the PDF to be accessible, copy it to the static directory:

```bash
mkdir -p app/static/content/deep_learning/your_topic_name
cp content/deep_learning/your_topic_name/notes.pdf app/static/content/deep_learning/your_topic_name/
```

### Step 5: Add Route in Backend

Edit `app/main.py` and add a new route:

```python
@app.get("/lessons/your-topic-name", response_class=HTMLResponse)
async def lesson_your_topic(request: Request, templates: Templates):
    # Load metadata
    import json
    with open("content/deep_learning/your_topic_name/metadata.json") as f:
        metadata = json.load(f)

    return templates.TemplateResponse(
        "deep_learning_viewer.html",
        {
            "request": request,
            "content": metadata,
            "visualizations": metadata["visualizations"],
            "page_mappings": metadata["page_mappings"],
            "pdf_url": metadata["pdf"]["path"]
        }
    )
```

## Available Visualization Types

Currently implemented:
- `mlp_forward` - Multi-Layer Perceptron Forward Propagation

Coming soon:
- `mlp_backprop` - Backpropagation visualization
- `activation_comparison` - Interactive activation function graphs
- `cnn_convolution` - Convolutional layer visualization
- `attention_mechanism` - Attention mechanism for transformers

## Tips for PDF Design

1. **Keep it visual** - Your PDFs are already beautiful, keep that style!
2. **Mark visualization pages** - Add a small icon or note on pages that have interactive visualizations
3. **Consistent layout** - Use consistent formatting for easier navigation
4. **High resolution** - PDFs render at native quality, so high-res diagrams look great
5. **Page numbers** - Include page numbers for easy reference

## Best Practices

- One lesson per folder
- Use descriptive slugs (lowercase, hyphens)
- Link visualizations to relevant pages
- Test your PDF renders correctly before deploying
- Keep PDFs under 10MB for faster loading

## Need Help?

Check the example in `mlp_basics/` for a complete working example.
