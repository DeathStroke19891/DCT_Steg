import cv2
import bitstring
import numpy  as np
import zigzag as zz
import image_preparation as img
import data_embedding as stego

NUM_CHANNELS = 3
COVER_IMAGE_FILEPATH  = "./assets/spaceship_monochrome.png"
STEGO_IMAGE_FILEPATH  = "./res/stego_image.jpg"
SECRET_MESSAGE_STRING = "<insert_flag_here>"


raw_cover_image = cv2.imread(COVER_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
height, width   = raw_cover_image.shape[:2]
while(height % 8): height += 1
while(width  % 8): width  += 1
valid_dim = (width, height)
padded_image    = cv2.resize(raw_cover_image, valid_dim)
cover_image_f32 = np.float32(padded_image)
cover_image_YCC = img.YCC_Image(cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb))

stego_image = np.empty_like(cover_image_f32)

for chan_index in range(NUM_CHANNELS):
    dct_blocks = [cv2.dct(block) for block in cover_image_YCC.channels[chan_index]]
    dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]

    sorted_coefficients = [zz.zigzag(block) for block in dct_quants]

    if (chan_index == 0):
        secret_data = ""
        for char in SECRET_MESSAGE_STRING.encode('ascii'): secret_data += bitstring.pack('uint:8', char)
        embedded_dct_blocks   = stego.embed_encoded_data_into_DCT(secret_data, sorted_coefficients)
        desorted_coefficients = [zz.inverse_zigzag(block, vmax=8,hmax=8) for block in embedded_dct_blocks]
    else:
        desorted_coefficients = [zz.inverse_zigzag(block, vmax=8,hmax=8) for block in sorted_coefficients]

    dct_dequants = [np.multiply(data, img.JPEG_STD_LUM_QUANT_TABLE) for data in desorted_coefficients]

    idct_blocks = [cv2.idct(block) for block in dct_dequants]

    stego_image[:,:,chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(cover_image_YCC.width, idct_blocks))

stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)

final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))

cv2.imwrite(STEGO_IMAGE_FILEPATH, final_stego_image)
