# encoding: utf-8
import io
import re
import time

"""
'**EMAIL', '**DATE',
'**PHONE', '**AGE', '**INSTITUTION',
'**PLACE', '**NAME',
'**WEB - LOC', '**DEVICE - ID',
'**STREET - ADDRESS', '**ZIP - CODE',
'**ID - NUM', '**ACCESSION - NUMBER']
"""
map_de_ident = {
    'EMAIL': 'EMAIL',
    'DATE': 'DATE',
    'PHONE': 'PHONE',
    'AGE': 'AGE',
    'INSTITUTION': 'INSTITUTE',
    'PLACE': 'CITY',
    'NAME': 'NAME',
    'WEB-LOC': 'URL',
    'DEVICE-ID': 'ID',
    'STREET-ADDRESS': 'STREET',
    'ZIP-CODE': 'ZIP',
    'ID-NUM': 'ID',
    'ACCESSION-NUMBER': 'ID'
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

file_answer = "conll2002_ans.txt"
file_res = "conll2002_res.txt"

with io.open(file_answer, "r", encoding="utf-8") as f:
    token_standard = []
    token_type_standard = []
    for line in f.read().split("\n"):
        if len(line) > 0:
            info = line.split(' ')
            token_standard.append(info[0])
            token_type_standard.append([info[1]])


with io.open(file_res, "r", encoding="utf-8") as f_deiden:
    token_de_iden = []
    token_type_de_iden = []
    for line in f_deiden.read().split("\n"):
        if len(line) > 0:
            info = line.split(' ')
            token_de_iden.append(info[0])
            token_type_de_iden.append(info[1])


def find_end_match(token_list, match_list):
    special_case = ['y', 'yr', 'yo', 'nd', '#']
    match_number = len(match_list)
    for i in range(len(token_list) - match_number + 1):
        is_match = True
        match_by_special = True
        for j, tl in enumerate(token_list[i:i + match_number]):
            if j == 0:
                if match_list[j] != tl:
                    if match_list[j] in special_case:
                        if not (tl.startswith(match_list[j]) or tl.endswith(match_list[j])):
                            is_match = False
                        else:
                            is_match = True
                            match_by_special = True
                            print(["Match by S/E:", match_list[j], tl])
                    else:
                        is_match = False

            else:
                if match_list[j] != '*':  # need to check is deident
                    if match_list[j] != tl:
                        if match_list[j] in special_case:
                            if not (tl.startswith(match_list[j]) or tl.endswith(match_list[j])):
                                is_match = False
                            else:
                                is_match = True
                                match_by_special = True
                                print(["Match by S/E:", match_list[j], tl])
                        else:
                            is_match = False

                else:
                    is_match = True
                    match_by_special = False

        if is_match:
            return i, match_by_special

    print([token_list[:30], match_list])
    raise Exception


def find_end_match_deident(token_list, match_list):
    match_number = len(match_list)
    for i in range(len(token_list) - match_number + 1):
        is_match = True
        if token_list[i: i + match_number] == match_list:
            return i

    raise Exception


def is_de_ident_and_deident_str(de_iden, j):
    # return 'PHONE', is_de_ident_or_not, position_of_last_token_of_de_ident
    # double_bracket = False
    if de_iden[j + 1] == '*' and de_iden[j + 2] == 'ACCESSION' and de_iden[j + 3] == '-' and de_iden[j + 4] == 'NUMBER':
        j_start = j
        j_find_bracket_end = 4
        while de_iden[j_start + j_find_bracket_end] != ']':
            j_find_bracket_end += 1

        judge_lstr = "".join(de_iden[j + 2:j + 5])
        return judge_lstr, True, j_find_bracket_end  # , double_bracket
    elif de_iden[j + 1] == '*' and de_iden[j + 2] == '*' and de_iden[j + 3] == 'PHONE':
        # ***PHONE
        return 'PHONE', True, 3  # , double_bracket
    elif de_iden[j + 1] == '*' and de_iden[j + 2] in match_first and de_iden[j + 3] == '-' and de_iden[j + 4] == match_second[de_iden[j + 2]]:
        # WEB, DEVICE, STREET, ZIP, ID, ACCESSION
        judge_lstr = "".join(de_iden[j + 2:j + 5])
        return judge_lstr, True, 4  # , double_bracket
    elif de_iden[j + 1] == '*' and de_iden[j + 2] in match_normal:
        # EMAIL, PHONE, INSTITUTION, PLACE
        return de_iden[j + 2], True, 2
    elif de_iden[j + 1] == '*' and de_iden[j + 2] in with_Bracket and de_iden[j + 3] == '[':
        j_start = j
        j_find_bracket_end = 4
        while de_iden[j_start + j_find_bracket_end] != ']':
            j_find_bracket_end += 1
        return de_iden[j + 2], True, j_find_bracket_end  # , double_bracket
    else:
        return None, False, None


i = 0  # ptr of standard
j = 0  # ptr of de_iden
standard_search_end_bond = 50  # prevent search too far

while j < len(token_de_iden) - 4:  # and i < len(token_standard) :
    token = token_de_iden[j]
    is_special_match = False
    if token == '*':
        # print(i)
        de_ident_str, is_de_ident_, de_ident_end_ = is_de_ident_and_deident_str(token_de_iden, j)
        if is_de_ident_:
            #is_double = True
            de_ident_start = [token_de_iden[j - 2], token_de_iden[j - 1]]
            answer_start = [token_standard[i - 2], token_standard[i - 1]]
            # if double_bracket:
            # find second bracket
            # first_bracket = token_de_iden[j:].index(de_ident_end_)
            # de_ident_end = token_de_iden[j+first_bracket : ].index(de_ident_end_) + 1 # **DATE[hsadu]]: => ':' ends (location)
            # de_ident_end_next_token = token_de_iden[j:][de_ident_end] # **DATE[hsadu]]: => ':' ends

            # else:
            # de_ident_end = token_de_iden[j:].index(de_ident_end_) + 1  # **DATE[hsadu]: => ':' ends (location)
            de_ident_end = de_ident_end_ + 1
            de_ident_end_next_token = token_de_iden[j:][de_ident_end]  # **DATE[hsadu]: => ':' ends
            de_ident_end_next_two_token = token_de_iden[j:][de_ident_end:de_ident_end + 2]
            #print(de_ident_end_next_token, de_ident_end_next_two_token)
            #print([de_ident_str, de_ident_end_next_token])

            if de_ident_end_next_token == '*':
                de_ident_str2, is_de_ident_, de_ident_end_ = is_de_ident_and_deident_str(token_de_iden, j + de_ident_end)
                if is_de_ident_:  # many de_ident next to each other
                    temp_j = j + de_ident_end

                    while is_de_ident_:
                        # print([de_ident_str2])
                        #de_ident_end = token_de_iden[temp_j:].index(de_ident_end_) + 1
                        de_ident_end = de_ident_end_ + 1
                        de_ident_end_next_token = token_de_iden[temp_j:][de_ident_end]
                        #print(de_ident_end_next_token, de_ident_end_next_two_token)
                        temp_j = temp_j + de_ident_end

                        if de_ident_end_next_token == '*':
                            de_ident_str2, is_de_ident_, de_ident_end_ = is_de_ident_and_deident_str(token_de_iden, temp_j)
                        elif de_ident_end_next_token != '*':
                            is_de_ident_ = False
                            j = temp_j
                            de_ident_end_next_two_token = token_de_iden[j:j + 2]

                    #print(["Many Deident end:", token_de_iden[j]])

                    # standard_end = token_standard[i:].index(de_ident_end_next_token)  # find ':' in standard (location)

                    try:
                        standard_end, is_special_match = find_end_match(token_standard[i:i + standard_search_end_bond], de_ident_end_next_two_token)
                    except:
                        print(i, j)
                        raise Exception

                    for temp_i in range(standard_end):
                        list_standard_token_type = token_type_standard[i + temp_i]
                        if list_standard_token_type[0] != 'O':
                            list_standard_token_type.append(list_standard_token_type[0])
                        else:
                            list_standard_token_type.append('B-never_match')
                    i = i + standard_end

                else:
                    # standard_end = token_standard[i:].index(de_ident_end_next_token)  # find ':' in standard (location)
                    try:
                        standard_end, is_special_match = find_end_match(token_standard[i:i + standard_search_end_bond], de_ident_end_next_two_token)
                    except:
                        print(i, j)
                        raise Exception

                    token_type_standard[i].append('B-' + map_de_ident[de_ident_str])
                    for temp_i in range(1, standard_end):
                        token_type_standard[i + temp_i].append('I-' + map_de_ident[de_ident_str])
                    j = j + de_ident_end
                    i = i + standard_end
            else:
                try:
                    standard_end, is_special_match = find_end_match(token_standard[i:i + standard_search_end_bond], de_ident_end_next_two_token)
                except:
                    print(i, j)
                    raise Exception

                token_type_standard[i].append('B-' + map_de_ident[de_ident_str])
                for temp_i in range(1, standard_end):
                    token_type_standard[i + temp_i].append('I-' + map_de_ident[de_ident_str])

                j = j + de_ident_end
                i = i + standard_end

            # print("========================")
        else:
            if len(token_type_standard[i]) == 1:
                token_type_standard[i].append('O')

            # token_type_standard[i].append('O')
            i = i + 1
            j = j + 1

    else:
        if len(token_type_standard[i]) == 1:
            token_type_standard[i].append('O')

        # token_type_standard[i].append('O')
        i = i + 1
        j = j + 1

for t, tts in enumerate(token_type_standard):
    if len(tts) > 2:
        print([t, token_standard[t], tts])


# # print(token_type_standard)

with io.open("processed_deid.txt", "w+", encoding="utf-8") as f_write:
    for t, tts in enumerate(token_type_standard):
        try:
            f_write.write(token_standard[t] + " " + tts[0] + " " + tts[1] + "\n")
        except:
            f_write.write(token_standard[t] + " " + tts[0] + "\n")
