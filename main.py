# This project is licensed under the
# GNU General Public License v3.0
# 这个项目使用GPLv3许可证发布。
'''
This project is aim to make an AI who can write songs under some rules.
This project needs Python MIDI library(under MIT License), you can install it use the command below:
    pip install git+https://github.com/vishnubob/python-midi@feature/python3
This project is tested using Python3.5.2.
这个项目的目标是制作一个可以根据某些规则进行作曲的人工智能。
这个项目需要 Python MIDI library（基于MIT许可证），你可以通过下面的命令安装它：
    pip install git+https://github.com/vishnubob/python-midi@feature/python3
这个项目在Python3.5.2下测试通过。
'''
import math
import random

import midi


def init_midi(speed):
    # init an midi
    global pattern
    global track
    pattern = midi.Pattern(format=1, resolution=96)  # FL Studio's midi's resolution is 96.
    track = midi.Track()
    pattern.append(track)
    track.append(midi.SetTempoEvent(tick=0, data=[speed, 0, 0]))  # TODO：Discover what it is, and give a tempo option.
    # track.append(midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8])) # TODO：Discover what it is.
    # TimeSignatureEvent的第三个字节（24）是表示一个四分音符的tick数


def end_midi():
    # Add the end of track event, append it to the track
    global track
    eot = midi.EndOfTrackEvent(tick=0)
    track.append(eot)


def read_midi_file(path):
    global pattern
    pattern = midi.read_midifile(path)


def write_midi_file(path):
    global pattern
    midi.write_midifile(path, pattern)


def add_note(long, velocity, pitch):
    global track
    # pitch: A4=57, A5=69
    on = midi.NoteOnEvent(tick=0, velocity=velocity, pitch=pitch)
    track.append(on)
    off = midi.NoteOffEvent(tick=long * 24, pitch=pitch)
    track.append(off)


def test():
    # 随机生成的五声调式歌曲，但遵循下列规则：
    # 1.每个音符长1拍，
    # 2.总长度48拍
    global pattern
    init_midi(20)
    pitches = [midi.C_5, midi.D_5, midi.E_5, midi.G_5, midi.A_5, ]  # 民族五声调式的五个音
    for i in range(0, 48):
        rand = random.random() * len(pitches)
        pitch = pitches[int(rand)]
        add_note(1, 100, pitch)
    end_midi()
    write_midi_file("test.mid")
    print(pattern)


def test2():
    # 随机生成的五声调式歌曲，但遵循下列规则：
    # 1.下行多级进
    # 2.上行多跳进
    # 3.模板：[A-A-B-C]-[A-A-B-C]-[D-E-F]-[D-E-F]-[A-A-B-C] 其中ABCF为2小节，DE为1小节（一小节有4拍）
    global pattern
    # 初始化素材
    pitches = [midi.D_5,midi.E_5,midi.G_5, midi.A_5, midi.C_6, midi.D_6, midi.E_6]
    parts = {}
    direction = 0  # 1为上行，0为下行
    first_note = 4
    new_note = last_note = first_note
    # 生成素材
    for j in range(0, 6):
        parts[j] = []
        if j == 0 or j == 1 or j == 2 or j == 5:
            k = 8
        else:
            k = 4
        for i in range(0, k):
            # 如果是全曲第一个音
            if i == 0 and j == 1:
                parts[j].append(pitches[first_note])
            # 否则
            else:
                # 如果到底部，则上行
                if last_note == 0:
                    direction = 1
                # 如果到顶部，则下行
                elif last_note == len(pitches) - 1:
                    direction = 0
                # 如果在中间
                else:
                    # 有趋向0.618的音的趋向性
                    target_note = int(len(pitches) / 2 + 0.5)  # int((pitches[-1]-pitches[0])*0.618)
                    rand = random.random()
                    if last_note > target_note:  # 如果在目标音符上方
                        if direction == 0:  # 如果当前是下行
                            if rand - (last_note - target_note) / 15 >= 0.8:  # 偶尔也会反弹
                                direction = 1
                        else:  # 如果当前是上行
                            if rand + (last_note - target_note) / 12 >= 0.5:  # 偏离越多趋向性越强
                                direction = 0
                    if last_note <= target_note:  # 如果在目标音符下方
                        if direction == 0:  # 如果当前是下行
                            if rand - (last_note - target_note) / 12 >= 0.5:
                                direction = 1
                        else:  # 如果当前是上行
                            if rand + (last_note - target_note) / 15 >= 0.8:
                                direction = 0
                # 根据上面判断的方向，产生音符
                ok = 0
                if direction == 0:
                    # 随机下行
                    while (ok == 0):
                        rand = random.random()
                        if rand <= 0.9:  # 级进
                            new_note = last_note - 1
                        else:  # 跳进
                            new_note = last_note - 2  # 最多跳2个音
                        if new_note >= 0: ok = 1
                else:
                    # 随机上行
                    while (ok == 0):
                        rand = random.random()
                        if rand <= 0.6:  # 级进
                            new_note = last_note + 1
                        else:  # 跳进
                            new_note = last_note + int(math.sqrt((rand - 0.4) * 15+0.5) + 2)  # 最多跳5个音
                        if new_note <= len(pitches) - 1: ok = 1
                parts[j].append(pitches[new_note])
                last_note = new_note
                # print(last_note)
    init_midi(10)
    # [A-A-B-C]-[A-A-B-C]-[D-E-F]-[D-E-F]-[A-A-B-C]
    #texture = [0, 0, 1, 2, 0, 0, 1, 2, 3, 4, 5, 3, 4, 5, 0, 0, 1, 2]
    texture = [0, 1, 2,  3, 4, 5]
    for i in range(0, len(texture)):
        for j in range(0, len(parts[texture[i]])):
            add_note(1, 100, parts[texture[i]][j])

    end_midi()
    write_midi_file("test.mid")
    print(pattern)


if __name__ == '__main__':
    test2()
