from PIL import Image

def make_white_transparent(input_path, output_path=None, threshold=240):
    """
    Converts all white (or near-white) pixels in a PNG to transparent.
    Args:
        input_path (str): Path to the input PNG file.
        output_path (str, optional): Path to save the output PNG.
        threshold (int): RGB value above which a pixel is considered white.
    """
    img = Image.open(input_path).convert('RGBA')
    datas = img.getdata()
    newData = []
    
    for item in datas:
        # item is (R, G, B, A)
        if item[0] >= threshold and item[1] >= threshold and item[2] >= threshold:
            # Make white/near-white pixels transparent
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    img.putdata(newData)
    
    if output_path:
        img.save(output_path, "PNG")
    
    return output_path
