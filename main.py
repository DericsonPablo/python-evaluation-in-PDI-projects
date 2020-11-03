import os
import shutil
import time
import cv2
import argparse

# Processa parâmetros opcionais de entrada
parser = argparse.ArgumentParser(description='Segmentation images with rgb, lab and hsv')
parser.add_argument('--img',
                    help="Parâmetro onde deve ser passado o caminho das imagens, por default utiliza 'imagens/'")
parser.add_argument('--save', action='store_true',
                    help="Parâmetro para salvar as imagens intermediárias, default é 'False'")
parser.add_argument('--ruido', help="Utilizado para definir um ruido mínimo, default é 0")
args = parser.parse_args()

SALVA_IMAGENS = args.save or True
AREA_RUIDO = float(args.ruido) or 0.0


# processa a imagem e retorna a imagem com o filtro otsu e a binarização
def otsu_threshold(imagem, name, type):
    _, otsu = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, otsu_inv = cv2.threshold(otsu, 0, 255, cv2.THRESH_BINARY_INV)
    if SALVA_IMAGENS:
        cv2.imwrite(f"imagens/processadas/{name}_otsu_{type}.jpg", otsu)
        cv2.imwrite(f"imagens/processadas/{name}_otsu_inv_{type}.jpg", otsu_inv)
    return otsu_inv


# Retorna os contornos econtrados
def encontra_contornos(imagem, imagem_original, type):
    contours, hierarchy = cv2.findContours(imagem, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if SALVA_IMAGENS:
        new_image = imagem_original.copy()
        cv2.drawContours(new_image, contours, -1, (0, 255, 0), 3)
        cv2.imwrite(f"imagens/processadas/image_with_contours_{type}.jpg", new_image)
    return contours


# Realiza o corte das imagens e retorna a quantidade de cortes encontrados e a área cortada
def corta_imagens(contours, imagem, image_and, name, type):
    print("    Corta Sementes")
    area_total = 0.0
    quantidade = 0

    for contorno in contours:
        area = cv2.contourArea(contorno)
        if area > AREA_RUIDO:
            area_total += area
            if SALVA_IMAGENS:
                x, y, w, h = cv2.boundingRect(contorno)
                cortada = imagem[y:y + h, x:x + w]
                cortada_f = image_and[y:y + h, x:x + w]
                cv2.imwrite(f"imagens/processadas/cortadas{type}/{name}_{quantidade}.png", cortada)
                cv2.imwrite(f"imagens/processadas/cortadas{type}F/{name}_{quantidade}.png", cortada_f)
            quantidade += 1
    return area_total, quantidade


# Função que realiza a segmentação RGB
def segmenta_rgb(imagem, name):
    print("RGB")
    print("  Segmentação")
    initial_time = time.time()
    frame_r, frame_g, frame_b = cv2.split(imagem)
    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/img_RGB_r.jpg", frame_r)
        cv2.imwrite("imagens/processadas/img_RGB_g.jpg", frame_g)
        cv2.imwrite("imagens/processadas/img_RGB_b.jpg", frame_b)

    otsu_inv_r = otsu_threshold(frame_r, name, "RGB_r")
    otsu_inv_g = otsu_threshold(frame_g, name, "RGB_g")
    otsu_inv_b = otsu_threshold(frame_b, name, "RGB_b")

    image_otsu_range = cv2.bitwise_or(otsu_inv_r, otsu_inv_g)
    image_otsu_range = cv2.bitwise_or(otsu_inv_g, image_otsu_range)

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/image_RGB_otsu_range.jpg", image_otsu_range)
    contours = encontra_contornos(image_otsu_range, imagem, "RGB")

    image_merged_rgb = cv2.merge((otsu_inv_r, otsu_inv_g, otsu_inv_b))
    image_and = cv2.bitwise_and(image_merged_rgb, imagem)

    print(f"Segmentação levou {time.time() - initial_time} segundos")

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/merged_rgb.jpg", image_and)

    area_total, quantidade = corta_imagens(contours, imagem, image_and, name, "RGB")
    print(f"Area Total: {area_total}")
    print(f"Total: {quantidade}")


# Função que realiza a segmentação LAB
def segmenta_cielab(imagem, name):
    print("LAB")
    print("  Segmentação")
    initial_time = time.time()
    img_lab = cv2.cvtColor(imagem, cv2.COLOR_RGB2Lab)
    img_LRGB = cv2.cvtColor(img_lab, cv2.COLOR_Lab2LRGB)
    if SALVA_IMAGENS:
        cv2.imwrite(f"imagens/processadas/{name}_name_img_lab.png", img_lab)
        cv2.imwrite(f"imagens/processadas/{name}_lab2.png", img_LRGB)

    frame_l, frame_a, frame_b = cv2.split(img_LRGB)

    l = otsu_threshold(frame_l, name, "CIE_l")
    a = otsu_threshold(frame_a, name, "CIE_a")
    b = otsu_threshold(frame_b, name, "CIE_b")

    image_otsu_range = cv2.bitwise_or(l, a)
    image_otsu_range = cv2.bitwise_or(b, image_otsu_range)

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/image_CIE_otsu_range.jpg", image_otsu_range)
    contours = encontra_contornos(image_otsu_range, imagem, "CIE")

    image_merged_lab = cv2.merge((l, a, b))
    image_and = cv2.bitwise_and(image_merged_lab, imagem)

    print(f"Segmentação levou {time.time() - initial_time} segundos")

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/merged_rgb.jpg", image_and)

    area_total, quantidade = corta_imagens(contours, imagem, image_and, name, "LAB")
    print(f"Area Total: {area_total}")
    print(f"Total: {quantidade}")


# Função que realiza a segmentação HSV
def segmenta_hsv(imagem, name):
    print("HSV")
    print("  Segmentação")
    initial_time = time.time()
    img_hsv = cv2.cvtColor(imagem, cv2.COLOR_RGB2HSV)
    img_hsv_save = cv2.cvtColor(img_hsv, cv2.COLOR_Lab2LRGB)
    if SALVA_IMAGENS:
        cv2.imwrite(f"imagens/processadas/{name}_img_hsv.png", img_hsv)
        cv2.imwrite(f"imagens/processadas/{name}_img_hsv_save.png", img_hsv_save)

    frame_h, frame_s, frame_v = cv2.split(img_hsv)

    h = otsu_threshold(frame_h, name, "HSV_h")
    s = otsu_threshold(frame_s, name, "HSV_s")
    v = otsu_threshold(frame_v, name, "HSV_v")

    image_otsu_range = cv2.bitwise_or(h, s)
    image_otsu_range = cv2.bitwise_or(v, image_otsu_range)

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/image_HSV_otsu_range.jpg", image_otsu_range)
    contours = encontra_contornos(image_otsu_range, imagem, "HSV")

    image_merged_lab = cv2.merge((h, s, v))
    image_and = cv2.bitwise_and(image_merged_lab, imagem)

    print(f"Segmentação levou {time.time() - initial_time} segundos")

    if SALVA_IMAGENS:
        cv2.imwrite("imagens/processadas/merged_hsv.jpg", image_and)

    area_total, quantidade = corta_imagens(contours, imagem, image_and, name, "HSV")
    print(f"Area Total: {area_total}")
    print(f"Total: {quantidade}")


# Função principal do aplicativo
def application():
    root_folder = 'imagens'
    cortadas = ["processadas/cortadasLAB", "processadas/cortadasLABF", "processadas/cortadasRGB",
                "processadas/cortadasRGBF", "processadas/cortadasHSV", "processadas/cortadasHSVF"]

    # Cria pastas e remove o que não devia estar ali
    for cortada_path in cortadas:
        cortada_path_full = os.path.join(root_folder, cortada_path)
        if not os.path.exists(cortada_path_full):
            os.makedirs(cortada_path_full)
        else:
            for folder in os.listdir(cortada_path_full):
                full_folder = os.path.join(cortada_path_full, folder)
                if os.path.isfile(full_folder):
                    os.remove(full_folder)
                else:
                    shutil.rmtree(full_folder)

    # itera sobre as imagens base
    for path in os.listdir(root_folder):
        path_full = os.path.join(root_folder, path)
        if os.path.isfile(path_full):
            filename, file_extension = path.split(".")
            if file_extension.lower() in ['png', 'bmp', 'jpg']:
                print("Processing file " + path_full)
                print(f"Utilizando como área mínima de ruído {AREA_RUIDO}")
                image = cv2.imread(path_full, cv2.IMREAD_ANYCOLOR)

                print("Realizando segmentação RGB")
                tempo_inicial = time.time()
                segmenta_rgb(image, filename)
                print(f"Processamento total realizado em {time.time() - tempo_inicial} segundos")

                print("Realizando segmentação cielab")
                tempo_inicial = time.time()
                segmenta_cielab(image, filename)
                print(f"Processamento total realizado em {time.time() - tempo_inicial} segundos")

                print("Realizando segmentação hsv")
                tempo_inicial = time.time()
                segmenta_hsv(image, filename)
                print(f"Processamento total realizado em {time.time() - tempo_inicial} segundos")


if __name__ == '__main__':
    application()
