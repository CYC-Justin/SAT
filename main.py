from optparse import Values
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn  # 注意：虽然你说不要用 uvicorn，但这不启动外部命令行，而是内部调用
import psycopg2 as pg
from fastapi.staticfiles import StaticFiles
from psycopg2.extras import RealDictCursor
from typing import Optional

conn = pg.connect(host = '192.168.0.20', port='5432', dbname='testDB', user = 'postgres',password = '50984878')
cursor = conn.cursor(cursor_factory=RealDictCursor)


def get_records(id: Optional[str] = None, name: Optional[str] = None):
    if id and name:
        # 精确搜索：同时匹配 id 和 name
        cursor.execute("SELECT * FROM justin.todolist WHERE id = %s AND name = %s", (id, name))
    elif id:
        # 只搜索 id
        cursor.execute("SELECT * FROM justin.todolist WHERE id = %s", (id,))
    elif name:
        # 只搜索 name
        cursor.execute("SELECT * FROM justin.todolist WHERE name ILIKE %s", (f"%{name}%",))
    else:
        # 没有搜索条件，返回所有记录
        cursor.execute("SELECT * FROM justin.todolist")
    records = cursor.fetchall()
    return records

# def search_records(id: Optional[str] = None, name: Optional[str] = None):
#     if id and name:
#         # 精确搜索：同时匹配 id 和 name
#         cursor.execute("SELECT * FROM justin.todolist WHERE id = %s AND name = %s", (id, name))
#     elif id:
#         # 只搜索 id
#         cursor.execute("SELECT * FROM justin.todolist WHERE id = %s", (id,))
#     elif name:
#         # 只搜索 name
#         cursor.execute("SELECT * FROM justin.todolist WHERE name = %s", (name,))
#     else:
#         # 没有搜索条件，返回所有记录
#         cursor.execute("SELECT * FROM justin.todolist")
    
#     records = cursor.fetchall()
#     return records

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




# def main():
#     while True:
#         Userinput = input('请选择 1(显示), 2(添加), 3(删除), 4(退出):')
#         if Userinput == '1':
#             records = get_records()
#             print(records)
#         elif Userinput == '2':
#             add()
#         elif Userinput == '3':
#             delete()
#         elif Userinput == '4':
#             break
#     cursor.close()
#     conn.close()


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

class update_list(BaseModel):
    id: str
    name: str

class search_list(BaseModel):
    id: str
    name: str

# GET 路由 - 支持可选的搜索参数
@app.get("/get/")
async def read_root(id: Optional[str] = Query(None, description="搜索的ID"), 
                   name: Optional[str] = Query(None, description="搜索的名称")):
    if id or name:
        # 有搜索参数，执行搜索
        records = get_records(id, name)
        if len(records) == 0:
            return {"message": "查询失败", "error": "没有找到匹配的记录", "records": [], "count": 0}
        else:
            return {"message": "查询成功", "records": records, "count": len(records)}
    else:
        # 没有搜索参数，返回所有记录
        records = get_records()
        return {"message": "获取所有记录", "records": records, "count": len(records)}




# @app.post("/search/")
# async def search_value(value: search_list):
#     cursor.execute("SELECT * FROM justin.todolist WHERE id = %s AND name = %s", (value.id, value.name))
#     records = cursor.fetchall()
    
#     if len(records) == 0:
#         return {"message": "查询失败", "error": f"ID '{value.id}' 和 name '{value.name}' 的记录不存在", "id": value.id, "name": value.name}
#     else:
#         return {"message": "查询成功", "records": records, "count": len(records)}

# POST 路由


@app.post("/add/")
async def add_value(value: add_list):
    cursor.execute("INSERT INTO justin.todolist(id, name) VALUES (%s, %s)", (value.id, value.name))
    conn.commit()
    return {"message": "添加成功", "id": value.id, "name": value.name}

@app.post("/delete/")
async def delete_value(value: delete_list):
    cursor.execute("DELETE FROM justin.todolist WHERE id = %s AND name = %s", (value.id, value.name))
    conn.commit()
    return {"message": "删除成功", "id": value.id, "name": value.name}

@app.post("/update/")
async def update_value(value: update_list):
    # 当前逻辑：根据 ID 更新 name
    # 如果你需要同时更新 ID 和 name，可以使用下面的 SQL：
    # cursor.execute("UPDATE justin.todolist SET id = %s, name = %s WHERE id = %s", (value.id, value.name, value.id))
    
    cursor.execute("UPDATE justin.todolist SET name = %s WHERE id = %s", (value.name, value.id))
    conn.commit()
    
    # 检查是否有记录被更新
    if cursor.rowcount == 0:
        return {"message": "更新失败", "error": f"ID '{value.id}' 不存在", "id": value.id}
    else:
        return {"message": "更新成功", "id": value.id, "name": value.name}




# 挂载静态文件目录，将根路径 "/" 映射到 static 文件夹，html=True 表示支持 HTML 文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 内部调用 uvicorn 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # endpoint
