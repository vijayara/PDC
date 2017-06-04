import time

current_milli_time = lambda: int(round(time.time() * 1000))

n_takes = 10
mili_step = 10
time_end = 0

curr_pic = 0


end_recording = False

previous_mili_sec = time_end

while not end_recording:
    current_mili_sec = current_milli_time() % mili_step

    if current_mili_sec == time_end and previous_mili_sec != time_end:
        print(current_mili_sec)
        curr_pic += 1

    previous_mili_sec = current_mili_sec

    if n_takes < curr_pic:
        end_recording = True

