# coding: utf-8

def Hex2List(h,n):
    """
    This function ...

    :param h: a hex number
    :param n: the length of the list
    :return: a list(like that ['xx', 'xx', ...])
    """
    s = hex(h)
    s1 = s[2:-1] if s[-1] == "L" else s[2:]
    str = s1.zfill(n*2)
    ret = [str[2*i:2*(i+1)] for i in range(n)]
    return ret

def byteconvert(v):
    ret = 0
    ret = ((v&0xFFFF00000000) >> 32) + ((v&0xFFFF) << 32) + (v&0xFFFF0000)
    return ret

def byteconvert1(v):
    ret = 0
    ret = ((v&0xFF0000000000) >> 40) +\
          ((v&0xFF00000000) >> 24) +\
          ((v&0xFF000000)>>8) +\
          ((v&0xFF0000)<<8) + \
          ((v&0xFF00)<<24)+\
          ((v&0xFF)<<40)
    return ret

def byteconvert2(v):
    ret = 0
    l = Hex2List(v,6)
    l1 = [0,0,0,0,0,0]
    l1[1] = l[5]
    l1[3] = l[4]
    l1[5] = l[3]
    l1[0] = l[2]
    l1[2] = l[1]
    l1[4] = l[0]
    s = '0x' + ''.join(l1)
    ret = int(s,16)
    return ret
