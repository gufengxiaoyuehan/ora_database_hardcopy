#_*_ encoding:utf-8 _*_

from __future__ import division,print_function
import os
import logging
import shutil
import cx_Oracle as ora 
import sys



# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█'):
    """
    get this function from stackoverflow.
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


def find_files(conn_info, dest_folder):
    try:
        try:
            cnx =  ora.connect(conn_info, mode=ora.SYSDBA)
        except ora.DatabaseError as e:
            error, = e.args    
            # if not opened
            if error.code == 1034:
                cnx = ora.connect(conn_info, mode=ora.SYSDBA|ora.PRELIM_AUTH)
                cnx.startup()
                cnx = ora.connect(mode=ora.SYSDBA)
                cur = cnx.cursor()
                cur.execute('alter database mount')
                cur.execute('alter database open')
                cur.close()
            else:
                print(sys.exc_info())
                input('按任意键结束')
                sys.exit(1)

        cur = cnx.cursor()
        
        # retrive log files
        cur.execute("select member from v$logfile")
        logs = [member[0] for member in cur.fetchall()]

        # retrive datafile
        cur.execute('select name from v$datafile')
        datafiles = [name[0] for name in cur.fetchall()]

        # retrive control file
        cur.execute('select name from v$controlfile')
        controlfiles = [name[0] for name in cur.fetchall()]

        # retrive tempfile
        cur.execute('select name from v$tempfile')
        tempfiles = [name[0] for name in cur.fetchall()]

        # spfile 
        cur.execute("select value from v$parameter where name = 'spfile' or name ='pfile'")
        spfiles = [name[0] for name in cur.fetchall()]

        assert len(logs) >=2, 'log 文件未找到'
        assert len(datafiles) >= 1, 'datafile 文件为找到'
        assert len(controlfiles) >= 2,  'controlfiles 文件为找到'
        
        files = logs + datafiles + controlfiles + tempfiles + spfiles

        with open(os.path.join(dest_folder,'db_files.txt'), 'w') as f:
            for file in files:
                f.write(file+'\n')
        print("正在关闭数据库")
        cnx.shutdown(mode=ora.DBSHUTDOWN_IMMEDIATE)
        cur = cnx.cursor()
        cur.execute("alter database close normal")
        cur.execute("alter database dismount")
        cnx.shutdown(mode = ora.DBSHUTDOWN_FINAL)
        print("数据库已关闭")

        return files
    except ora.DatabaseError as e:
        error, = e.args
        print(e.message)
        input('按任意键结束')
        sys.exit(1)

def copy_file(copyfiles, dest_folder, logger):
    cnts = len(copyfiles)
    for idx, file in enumerate(copyfiles):
        printProgressBar(idx, cnts, suffix='已完成') 
        if not os.path.exists(file):
            print("%s not exists" %file)
            logger.error("%s not exists" %file)
            continue
        else:
            file_name = os.path.basename(file)
            dest_file = os.path.join(dest_folder,file_name)
            shutil.copy(file, dest_file)

if __name__ == '__main__':
    
    logger = logging.Logger(__name__)
    fh = logging.FileHandler(os.path.splitext(__file__)[0]+'.log')
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    conn_info =  input("请输入管理员权限的账号和密码和tns, 如'users/pswd@tns'隔开: ")
    
    while 1:
        dest_folder = input('请输入要存储数据库文件的文件夹(当前文件夹按<ENTER>),退出按q: ')
        if dest_folder == "":
            dest_folder = os.path.dirname(__file__)
            break
        elif dest_folder == 'q':
           
            sys.exit(1)        
        else:
            if os.path.exists(dest_folder):
                print("%s 不存在" %dest_folder)
                continue
            else:
                if os.path.isdir(dest_folder):
                    break
                elif os.path.isfile(dest_folder):
                    print("输入的是文件名, 将使用文件所在路径")
                    dest_folder = os.path.dirname(dest_folder)
                    break
    files = find_files(conn_info,dest_folder)
    copy_file(files, dest_folder, logger)
