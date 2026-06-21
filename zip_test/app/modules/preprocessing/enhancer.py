import cv2
import numpy as np

class ImageEnhancer:
    """
    Advanced Image Preprocessing Pipeline for Traffic Images.
    Addresses Hackathon Task: "Image Preprocessing - Enhance image quality... Handle low light, rain, shadows, motion blur."
    """
    
    @staticmethod
    def enhance_low_light(image):
        """
        Uses Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L channel of LAB color space
        to improve visibility in shadows, night, and rain without washing out colors.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l_channel)
        
        # Merge and convert back
        limg = cv2.merge((cl, a, b))
        enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return enhanced_image
        
    @staticmethod
    def reduce_motion_blur(image):
        """
        Applies Unsharp Masking to sharpen details like license plates 
        that may be suffering from motion blur due to high-speed vehicles.
        """
        gaussian_blur = cv2.GaussianBlur(image, (9, 9), 10.0)
        unsharp_image = cv2.addWeighted(image, 1.5, gaussian_blur, -0.5, 0)
        return unsharp_image
        
    @staticmethod
    def process(image_path: str, output_path: str = None) -> str:
        """
        Full enhancement pipeline.
        """
        image = cv2.imread(image_path)
        if image is None:
            return image_path
            
        # 1. Enhance Low Light / Shadows
        enhanced = ImageEnhancer.enhance_low_light(image)
        
        # 2. Reduce Motion Blur / Sharpen
        sharpened = ImageEnhancer.reduce_motion_blur(enhanced)
        
        # Save or return
        out_path = output_path if output_path else image_path.replace(".jpg", "_enhanced.jpg").replace(".png", "_enhanced.png")
        cv2.imwrite(out_path, sharpened)
        
        return out_path
