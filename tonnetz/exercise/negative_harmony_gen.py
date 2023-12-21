import numpy as np
import copy
import partitura as pt


PC_coodinates = {
    (0, 0): 0,
    (3, 1): 1,
    (2, 2): 2,
    (1, 0): 3,
    (0, 1): 4,
    (3, 2): 5,
    (2, 0): 6,
    (1, 1): 7,
    (0, 2): 8,
    (3, 0): 9,
    (2, 1): 10,
    (1, 2): 11,
    # lambda x,y: x%4 == 0 and y%3 == 0: 0, # C
    # lambda x,y: x%4 == 3 and y%3 == 1: 1, # C#
    # lambda x,y: x%4 == 2 and y%3 == 2: 2, # D
    # lambda x,y: x%4 == 1 and y%3 == 0: 3, # D#
    # lambda x,y: x%4 == 0 and y%3 == 1: 4, # E
    # lambda x,y: x%4 == 3 and y%3 == 2: 5, # F
    # lambda x,y: x%4 == 2 and y%3 == 0: 6, # F#
    # lambda x,y: x%4 == 1 and y%3 == 1: 7, # G
    # lambda x,y: x%4 == 0 and y%3 == 2: 8, # G#
    # lambda x,y: x%4 == 3 and y%3 == 0: 9, # A
    # lambda x,y: x%4 == 2 and y%3 == 1: 10, # A#
    # lambda x,y: x%4 == 1 and y%3 == 2: 11, # B
    0: (0,0),
    1: (3,1),
    2: (2,2),
    3: (1,0),
    4: (0,1),
    5: (3,2),
    6: (2,0),
    7: (1,1),
    8: (0,2),
    9: (3,0),
    10: (2,1),
    11: (1,2),
}


def reflect(chord, base_point=0, system=[3, 4, 5]):
    """Reflect a chord around a point."""
    if len(chord) == 1:
        return chord
    # chord to coordinates
    coords = tuple(map(lambda x: PC_coodinates[x], chord))
    b = PC_coodinates[base_point][1]
    # mirror coordinates around y = x + b
    new_coords = [(y-b, x+b) for (x, y) in coords]
    neg_chord = list(map(lambda x: PC_coodinates[(x[0]%system[1], x[1]%system[0])], new_coords))
    # base = chord[0]
    # new_base = ((point + 7) - base) % 12
    # if len(chord) > 1:
    #     rel_from_base = [(n - base) for n in chord[1:]]
    #     inv_rel = [(-rel) % 12 for rel in rel_from_base]
    #     neg_chord = [new_base] + list(map(lambda x: (x + new_base) % 12, inv_rel))
    # else:
    #     neg_chord = [new_base]
    return neg_chord


def negative_harmony(note_array_or_note_array, point=0):
    """Create Negative Harmony in the JacobColierian way."""
    if isinstance(note_array_or_note_array, np.ndarray):
        na = copy.copy(note_array)
        has_part = False
    else:
        part = copy.copy(note_array_or_note_array)
        na = part.note_array()
        has_part = True
    for onset in np.unique(na["onset_beat"]):
        plist = na[np.where(na["onset_beat"] == onset)]["pitch"]
        pm = list(map(lambda y: (y % 12, int(y / 12)), plist))
        pc, mapping = zip(*pm)
        new_pc = reflect(chord=pc, base_point=point, system=[3, 4, 5])
        new_pitches = [a + b * 12 for a, b in zip(new_pc, mapping)]
        for i, index in enumerate(np.where(na["onset_beat"] == onset)[0]):
            na["pitch"][index] = new_pitches[i]
    if has_part:
        for note in part.notes:
            n = na[na["id"] == note.id]
            mpitch = n["pitch"].item()
            note.midi_pitch = mpitch
            note_spelling = pt.utils.music.midi_pitch_to_pitch_spelling(mpitch)
            note.step, note.alter, note.octave = note_spelling
        return part
    else:
        return na






if __name__ == "__main__":
    import partitura
    import os

    sfn = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Exercise_01.musicxml")
    part = partitura.load_musicxml(sfn)
    part = partitura.load_musicxml(partitura.EXAMPLE_MUSICXML)
    note_array = partitura.utils.ensure_notearray(part)
    print(note_array["pitch"])
    print(negative_harmony(note_array)["pitch"])

