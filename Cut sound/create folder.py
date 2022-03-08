import os 

alphabet = ['a', 'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', "'", ' ', 'backspace']

for i in alphabet: 
    try:
        os.makedirs('./Test/' + i)
    except:
        print(i + ' Already exist donc tg')