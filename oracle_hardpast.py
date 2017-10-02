#_*_ encoding:utf-8 _*_
from __future__ import division,print_function

import os
import logging
import shutil
import sys

"""
确保oracle 软件的安装路径和所建立数据库名称(db_name)与要拷贝的数据库名称一致,
并且在关闭状态.
"""

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


def pase_file(dest_folder, logger):
    
    f = open(os.path.join(dest_folder,'db_files.txt'))
    files = [line.strip() for line in f.readlines()]
    cnts = len(files)
    for idx,file in enumerate(files):
        printProgressBar(idx, cnts, suffix='已完成') 
        file_dir = os.path.dirname(file)
        file_name = os.path.basename(file)
        sour_file = os.path.join(dest_folder,file_name)
        if not os.path.exists(file_dir):
        	os.makedirs(file_dir)

        if not os.path.exists(sour_file):
        	logger.debug(file_name, 'no exists')
        else:
        	shutil.copy(sour_file, file_dir)
if __name__ == '__main__':
    
    logger = logging.Logger(__name__)
    fh = logging.FileHandler(os.path.splitext(__file__)[0]+'.log')
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    while 1:
        sour_folder = input('请输入要存储数据库文件的文件夹(当前文件夹按<ENTER>),退出按q: ')
        if sour_folder == "":
            sour_folder = os.path.dirname(__file__)
            break
        elif sour_folder == 'q':
            sys.exit(1)        
        else:
            if not os.path.exists(sour_folder):
                continue
            else:
                break
    
    pase_file(sour_folder, logger)
