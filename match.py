# encoding: utf-8
import io
import re

"""
'**EMAIL', '**DATE',
'**PHONE', '**AGE', '**INSTITUTION',
'**PLACE', '**NAME',
'**WEB - LOC', '**DEVICE - ID',
'**STREET - ADDRESS', '**ZIP - CODE',
'**ID - NUM', '**ACCESSION - NUMBER']
"""
map_de_ident = {
    '**EMAIL': 'EMAIL',
    '**DATE': 'DATE',
    '**PHONE': 'PHONE',
    '**AGE': 'AGE',
    '**INSTITUTION': 'INSTITUTE',
    '**PLACE': 'CITY',
    '**NAME': 'NAME',
    '**WEB-LOC': 'URL',
    '**DEVICE-ID': 'ID',
    '**STREET-ADDRESS': 'STREET',
    '**ZIP-CODE': 'ZIP',
    '**ID-NUM': 'ID',
    '**ACCESSION-NUMBER': 'ID'
}

match_normal = [
    'EMAIL',
    'PHONE',
    'INSTITUTION',
    'PLACE',
]
match_first = [
    'WEB',
    'DEVICE',
    'STREET',
    'ZIP',
    'ID',
    'ACCESSION'
]
match_second = {
    'WEB': 'LOC',
    'DEVICE': 'ID',
    'STREET': 'ADDRESS',
    'ZIP': 'CODE',
    'ID': 'NUM',
    'ACCESSION': 'NUMBER'
}
with_Bracket = [
    'DATE',
    'NAME',
    'AGE',
]


with io.open("deid.bio", "r", encoding="utf-8") as f:
    token_standard = []
    token_type_standard = []
    for line in f.read().split("\n"):
        if len(line) > 0:
            info = line.split(' ')
            token_standard.append(info[0])
            token_type_standard.append([info[1]])


with io.open("deid.txt", "r", encoding="utf-8") as f_deiden:
    token_de_iden = []
    token_type_de_iden = []
    for line in f_deiden.read().split("\n"):
        if len(line) > 0:
            info = line.split(' ')
            token_de_iden.append(info[0])
            token_type_de_iden.append(info[1])

# print(standard[:5])
# print(de_iden[:5])


def is_de_ident_and_deident_str(de_iden, j):
    if de_iden[j + 1] == '*':  # **
        #judge_lstr = ''.join(de_iden[j:j + 8])
        # print(de_iden[j + 2])
        # print(de_iden[j + 3])
        # print(de_iden[j + 4])
        # print('==========')

        if de_iden[j + 2] in with_Bracket:  # DATE, AGE, NAME
            judge_lstr = ''.join(de_iden[j:j + de_iden[j:].index(']') + 1])
            # print(judge_lstr)
            match_de_ident = re.match("\*\*[A-Z]{1,20}\[[A-Za-z,0-9 ]*\]", judge_lstr)
            if match_de_ident == None:
                return None, False, None
            else:
                match_de_ident_span = match_de_ident.span()
                judge_lstr = judge_lstr[match_de_ident_span[0]:match_de_ident_span[1]]
                judge_lstr = judge_lstr[2:judge_lstr.index('[')]
                return judge_lstr, True, ']'
        else:
            if de_iden[j + 2] in match_first:  # WEB, DEVICE, STREET, ZIP, ID, ACCESSION
                if de_iden[j + 3] == '-':  # -
                    if de_iden[j + 4] == match_second[de_iden[j + 2]]:
                        judge_lstr = ''.join(de_iden[j:j + 5])
                        # print(judge_lstr)
                        match_de_ident = re.match("\*\*[A-Z]{1,20}", judge_lstr)
                        #print("match_first: " + judge_lstr + ", " + str(match_de_ident))
                        if match_de_ident == None:
                            return None, False, None
                        else:
                            match_de_ident_span = match_de_ident.span()
                            judge_lstr = judge_lstr[match_de_ident_span[0]:match_de_ident_span[1]][2:]
                            return judge_lstr, True, de_iden[j + 4]
                    else:
                        return None, False, None
                else:
                    return None, False, None
            elif de_iden[j + 2] in match_normal:  # EMAIL, PHONE, INSTITUTION, PLACE
                judge_lstr = ''.join(de_iden[j:j + 3])
                # print(judge_lstr)
                match_de_ident = re.match("\*\*[A-Z]{1,20}", judge_lstr)
                if match_de_ident == None:
                    return None, False, None
                else:
                    match_de_ident_span = match_de_ident.span()
                    judge_lstr = judge_lstr[match_de_ident_span[0]:match_de_ident_span[1]][2:]
                    return judge_lstr, True, de_iden[j + 2]
            else:
                return None, False, None
    else:
        return None, False, None


i = 0  # ptr of standard
j = 0  # ptr of de_iden

while j < len(token_de_iden):  # and i < len(token_standard) :
    token = token_de_iden[j]
    if token == '*':
        de_ident_str, is_de_ident_, de_ident_end_ = is_de_ident_and_deident_str(token_de_iden, j)
        if is_de_ident_:
            de_ident_end = token_de_iden[j:].index(de_ident_end_) + 1  # **DATE[hsadu]: => ':' ends (location)
            de_ident_end_next_token = token_de_iden[j:][de_ident_end]  # **DATE[hsadu]: => ':' ends
            #print("de_ident_end_next_token: " + de_ident_end_next_token)
            if de_ident_end_next_token == '*':
                de_ident_str, is_de_ident_, de_ident_end_ = is_de_ident_and_deident_str(token_de_iden, j + de_ident_end)
                if is_de_ident_:  # two de_ident next to each other
                    token_type_standard[i].append(token_type_standard[i][0])  # e.g. B-DATE
                    i = i + 1
                    while token_type_standard[i][0].split('-')[0] != 'B':  # while not next de_ident
                        token_type_standard[i].append(token_type_standard[i][0])  # e.g. I-DATE
                        i = i + 1
                j = j + de_ident_end

            else:
                standard_end = token_standard[i:].index(de_ident_end_next_token)  # find ':' in standard (location)
                # print(standard_end)
                token_type_standard[i].append('B-' + de_ident_str)
                # print(de_ident_end_next_token)
                # print(judge_lstr)
                for temp_i in range(1, standard_end):
                    token_type_standard[i + temp_i].append('I-' + de_ident_str)
                j = j + de_ident_end
                i = i + standard_end
            # while de_iden[j]
        else:
            # token_type_standard[i].append(token)
            token_type_standard[i].append('O')
            i = i + 1
            j = j + 1
            # print("hello")

    else:
        # token_type_standard[i].append(token)
        token_type_standard[i].append('O')
        i = i + 1
        j = j + 1


for t, tts in enumerate(token_type_standard):
    if tts[0] != tts[1]:
        print(token_standard[t] + ' ' + tts[0] + ' ' + tts[1])

# print(token_type_standard)

with io.open("processed_deid.txt", "w+", encoding="utf-8") as f_write:
    for t, tts in enumerate(token_type_standard):
        f_write.write(token_standard[t] + " " + tts[0] + " " + tts[1] + "\n")
