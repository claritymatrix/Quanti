import os





def read_dir(dir_path,op):


    locate = []

    table_count = 0

    for file in os.walk(dir_path):

        for table in file[2]:

            path = file[0] + '/' + table

            data = pd.read_csv(path,head=0,encoding="utf-8")



if __name__ == "__main__":


    dir_path = ""
    op = func()
    read_dir(dir_path,op)
