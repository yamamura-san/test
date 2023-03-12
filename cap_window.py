#ボタン押したら動画を撮影し、平均化処理し、指定のフォルダにimg_iとして保存するスクリプトにしようとしたが、使い勝手悪そうなのでやめる


import PySimpleGUI as sg
import configparser
from pypylon import pylon
import cv2
import time
import datetime
import os
import glob
import numpy as np


def cap_win(videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max):

    # フォルダ作成
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d-%H-%M")
    dir_output = "result_" + current_time
    os.makedirs(dir_output, exist_ok=True)
    dir_output_src = dir_output +"/source"
    os.makedirs(dir_output_src, exist_ok=True)    

    i = 1
    #　ループ
    while True:
        layout = [[sg.Text('処理を選択してください')],
                  [sg.Text("{}回目の撮影です".format(i))],
                  [sg.Button('撮影する'), sg.Button('撮影終了')]]

        window = sg.Window('動画撮影処理', layout)

        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        #　ボタン１を押したときの処理
        elif event == '撮影する':
            # 動画撮影
            name, folder = cap(dir_output, videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max, i)
            # 動画分割し、tmpフォルダに格納
            dir = split(name, folder, 100)
            # tmpフォルダの画像を平均化し、sourveフォルダにave画像を保存する
            ave(dir, dir_output_src, i)

            window.close()
            i = i+1

        #　ボタン２を押したときの処理
        elif event == '撮影終了':
            break

    window.close()
    return i-1, dir_output_src # 戻り値は撮影した回数とsourve画像のフォルダ

def cap(dir_output,videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max, i):
    # コーデック（fourcc）の設定
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

    # 動画ファイル設定（保存先、FPS、サイズ）
    name = 'output_{0}.mp4'.format(i)
    video = cv2.VideoWriter(dir_output+ "/" + name, fourcc, fps, (x_max-x_min, y_max-y_min))
    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # exposure time seting
    camera.ExposureTime.SetValue(exposuretime)
    # framerate
    camera.AcquisitionFrameRateEnable.SetValue(True)
    camera.AcquisitionFrameRate.SetValue(fps)
    # gain setting
    camera.Gain.SetValue(gain)

    converter = pylon.ImageFormatConverter()

    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    # カメラの設定変更のためにdelayさせる
    time.sleep(1)
    i=0
    while i < videotime*fps:
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            img= img[y_min : y_max, x_min : x_max]
            video.write(img)
            i +=1

    # Releasing the resource
    camera.StopGrabbing()
    cv2.destroyAllWindows()

    return name, dir_output

# 分割する動画名、動画の格納先、分割フレーム数の指定
def split(file, folder, num):
    # フォルダ作成処理
    # 実行時に生成するtmpフォルダ名の作成
    output = folder + "/tmp"
    os.makedirs(output, exist_ok=True)

    video = cv2.VideoCapture(folder + "/" + file)

    # 分割処理
    i=0
    while True:
        ret, frame = video.read() # 第一戻り数はTrue かFalse。動画が読み込めてたらTrue。第二戻り値は画像情報
        # fps分だけ分割
        if i < num:
            gray_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(output+'/img_'+str(i)+'.jpg', gray_frame)
            i +=1
        # 動画が読み込めなくなったらループ終了
        else:
            print("分割完了")
            break

    return output

def ave(dir, dir_output, k):
    #指定したディレクトリの画像を抽出
    imgs = dir+"/*jpg"
    imgs_list = glob.glob(imgs)

    #平均値を計算するための空のndarrayを作成
    img = cv2.imread(imgs_list[0],cv2.IMREAD_GRAYSCALE)
    h,w=img.shape[:2]
    base=np.zeros((h,w),np.uint32)

    #平均化処理
    for i in imgs_list:
        img = cv2.imread(i,cv2.IMREAD_GRAYSCALE)
        base += img
    base = base/(len(imgs_list))
    base=base.astype(np.uint8)
    cv2.imwrite(dir_output + "/ave_{0}.jpg".format(k), base)


if __name__ == "__main__":
    print(cap_win(2, 1000, 100, 23, 500, 900, 0, 1000))