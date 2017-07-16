import midi

pattern = midi.read_midifile("fl-60.mid")
print(pattern)

print("=================================")

pattern = midi.read_midifile("fl-120.mid")
print(pattern)