#-*- coding: utf-8 -*-
import zipfile
import os
import sys
import struct
import imghdr
import shutil
#import pillow
from PIL import Image

def unzip(source_file, dest_path) :
    with zipfile.ZipFile(source_file, 'r') as zf :
        zf.extractall(path=dest_path)
        zf.close()

def zip(src_path, dest_file) :
    with zipfile.ZipFile(dest_file, 'w') as zf :
        rootpath = src_path
        for (path, dir, files) in os.walk(src_path) :
            for file in files :
                fullpath = os.path.join(path, file)
                relpath = os.path.relpath(fullpath, rootpath)
                zf.write(fullpath, relpath, zipfile.ZIP_DEFLATED)

def get_image_size(fname) :
    with open(fname, 'rb') as fhandle :
        head = fhandle.read(24)
        if len(head) != 24 :
            return
        what = imghdr.what(None, head)
        if what == 'png' :
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a :
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif what == 'gif' :
            width, height = struct.unpack('<HH', head[6:10])
        elif what == 'jpeg' :
            try :
                fhandle.seek(0)
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc) :
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff :
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                fhandle.seek(1, 1)
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception :
                return
        else :
            return
            
        return width, height

def remove_all(path) :
    shutil.rmtree(path)

def img_process(zipfile, imgpath, destdir, isForward = True) :
    if not os.path.isdir(destdir) :
        os.mkdir(destdir)
        
    #print(zipfile)   
    cropdir = './temp/crop'
    if not os.path.isdir(cropdir) :
        os.mkdir(cropdir)
    zipbasefile = os.path.basename(zipfile)
    cropdir = cropdir + '/' + zipbasefile
    #print(cropdir)
    if not os.path.isdir(cropdir) :
        os.mkdir(cropdir)
    
    imgpath = imgpath + zipbasefile
    
    for (path, dir, files) in os.walk(imgpath) :
        if path != imgpath :
            break
        for file in files :
            fullpath = os.path.join(path, file)
            filename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1].lower()
            if ext not in ('.png', '.jpg', '.jpeg', '.gif') :
                #file = file.encode('cp949', 'ignore')
                #print(u"%s file is not image." % file)
                continue
            #print(fullpath)
            #width, height = get_image_size(fullpath)
            img = Image.open(fullpath)
            width = img.size[0]
            height = img.size[1]
            #print(width)
            if width > height :
                #print(u'split image : %s' % file)
                lhs = '_01'
                rhs = '_02'
                if isForward == False :
                    lhs = '_02'
                    rhs = '_01'
                #img = Image.open(fullpath)
                halfwidth = width / 2
                left_img = img.crop((0, 0, halfwidth, height))
                right_img = img.crop((halfwidth, 0, width, height))
                left_filename = filename + lhs + ext
                right_filename = filename + rhs + ext
                left_img.save(os.path.join(cropdir, left_filename))
                right_img.save(os.path.join(cropdir, right_filename))
            else :
                #print(u'copy file : %s' % file)
                shutil.copy(fullpath, cropdir)
                
    # zip
    outfile = os.path.basename(zipfile) + '.zip'
    zip(cropdir, os.path.join(destdir, outfile))
    
def isZipFile(filename) :
    ext = os.path.splitext(filename)[1]
    if ext != '.zip' :
        print(u'%s file is not zip file.' % filename)
        return False
    return True

def main(src, dest, isForward = True) :
    isfile = os.path.isfile(src)
    if isfile == False :
        if os.path.exists(src) == False :
            print(u'wrong parameter. (%s)' % src)
            return
            
    tempdir = './temp'
    unzipdir = tempdir + '/unzip/'
    
    if isfile :
        if isZipFile(src) :
            unzip(src, unzipdir)
            img_process(src, unzipdir, dest, isForward)
    else :
        for (path, dir, files) in os.walk(src) :
            for file in files :
                if isZipFile(file) == False :
                    continue
                print('Unzip file... %s' % file)
                fullpath = os.path.join(path, file)
                unzip(fullpath, unzipdir + os.path.splitext(file)[0])
                #img_process(fullpath, tempdir, dest, isForward)
        for dir in os.listdir(unzipdir) :
            fulldir = os.path.join(unzipdir, dir)
            print('Processing file... %s' % dir)
            img_process(fulldir, unzipdir, dest, isForward)
                
    remove_all(tempdir)
                
def useage() :
    print(u"python split_image.py [origin] [dest] [direction]\n")
    print(u"\t[origin]\tzipfile or directory.")
    print(u"\t[dest]\t\toutput directory.")
    print(u"\t[direction]\tRead direction.")
    print(u"\t\t\tLeft to right is 'R'")
    print(u"\t\t\tRight to left is 'L'")

if __name__ == "__main__" :
    if len(sys.argv) < 4 :
        print(u"Wrong useage.\n")
        useage()
    else :
        origin = sys.argv[1]
        dest = sys.argv[2]
        isForward = True
        if sys.argv[3] is 'L' or 'l' :
            isForward = False
            main(origin, dest, isForward)
        elif sys.argv[3] is 'R' or 'r' :
            isForward = True
            main(origin, dest, isForward)
        else :
            print(u"Wrong useage.\n")
            useage()
            
       