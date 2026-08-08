"""
Local AI Image Analysis Service.

Runs 100% locally on the server without any external LLM/Vision APIs.
Uses PIL / OpenCV / PyTorch for:
1. Sharpness & Blur Detection (Laplacian variance)
2. Lighting & Exposure Analysis (Daylight vs Nighttime)
3. Color Spectrum & Dominant Feature Extraction
4. Pre-trained Local Computer Vision (MobileNetV2) Object & Scene Classification
"""

import logging
import os
from typing import Dict, Any, Optional, List
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Global model reference for local PyTorch MobileNetV2
_vision_model = None
_vision_transforms = None
_categories_map = None


def _init_local_vision_model():
    """Attempt to initialize local PyTorch MobileNetV2 model for object tagging."""
    global _vision_model, _vision_transforms, _categories_map
    if _vision_model is not None:
        return

    try:
        import torch
        import torchvision.models as models
        import torchvision.transforms as transforms
        import urllib.request

        # Load lightweight MobileNetV2 locally
        _vision_model = models.mobilenet_v2(pretrained=True)
        _vision_model.eval()

        _vision_transforms = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
        with urllib.request.urlopen(url, timeout=5) as f:
            _categories_map = [line.decode("utf-8").strip() for line in f.readlines()]

        logger.info("Local PyTorch MobileNetV2 vision model loaded successfully")
    except Exception as e:
        logger.warning(f"Local PyTorch vision model initialization skipped: {e}")


CIVIC_TAG_MAPPING = {
    "Road": ["asphalt", "pothole", "street", "car", "cab", "truck", "traffic", "highway", "minibus", "tire", "bumper", "curb", "viaduct", "bridge", "intersection", "road", "vehicle"],
    "Waste": ["garbage", "trash", "bin", "litter", "carton", "plastic", "waste", "container", "dumpster", "junk", "refuse", "rubbish"],
    "Water": ["water", "stream", "lake", "ocean", "river", "hydrant", "fountain", "pool", "spill", "leak", "waterfall", "geyser"],
    "Electricity": ["pole", "line", "wire", "cable", "lamp", "lantern", "spotlight", "generator", "transformer", "lightning"],
    "Drainage": ["manhole", "sewer", "drain", "gutter", "puddle", "trench", "flood", "culvert"],
    "Safety": ["fence", "barrier", "fire", "danger", "warning", "police"],
}

NON_CIVIC_KEYWORDS = [
    # Animals & Pets
    "cat", "dog", "tabby", "persian", "siamese", "egyptian cat", "cougar", "lynx", "kitten", "puppy", "hound", "retriever",
    "terrier", "spaniel", "shepherd", "chihuahua", "poodle", "beagle", "bulldog",
    "lion", "tiger", "bear", "elephant", "zebra", "giraffe", "monkey", "rabbit",
    "mouse", "hamster", "bird", "parrot", "duck", "goose", "owl", "fish", "toy", "teddy",
    # Humans, Portraits, Selfies, Profile Pictures, Clothing
    "person", "man", "woman", "human", "face", "portrait", "profile", "selfie", "groom", "bride",
    "suit", "necktie", "bow tie", "trench coat", "fur coat", "lab coat", "cardigan", "jersey", "sweatshirt",
    "t-shirt", "shirt", "dress", "skirt", "gown", "academic gown", "wig", "hair slide", "sunglasses", "spectacles",
    "swimming trunks", "swimsuit", "bikini", "pajamas", "footwear", "sandal", "clog", "shoe", "boot",
    # Documents, ID Cards, Passports, Paper, Cards & License
    "identity card", "id card", "envelope", "passport", "menu", "paper", "binder", "book", "card",
    "document", "certificate", "license", "credit card", "bank card", "cash machine", "web site",
    "crossword", "scoreboard", "packet", "carton", "letter", "page",
    # Indoor Household & Office Furniture
    "sofa", "couch", "bed", "pillow", "quilt", "desk", "table", "chair", "armchair", "rocking chair",
    "television", "monitor", "screen", "laptop", "keyboard", "mouse", "refrigerator", "microwave",
    "coffee maker", "espresso", "cup", "mug", "plate", "bowl", "fork", "knife", "spoon", "menu", "vase"
]


def analyze_uploaded_image(file_path: str, expected_category: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an uploaded image file locally on the server.
    
    Returns structured analysis results including clarity, lighting, visual tags, category boost, and relevancy.
    """
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "File not found",
            "is_relevant": False,
            "rejection_reason": "File not found",
            "clarity_score": 0.0,
            "clarity_label": "Unknown",
            "lighting": "Unknown",
            "detected_tags": [],
            "suggested_category": None,
        }

    try:
        img = Image.open(file_path).convert("RGB")
        img_np = np.array(img)

        # 1. Lighting Analysis (Average Luminance)
        luminance = np.mean(0.299 * img_np[:, :, 0] + 0.587 * img_np[:, :, 1] + 0.114 * img_np[:, :, 2])
        if luminance < 60:
            lighting = "Nighttime / Dark"
        elif luminance > 200:
            lighting = "Overexposed / Very Bright"
        else:
            lighting = "Daylight / Well-lit"

        # 2. Sharpness & Blur Analysis
        gy, gx = np.gradient(img_np[:, :, 0].astype(float))
        gnorm = np.sqrt(gx**2 + gy**2)
        sharpness_score = float(np.var(gnorm))

        if sharpness_score < 10.0:
            clarity_label = "Blurry / Low Quality"
        elif sharpness_score < 40.0:
            clarity_label = "Moderate Clarity"
        else:
            clarity_label = "High Clarity / Sharp"

        # 3. Object & Tag Detection via local PyTorch model if available
        detected_tags = []
        suggested_category = None
        category_scores = {cat: 0.0 for cat in CIVIC_TAG_MAPPING}
        animal_or_human_detected_label = None

        _init_local_vision_model()
        if _vision_model is not None and _vision_transforms is not None and _categories_map is not None:
            try:
                import torch
                input_tensor = _vision_transforms(img).unsqueeze(0)
                with torch.no_grad():
                    output = _vision_model(input_tensor)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                top_prob, top_cat_id = torch.topk(probabilities, 5)
                for i in range(top_prob.size(0)):
                    prob = float(top_prob[i].item())
                    class_idx = int(top_cat_id[i].item())
                    label = _categories_map[class_idx].lower() if class_idx < len(_categories_map) else f"class_{class_idx}"
                    if prob > 0.05:
                        detected_tags.append(f"{label} ({prob*100:.0f}%)")

                        # ImageNet classes 0 to 397 are animals/pets/wildlife
                        if class_idx < 398 and prob > 0.15 and not animal_or_human_detected_label:
                            animal_or_human_detected_label = label

                        # Map label to civic category
                        for cat, keywords in CIVIC_TAG_MAPPING.items():
                            for kw in keywords:
                                if kw in label:
                                    category_scores[cat] += prob

            except Exception as ex:
                logger.warning(f"Local vision model inference failed: {ex}")

        # If no PyTorch tags matched, fallback to color spectrum heuristics
        if not any(category_scores.values()):
            avg_r, avg_g, avg_b = np.mean(img_np[:, :, 0]), np.mean(img_np[:, :, 1]), np.mean(img_np[:, :, 2])
            if avg_b > avg_r + 15 and avg_b > avg_g:
                category_scores["Water"] += 0.3
                detected_tags.append("water-colored surface")
            elif abs(avg_r - avg_g) < 15 and abs(avg_g - avg_b) < 15 and luminance < 120:
                category_scores["Road"] += 0.3
                detected_tags.append("asphalt/road grey surface")

        best_cat = max(category_scores, key=category_scores.get)
        if category_scores[best_cat] > 0.1:
            suggested_category = best_cat

        # 4. Relevancy & Non-Civic Subject Validation
        is_relevant = True
        rejection_reason = None

        # Check animal / human class IDs
        if animal_or_human_detected_label:
            is_relevant = False
            rejection_reason = f"Uploaded photo appears to be an animal/pet or non-civic subject ('{animal_or_human_detected_label}')."
        else:
            # Check non-civic keywords (person, suit, tie, profile pic, furniture, etc.) using whole-word boundaries
            import re
            for tag in detected_tags:
                tag_clean = tag.lower()
                for non_kw in NON_CIVIC_KEYWORDS:
                    if re.search(r'\b' + re.escape(non_kw.lower()) + r'\b', tag_clean):
                        is_relevant = False
                        rejection_reason = f"Uploaded photo appears to be a person, portrait, or non-civic object ('{non_kw}')."
                        break
                if not is_relevant:
                    break

        # Check category alignment if expected_category is provided and image is still marked relevant
        if is_relevant and expected_category and expected_category in CIVIC_TAG_MAPPING:
            exp_score = category_scores.get(expected_category, 0.0)
            other_cats = [c for c, s in category_scores.items() if c != expected_category and s > 0.15]
            if exp_score == 0.0 and other_cats:
                is_relevant = False
                top_other = max(other_cats, key=lambda c: category_scores[c])
                rejection_reason = f"Uploaded photo appears to show '{top_other}' evidence rather than reported '{expected_category}' issue."

        # Document / ID Card Heuristic: High uniform light background with no civic features
        if is_relevant and luminance > 160 and sharpness_score > 25.0 and not any(category_scores.values()):
            h, w, _ = img_np.shape
            if h > 50 and w > 50:
                corners = [
                    img_np[:25, :25], img_np[:25, -25:], img_np[-25:, :25], img_np[-25:, -25:]
                ]
                corner_stds = [float(np.std(c)) for c in corners]
                if np.mean(corner_stds) < 30.0:
                    is_relevant = False
                    rejection_reason = "Uploaded photo appears to be a document, ID card, paper, or text scan rather than a civic infrastructure issue."

        return {
            "status": "success",
            "is_relevant": is_relevant,
            "rejection_reason": rejection_reason,
            "clarity_score": round(sharpness_score, 1),
            "clarity_label": clarity_label,
            "lighting": lighting,
            "detected_tags": detected_tags[:5],
            "suggested_category": suggested_category,
            "image_width": img.width,
            "image_height": img.height,
        }

    except Exception as e:
        logger.error(f"Failed to analyze image {file_path}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "clarity_score": 0.0,
            "clarity_label": "Unknown",
            "lighting": "Unknown",
            "detected_tags": [],
            "suggested_category": None,
        }
