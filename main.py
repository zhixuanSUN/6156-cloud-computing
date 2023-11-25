from fastapi import FastAPI, Response, HTTPException, Request

# I like to launch directly and not use the standard FastAPI startup
import uvicorn
import psycopg2


app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello Don, I'm Zhixuan Sun, UNI: zs2572"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Awesome cloud developer dff9 says Hello {name}"}


@app.get("/hello_text/{name}")
async def say_hello_text(name: str):
    the_message = f"Awesome cloud developer dff9 says Hello {name}"
    rsp = Response(content=the_message, media_type="text/plain")
    return rsp


endpoint = "database-1.ctxkoq8uo7wh.us-east-1.rds.amazonaws.com"
port = "5432"
username = "postgres"
password = "12345678"
database = "postgres"


@app.get("/get")
async def lookup():
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM buyer")
    results = cur.fetchall()
    for row in results:
        print(row)
    cur.close()
    conn.close()
    return results


@app.post("/post")
async def add(buyer_id: int, buyer_name: str, buyer_password: str):
    if not all([buyer_id, buyer_name, buyer_password]):
        raise HTTPException(status_code=400, detail="Incomplete data provided")
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()

    select_query = "SELECT * FROM buyer WHERE buyer_id = %s"
    cur.execute(select_query, (buyer_id,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Data with the same buyer_id already exists")

    cur.execute("INSERT INTO buyer (buyer_id, buyer_name, buyer_password) VALUES (%s, %s, %s)",
                (buyer_id, buyer_name, buyer_password))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "message": "Data inserted successfully"}


@app.delete("/delete")
async def delete_buyer(buyer_id: str):
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    delete_query = "DELETE FROM buyer WHERE buyer_id = %s"
    cur.execute(delete_query, buyer_id)

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Buyer not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "success", "message": f"Buyer with ID {buyer_id} deleted"}


@app.put("/put")
async def update_password(buyer_id: int, new_password: str):

    if not new_password:
        raise HTTPException(status_code=400, detail="New password is required")

    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()

    select_query = "SELECT * FROM buyer WHERE buyer_id = %s"
    cur.execute(select_query, (buyer_id,))

    existing_data = cur.fetchone()
    if not existing_data:
        raise HTTPException(status_code=404, detail="Buyer not found")

    update_query = "UPDATE buyer SET buyer_password = %s WHERE buyer_id = %s"
    cur.execute(update_query, (new_password, buyer_id))
    conn.commit()

    cur.close()
    conn.close()

    return {"status": "success", "message": f"Password updated for buyer with ID {buyer_id}"}


if __name__ == "__main__":
    uvicorn.run(app, host="54.89.190.246", port=8080)
