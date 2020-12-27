import pyodbc

delta = 0.75


def predict2(cursor, table, str):
    statement = "SELECT TOP 5 char3, prob, count, sum FROM trigrams.dbo." + table
    statement += " WHERE char12=? ORDER BY count DESC"
    cursor.execute(statement, str)
    for row in cursor:
        print(row)


def getp1(cursor, str):
    cursor.execute("SELECT prob FROM trigrams.dbo.p1 WHERE unigram=?", str)
    row = cursor.fetchone()
    return float(row[0])


def getp2(cursor, str):
    cursor.execute("SELECT prob FROM trigrams.dbo.p2 WHERE bigram=?", str)
    row = cursor.fetchone()
    if row:
        return float(row[0])

    cursor.execute("SELECT TOP 1 c1 FROM trigrams.dbo.job1 WHERE bigram LIKE ? ORDER BY bigram ASC", str[0] + "%")
    c1 = float(cursor.fetchone()[0])
    cursor.execute("SELECT TOP 1 d1 FROM trigrams.dbo.job3 WHERE bigram LIKE ? ORDER BY bigram ASC", str[0] + "%")
    d1 = float(cursor.fetchone()[0])
    cursor.execute("SELECT TOP 1 d2 FROM trigrams.dbo.job4 WHERE bigram LIKE ? ORDER BY bigram ASC", "%" + str[1])
    d2 = float(cursor.fetchone()[0])
    cursor.execute("SELECT TOP 1 dall FROM trigrams.dbo.job5 ORDER BY bigram ASC")
    dall = float(cursor.fetchone()[0])

    p2 = delta * d1 / c1 * d2 / dall
    return p2


def getp3(cursor, str):
    cursor.execute("SELECT prob FROM trigrams.dbo.p3 WHERE trigram=?", str)
    row = cursor.fetchone()
    if row:
        return float(row[0])

    p2 = getp2(cursor, str[0:2])
    cursor.execute("SELECT TOP 1 d12 FROM trigrams.dbo.job6 WHERE trigram LIKE ? ORDER BY trigram ASC", str[0:2] + "%")
    d12 = float(cursor.fetchone()[0])
    cursor.execute("SELECT TOP 1 c12 FROM trigrams.dbo.job2 WHERE trigram LIKE ? ORDER BY trigram ASC", str[0:2] + "%")
    c12 = float(cursor.fetchone()[0])

    p3 = delta * d12 / c12 * p2
    return p3


if __name__ == '__main__':
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-8C2EFT2;'
                          'Database=trigrams;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()

    print("请选择：\n1：语句概率计算\n2：中文输入预测\n0：退出")
    choice = int(input())

    while True:
        if choice == 1:
            str = input()
            a = [getp1(cursor, str[0:1])]
            if len(str) >= 2:
                a.append(getp2(cursor, str[0:2]))
            for i in range(2, len(str)):
                a.append(getp3(cursor, str[i-2:i+1]))
            res = 1.0
            for x in a:
                res *= x
            print(res)
        elif choice == 2:
            str = input()
            if len(str) >= 2:
                cursor.execute("SELECT TOP 1 trigram FROM trigrams.dbo.p3 WHERE trigram LIKE ? ORDER BY prob DESC", str[-2:] + "%")
                row = cursor.fetchone()
                trigram = row[0]
                print(trigram[2])
            elif len(str) == 1:
                cursor.execute("SELECT TOP 1 bigram FROM trigrams.dbo.p2 WHERE bigram LIKE ? ORDER BY prob DESC", str[-1:] + "%")
                row = cursor.fetchone()
                bigram = row[0]
                print(bigram[1])
        else:
            break


    conn.close()
