from operator import concat
from flask import Flask,render_template,request

app = Flask(__name__)

# functions
def caesar_dict_generator(start,end,shift):
    shift %= (end-start+1)
    return dict(zip([i for i in range(start,end+1)], [end+1-(start-(i+shift)) if i+shift<start else start-1+((i+shift)-end) if end<i+shift else i+shift for i in range(start,end+1)]))

def flag(num):
    return -1 if num%2==1 else 1

# Home(original generator)
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/index", methods=["post"])
def index_post():
    # request
    service_name = request.form["service_name"]
    birthdate = request.form["birthdate"]
    password_len = int(request.form["password_len"])
    initial = request.form["initial"]

    # preprocessing
    service_name_len = len(service_name)
    service_name_code = int.from_bytes(service_name.encode('utf-8'), 'big')
    birthdate_num = int(birthdate.replace('-', ''))
    initial_code = int.from_bytes(initial.encode('utf-8'), 'big')

    password_num = service_name_code*birthdate_num*initial_code

    sign_list = [58,59,60,61,62,63,64,91,92,93,94,95,96]
    password_list = ""#[(password_num + i*service_name_len*flag(i*service_name_len))%122 if ((password_num + i*service_name_len*flag(i*service_name_len))%122) >= 48 else ((password_num + i*service_name_len*flag(i*service_name_len))%122) + 48 for i in range(password_len)]
    password = "".join([chr((password_num + i*service_name_len*flag(i*service_name_len))%122) if ((password_num + i*service_name_len*flag(i*service_name_len))%122) >= 48 else chr((password_num + i*service_name_len*flag(i*service_name_len))%122 + 48) for i in range(password_len)])
    password =  "".join([chr(ord(pw)+7) if ord(pw) in sign_list else pw for pw in password])

    # caesar
    capital_shift_dict = caesar_dict_generator(65,90,service_name_len)
    noncapital_shift_dict = caesar_dict_generator(97,122,service_name_len)
    password = "".join([chr(capital_shift_dict[ord(pw)]) if 65<=ord(pw)<=90 else 
                chr(noncapital_shift_dict[ord(pw)]) if 97<=ord(pw)<=122 else 
                pw
                for pw in password])

    return render_template("index.html", password_len=password_len, service_name=service_name, birthdate=birthdate, initial=initial, password=password, password_list=password_list, copy_flag=True)


# caesar cipher
@app.route("/caesar")
def caesar():
    return render_template("caesar.html")

@app.route("/caesar", methods=["post"])
def caesar_post():
    sentence = request.form["sentence"]
    shift_direction = 1 if request.form["shift_direction"] == "right" else -1
    shift_len = int(request.form["shift_len"])
    shift = shift_direction * shift_len
    shift_direction = "右" if request.form["shift_direction"] == "right" else "左"

    number_shift_dict = caesar_dict_generator(48,57,shift) #48~57
    capital_shift_dict = caesar_dict_generator(65,90,shift) #65~90
    noncapital_shift_dict = caesar_dict_generator(97,122,shift) #97~122
    hiragana_shift_dict = caesar_dict_generator(12354,12435,shift) #12354~12435
    katakana_shift_dict = caesar_dict_generator(12450,12531,shift) #12450~12531

    caesar = "".join([chr(number_shift_dict[ord(s)])if 48<=ord(s)<=57 else 
            chr(capital_shift_dict[ord(s)]) if 65<=ord(s)<=90 else 
            chr(noncapital_shift_dict[ord(s)]) if 97<=ord(s)<=122 else 
            chr(hiragana_shift_dict[ord(s)]) if 12354<=ord(s)<=12435 else 
            chr(katakana_shift_dict[ord(s)])
            for s in sentence])

    return render_template("caesar.html", shift_direction=shift_direction, shift_len=shift_len, sentence=sentence, caesar=caesar, copy_flag=True)


# vigenere cipher
@app.route("/vigenere")
def vigenere():
    return render_template("vigenere.html")

@app.route("/vigenere", methods=["post"])
def vigenere_post():
    is_ed = int(request.form["is_ed"])
    key = request.form["key"]
    sentence = request.form["sentence"]

    key_index = 0
    vigenere = ""
    for s in sentence:
        if key_index == len(key): key_index = 0
        start,end = (48,57) if 48<=ord(s)<=57 else (65,90) if 65<=ord(s)<=90 else (97,122) if 97<=ord(s)<=122 else (12354,12435) if 12354<=ord(s)<=12435 else (12450,12531)
        key_start = 48 if 48<=ord(key[key_index])<=57 else 65 if 65<=ord(key[key_index])<=90 else 97 if 97<=ord(key[key_index])<=122 else 12354 if 12354<=ord(key[key_index])<=12435 else 12450
        vigenere_dict = caesar_dict_generator(start,end,flag(is_ed)*(ord(key[key_index])-key_start))
        vigenere += chr(vigenere_dict[ord(s)])
        print(ord(key[key_index]))
        key_index += 1

    is_ed = "暗号化" if is_ed == 0 else "復号化"

    return render_template("vigenere.html", is_ed=is_ed, key=key, sentence=sentence, vigenere=vigenere, copy_flag=True)


# radix transformation
@app.route("/radix")
def radix():
    return render_template("radix.html")

@app.route("/radix", methods=["post"])
def radix_post():
    number = request.form["number"]
    before_radix = int(request.form["before_radix"])
    after_radix = int(request.form["after_radix"])
    num_str_dict = dict(zip([i for i in range(0,37)], [str(i) for i in range(0,10)]+[chr(i) for i in range(65,91)]))

    def MtoN(m,num,n):
        # m == n
        if m == n: return num

        # m -> 10
        m10 = int(num, m)

        # 10 -> n
        n10 = ""
        i = 0
        while m10 > 0:
            r = m10%n
            n10 += str(num_str_dict[r])
            m10 = m10//n
            i += 1

        return n10[::-1]

    radix = MtoN(before_radix, number, after_radix)

    return render_template("radix.html",number=number, before_radix=before_radix, after_radix=after_radix, radix=radix, copy_flag=True)


if __name__ == "__main__":
    app.run(debug=True)