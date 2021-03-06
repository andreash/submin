# from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/325204
#
# Original license:
# * "THE BEER-WARE LICENSE" (Revision 42):
# * <phk@login.dknet.dk> wrote this file.  As long as you retain this notice you
# * can do whatever you want with this stuff. If we meet some day, and you think
# * this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp

from hashlib import md5
import random

def md5crypt(password, salt, magic='$1$'):
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    magic = magic.encode('utf-8')

    #  The password first, since that is what is most unknown
    #  Then our magic string
    #  Then the raw salt
    m = md5()
    m.update(password + magic + salt)

    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = md5(password + salt + password).digest()
    for i in range(0, len(password)):
        c = mixin[(i % 16):(i % 16)+1]
        m.update(c)

    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
        if i & 1:
            m.update('\x00'.encode('utf-8'))
        else:
            m.update(password[0:1])
        i >>= 1

    final = m.digest()

    # /* and now, just to make sure things don't run too fast */
    for i in range(1000):
        m2 = md5()
        if i & 1:
            m2.update(password)
        else:
            m2.update(final)

        if i % 3:
            m2.update(salt)

        if i % 7:
            m2.update(password)

        if i & 1:
            m2.update(final)
        else:
            m2.update(password)

        final = m2.digest()

    # This is the bit that uses to64() in the original code.
    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    rearranged = ''
    for a, b, c in ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = final[a] << 16 | final[b] << 8 | final[c]
        for i in range(4):
            rearranged += itoa64[v & 0x3f]; v >>= 6

    v = final[11]
    for i in range(2):
        rearranged += itoa64[v & 0x3f]; v >>= 6

    return magic.decode('utf-8') + salt.decode('utf-8') + '$' + rearranged 

# END original file

def makesalt():
	salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'

	salt = ''
	bla = random.Random()
	for i in range(8):
		salt += bla.choice(salts)

	return salt

