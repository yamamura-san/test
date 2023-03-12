from package import camera_setting as cs
from package import cap_window as cw

print("処理中です")

videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max = cs.setting()

print(cw.cap_win(videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max))

print("処理完了")