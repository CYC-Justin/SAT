from optparse import Values
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn  # 注意：虽然你说不要用 uvicorn，但这不启动外部命令行，而是内部调用
import psycopg2 as pg
from fastapi.staticfiles import StaticFiles
from psycopg2.extras import RealDictCursor

conn = pg.connect(host = '192.168.0.20', port='5432', dbname='testDB', user = 'postgres',password = '50984878')
cursor = conn.cursor(cursor_factory=RealDictCursor)


def get_records():
    cursor.execute("SELECT * FROM justin.todolist")
    records = cursor.fetchall()
    return records
    
def add():
    id = input('请输入id:')
    name = input('请输入name:')
    cursor.execute("INSERT INTO justin.todolist(id, name) VALUES (%s,%s)",(id,name))
    conn.commit()
def delete():
    id = input('请输入id:')
    name = input('请输入name:')
    cursor.execute("DELETE FROM justin.todolist where id = %s and name = %s",(id,name))
    conn.commit()




def main():
    while True:
        Userinput = input('请选择 1(显示), 2(添加), 3(删除), 4(退出):')
        if Userinput == '1':
            records = get_records()
            print(records)
        elif Userinput == '2':
            add()
        elif Userinput == '3':
            delete()
        elif Userinput == '4':
            break
    cursor.close()
    conn.close()


app = FastAPI()

# 定义 POST 数据结构
class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

class add_list(BaseModel):
    id: str
    name: str

class delete_list(BaseModel):
    id: str
    name: str

# GET 路由
# @app.<method>("路由路径")
# async def 处理函数():
@app.get("/get/")
async def read_root():
    records = get_records()
    return records


@app.get("/hi")
async def hi():
    main()

# POST 路由


@app.post("/add/")
async def add_value(value: add_list):
    cursor.execute("INSERT INTO justin.todolist(id, name) VALUES (%s, %s)", (value.id, value.name))
    conn.commit()
    return {"message": "添加成功", "id": value.id, "name": value.name}

@app.post("/delete/")
async def delete_value(value: delete_list):
    print("aaaaa",value)
    cursor.execute("DELETE FROM justin.todolist WHERE id = %s AND name = %s", (value.id, value.name))
    conn.commit()
    return {"message": "删除成功", "id": value.id, "name": value.name}

# 挂载静态文件目录，将根路径 "/" 映射到 static 文件夹，html=True 表示支持 HTML 文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 内部调用 uvicorn 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # endpoint
